"""
 pricing-insights.py

 @ticket:	https://vampdash.atlassian.net/browse/DAS-11411
 @date:		2022-03-23
 @auth:		Daniel Stratti < daniels@vamp.me >

 @desc:
 This lambda function is triggered via scheduling to collect the campaign
 performance insights on all active campaigns

 Campaign Performance
 and send out an update weekly. The things to consider in this email are:

 - Calculated the expected statistics based off creator past performance

 - Calculated the expected statistics based off platform, region & category targeted:

 - Compare actual performance with quote & expected performance


 To progress, can we set up a weekly email, similar to the one I set up for profitability where we provide the campaign quote (Reach, Impressions, Engagements, Content) and:
The actual results achieved
The benchmark using our linear regression models and the creators actually selected
The benchmark based on the platform average in the category and region targeted
"""
import json
import logging
import math
import os

import pandas as pd
from createsend import Transactional
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

pd.options.display.float_format = "{:,.2f}".format


"""
This query contains all active campaigns, the quoted estimates & team details"""
CAMPAIGNS = """
	SELECT teams.name
		, users.email
		, camp.id AS campaign_id
		, camp.version
		, camp.started_on
		, camp.name AS campaign_name
		, camp.has_managed_service
		, camp.total_coins
		, camp.spent_coins
		, cc.product_coins_spent
		, cc.ad_coins_spent
		, camp.additional_coins

		-- Analyse content plan etc
		, camp.estimates
		, camp.estimates::json#>>'{cpe}' AS cpe
		, camp.estimates::json#>>'{cpm}' AS cpm
		, camp.estimates::json->'content' AS estimated_content
		, camp.estimates::json#>>'{contentPlan}' AS content_plan

		-- Analyse social stats
		, camp.estimates::json#>>'{engagement}' AS estimated_engagement
		, camp.estimates::json#>>'{impressions}' AS estimated_impressions
		, camp.estimates::json#>>'{reach}' AS estimated_reach
		, camp.estimates::json#>>'{socialAudience}' AS estimated_social_audience
		, camp.estimates::json#>>'{talent}' AS estimated_talent
	FROM campaigns camp
	JOIN teams ON teams.id = camp.team_id
	LEFT JOIN campaign_costs cc ON cc.campaign_id = camp.id
	JOIN campaign_statuses cs ON cs.id = camp.campaign_status_id
	LEFT JOIN memberships m ON m.team_id = teams.id
		AND m.user_id = teams.owner_id
	LEFT JOIN users ON users.id = m.id

	WHERE teams.name NOT IN (
			'Vamp', -- Confirm if should be included
			'Vamp Productions', -- Confirm if should be included
			'Vamp - hotmail', -- Confirm if should be included
			'Vamp Demo',
			'VampVision',
			'Shutterstock (Vamp)', -- Confirm if should be included
			'Vamp Creative', -- Confirm if should be included
			'Vamp Demo Whitelabel',
			'Marks Agency Vamp', -- Confirm if should be included
			'Vamp Japan', -- Confirm if should be included
			'Vamp Japan Test',
			'Vamp Test',
			'Vamp / Nestle', -- Confirm if should be included
			'JoTestProd',
			'Digital4ge',
			'Yourcompany',
			'Demo Team',
			'AnnaTestAB',
			'Anna Test Company Name',
			'Lee+test',
			'Annas Agency',
			'AnnaTestAB',
			'Demo Talent Management',
			'Aili TM Company'
		)
		AND teams.name IS NOT NULL
		AND (camp.desired_age_ranges<>'100-999' OR camp.desired_age_ranges IS NULL)
		AND cs.code = 'fulfilled'
		AND camp.start_date IS NOT NULL
		AND camp.updated_at >= CURRENT_DATE - INTERVAL '1 weeks'
	ORDER BY camp.start_date DESC;
"""

CAMPAIGN_CAT_REGION = """
	SELECT camp.id AS campaign_id
		, ARRAY_REMOVE(ARRAY_AGG(distinct(cat.code)), NULL) AS categories
		, ARRAY_REMOVE(ARRAY_AGG(distinct(c.region)), NULL) AS regions
	FROM campaigns camp
	JOIN teams ON teams.id = camp.team_id
	LEFT JOIN campaign_costs cc ON cc.campaign_id = camp.id
	JOIN campaign_statuses cs ON cs.id = camp.campaign_status_id
	LEFT JOIN memberships m ON m.team_id = teams.id
		AND m.user_id = teams.owner_id
	LEFT JOIN users ON users.id = m.id
	LEFT JOIN categories cat ON cat.code = ANY(STRING_TO_ARRAY(LOWER(camp.search_term), ',')::text[])
	LEFT JOIN countries c ON c.code = ANY(STRING_TO_ARRAY(camp.desired_location, ','))

	WHERE teams.name NOT IN (
			'Vamp', -- Confirm if should be included
			'Vamp Productions', -- Confirm if should be included
			'Vamp - hotmail', -- Confirm if should be included
			'Vamp Demo',
			'VampVision',
			'Shutterstock (Vamp)', -- Confirm if should be included
			'Vamp Creative', -- Confirm if should be included
			'Vamp Demo Whitelabel',
			'Marks Agency Vamp', -- Confirm if should be included
			'Vamp Japan', -- Confirm if should be included
			'Vamp Japan Test',
			'Vamp Test',
			'Vamp / Nestle', -- Confirm if should be included
			'JoTestProd',
			'Digital4ge',
			'Yourcompany',
			'Demo Team',
			'AnnaTestAB',
			'Anna Test Company Name',
			'Lee+test',
			'Annas Agency',
			'AnnaTestAB',
			'Demo Talent Management',
			'Aili TM Company'
		)
    	AND teams.name IS NOT NULL
		AND (camp.desired_age_ranges<>'100-999' OR camp.desired_age_ranges IS NULL)
		AND cs.code = 'fulfilled'
		AND camp.start_date IS NOT NULL
        AND camp.updated_at >= CURRENT_DATE - INTERVAL '1 weeks'
	GROUP BY 1;
"""


"""
This query collects all the deliverables selected for a campaign
"""
DELIVERABLES = """
	SELECT camp.id AS campaign_id
		, briefs.influencer_id
		, sp.code AS social_platform
		, (
		  CASE
			WHEN (sp.code IN ('youtube', 'instagram') AND sa.followers_count <= 10000)
				OR (sp.code = 'tiktok' AND sa.followers_count BETWEEN 10000 AND 100000)
				THEN 'nano'
			WHEN (sp.code IN ('youtube', 'instagram') AND sa.followers_count <= 25000)
				OR (sp.code = 'tiktok' AND sa.followers_count <= 200000)
				THEN 'micro'
			WHEN (sp.code IN ('youtube', 'instagram') AND sa.followers_count <= 50000)
				OR (sp.code = 'tiktok' AND sa.followers_count <= 500000)
				THEN 'mid'
			WHEN (sp.code IN ('youtube', 'instagram') AND sa.followers_count <= 100000)
				OR (sp.code = 'tiktok' AND sa.followers_count <= 1000000)
				THEN 'macro'
			WHEN (sp.code IN ('youtube', 'instagram') AND sa.followers_count > 100000)
				OR (sp.code = 'tiktok' AND sa.followers_count > 1000000)
				THEN 'mega'

			ELSE 'unknown'

		  END
		) AS band
		, sa.followers_count
		, sa.engagement_rate
		, ds.code as deliverable_status
		, CASE
			WHEN ds.code IN ('due_for_review', 'in_review', 'posting')
				THEN FALSE
			WHEN ds.code IN ('checking_social', 'media_matched', 'ready_for_invoice', 'processing_payment', 'paid', 'fulfilled')
				THEN TRUE
			ELSE FALSE
		END AS is_live
		, dt.code AS deliverable_type
		, d.id as deliverable_id
		, br.quantity
		, br.token_cost
		, br.custom_price
		, br.agency_price
		, br.agreed_price
		, d.reward_value
		, media.comments_count
		, media.likes_count
		, media.engagement_rate as media_engagement_rate

		, COALESCE(mi.impressions , (
			  SELECT mit.value
			  FROM media_insight_tags mit
			  JOIN insight_tags it ON it.id = mit.insight_tag_id
			  WHERE mit.media_id = media.id
			  AND it.code = 'view_count'
			)
		) AS impressions
		, mi.reach
		, COALESCE(mi.engagement , (
			  SELECT mit.value
			  FROM media_insight_tags mit
			  JOIN insight_tags it ON it.id = mit.insight_tag_id
			  WHERE mit.media_id = media.id
			  AND it.code = 'engagement_count'
			)
		) AS engagement
	FROM campaigns camp
	JOIN briefs ON briefs.campaign_id = camp.id
	JOIN brief_requirements br ON br.brief_id = briefs.id
	LEFT JOIN deliverables d ON d.brief_id = briefs.id
		AND d.deliverable_type_id = br.deliverable_type_id
	LEFT JOIN deliverable_types dt ON dt.id = d.deliverable_type_id
	LEFT JOIN deliverable_statuses ds ON ds.id = d.deliverable_status_id
	LEFT JOIN media ON media.brief_id = briefs.id
		AND media.deliverable_id = d.id
	LEFT JOIN media_insights mi ON mi.media_id = media.id
		AND mi.social_platform_id = dt.social_platform_id
	JOIN social_accounts sa ON sa.influencer_id = briefs.influencer_id
		AND sa.social_platform_id = dt.social_platform_id
	JOIN social_platforms sp ON sp.id = sa.social_platform_id
	JOIN teams ON teams.id = camp.team_id
	JOIN campaign_statuses cs ON cs.id = camp.campaign_status_id
	WHERE teams.name NOT IN (
			'Vamp', -- Confirm if should be included
			'Vamp Productions', -- Confirm if should be included
			'Vamp - hotmail', -- Confirm if should be included
			'Vamp Demo',
			'VampVision',
			'Shutterstock (Vamp)', -- Confirm if should be included
			'Vamp Creative', -- Confirm if should be included
			'Vamp Demo Whitelabel',
			'Marks Agency Vamp', -- Confirm if should be included
			'Vamp Japan', -- Confirm if should be included
			'Vamp Japan Test',
			'Vamp Test',
			'Vamp / Nestle', -- Confirm if should be included
			'JoTestProd',
			'Digital4ge',
			'Yourcompany',
			'Demo Team',
			'AnnaTestAB',
			'Anna Test Company Name',
			'Lee+test',
			'Annas Agency',
			'AnnaTestAB',
			'Demo Talent Management',
			'Aili TM Company'
		)
    	AND teams.name IS NOT NULL
		AND (camp.desired_age_ranges<>'100-999' OR camp.desired_age_ranges IS NULL)
		AND cs.code = 'fulfilled'
		AND camp.start_date IS NOT NULL
        AND camp.updated_at >= CURRENT_DATE - INTERVAL '1 weeks'
		AND br.quantity > 0
		AND dt.code NOT IN ('product_purchase', 'product_distribution');
"""


BENCH_MARK = """
	SELECT countries.region
		, sp.code AS social_platform
		, (
		  CASE
			WHEN (sp.code IN ('youtube', 'instagram') AND sa.followers_count <= 10000)
				OR (sp.code = 'tiktok' AND sa.followers_count BETWEEN 10000 AND 100000)
				THEN 'nano'
			WHEN (sp.code IN ('youtube', 'instagram') AND sa.followers_count <= 25000)
				OR (sp.code = 'tiktok' AND sa.followers_count <= 200000)
				THEN 'micro'
			WHEN (sp.code IN ('youtube', 'instagram') AND sa.followers_count <= 50000)
				OR (sp.code = 'tiktok' AND sa.followers_count <= 500000)
				THEN 'mid'
			WHEN (sp.code IN ('youtube', 'instagram') AND sa.followers_count <= 100000)
				OR (sp.code = 'tiktok' AND sa.followers_count <= 1000000)
				THEN 'macro'
			WHEN (sp.code IN ('youtube', 'instagram') AND sa.followers_count > 100000)
				OR (sp.code = 'tiktok' AND sa.followers_count > 1000000)
				THEN 'mega'

			ELSE 'unknown'

		  END
		) AS band
		, dt.code AS deliverable_type
		, cat.code AS category
		, AVG(COALESCE(mi.impressions , (
			  SELECT mit.value
			  FROM media_insight_tags mit
			  JOIN insight_tags it ON it.id = mit.insight_tag_id
			  WHERE mit.media_id = media.id
			  AND it.code = 'view_count'
			)
		)) AS impressions
		, AVG(mi.reach) AS reach
		, AVG(COALESCE(mi.engagement , (
			  SELECT mit.value
			  FROM media_insight_tags mit
			  JOIN insight_tags it ON it.id = mit.insight_tag_id
			  WHERE mit.media_id = media.id
			  AND it.code = 'engagement_count'
			)
		)) AS engagement
	FROM campaigns camp
	JOIN briefs ON briefs.campaign_id = camp.id
	JOIN brief_requirements br ON br.brief_id = briefs.id
	JOIN deliverables d ON d.brief_id = briefs.id
		AND d.deliverable_type_id = br.deliverable_type_id
	JOIN deliverable_types dt ON dt.id = d.deliverable_type_id
	JOIN deliverable_statuses ds ON ds.id = d.deliverable_status_id
	JOIN media ON media.brief_id = briefs.id
		AND media.deliverable_id = d.id
	LEFT JOIN media_insights mi ON mi.media_id = media.id
		AND mi.social_platform_id = dt.social_platform_id
	JOIN social_accounts sa ON sa.influencer_id = briefs.influencer_id
		AND sa.social_platform_id = dt.social_platform_id
	JOIN social_platforms sp ON sp.id = sa.social_platform_id
	JOIN influencers inf ON inf.id = sa.influencer_id
	JOIN countries ON countries.name = inf.country
	JOIN influencer_categories ic ON ic.influencer_id = inf.id
	JOIN categories cat ON cat.id = ic.category_id
	JOIN teams ON teams.id = camp.team_id
	JOIN campaign_statuses cs ON cs.id = camp.campaign_status_id
	WHERE teams.name NOT IN (
			'Vamp', -- Confirm if should be included
			'Vamp Productions', -- Confirm if should be included
			'Vamp - hotmail', -- Confirm if should be included
			'Vamp Demo',
			'VampVision',
			'Shutterstock (Vamp)', -- Confirm if should be included
			'Vamp Creative', -- Confirm if should be included
			'Vamp Demo Whitelabel',
			'Marks Agency Vamp', -- Confirm if should be included
			'Vamp Japan', -- Confirm if should be included
			'Vamp Japan Test',
			'Vamp Test',
			'Vamp / Nestle', -- Confirm if should be included
			'JoTestProd',
			'Digital4ge',
			'Yourcompany',
			'Demo Team',
			'AnnaTestAB',
			'Anna Test Company Name',
			'Lee+test',
			'Annas Agency',
			'AnnaTestAB',
			'Demo Talent Management',
			'Aili TM Company'
		)
    	AND teams.name IS NOT NULL
		AND (camp.desired_age_ranges<>'100-999' OR camp.desired_age_ranges IS NULL)
		AND cs.code IN ('fulfilled', 'paid')
		AND camp.end_date BETWEEN CURRENT_DATE - INTERVAL '1 years' AND CURRENT_DATE - INTERVAL '1 week'
		AND camp.start_date IS NOT NULL
		AND br.quantity > 0
		AND dt.code NOT IN ('product_purchase', 'product_distribution')
	GROUP BY 1, 2, 3, 4, 5;
"""


EXPECTED_COLS = ["impressions", "reach", "engagement"]

""" Generic structure for the performance statistics table rows """
performance_statistic = """
	<tr class='{css_class}' style='width: 100%;'>
			<td class='table-row' style='width: 2rem; height: 2rem;'>{icon}</td>
			<td style='text-align: left; width: 8rem'>{stat}</td>
			<td style='text-align: left; width: auto'>
				{value}
			</td>
	</tr>
"""

""" Generic structure for performance tables """
performance_sections = """
	<table role='presentation' style='width:100%;border-collapse:collapse;border:0;border-spacing:0;'>
		<tbody>
			{table_rows}
		</tbody>
	</table>
"""


# TODO: Make a donut graph of current stats to lower bound
# percentage_html = """
# <div align="center">
# 	<!--[if mso]>
#     <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="http://" style="height:100px;v-text-anchor:middle;width:100px;" arcsize="600%" stroke="f" fillcolor="#ff8080">
#     <w:anchorlock/>
#     	<center>
#         <![endif]-->
# 		<div align="center" style='position: relative; background-color:#f5f6f8; border-radius:50%;display:inline-block;font-family:sans-serif;font-size:0.5rem;font-weight:bold;text-align:center;text-decoration:none;width:100%;height:100%;-webkit-text-size-adjust:none;background-image: conic-gradient(#6c25ff {percentage}%, #f5f6f8 0);'>
# 			<div style="justify-content: center;align-items: center;position: absolute;top: 15%;left: 15%;background-color:#FFF;border-radius:50%;display:inline-block;font-family:sans-serif;font-size:0.5rem;font-weight:300;text-align:center;text-decoration:none;width:70%;height:70%;-webkit-text-size-adjust:none;text-align: center;vertical-align: middle"></div>
#         </div>
#         <!--[if mso]>
#         </center>
#     </v:roundrect>
#     <![endif]-->
# </div>
# """

""" Generic structure for the platform icon """
platform_icons = {
    "instagram": (
        '<img src="https://cdn2.iconfinder.com/data/icons/social-media-2285/512/1_Instagram_colored_svg_1-512.png"'
        ' alt="Instagram" width="24" style="height:auto;display:block;border:0;" />'
    ),
    "tiktok": (
        '<img src="https://www.edigitalagency.com.au/wp-content/uploads/TikTok-icon-glyph.png"'
        ' alt="Tiktok" width="24" style="height:auto;display:block;border:0;" />'
    ),
    "youtube": (
        '<img src="https://www.iconpacks.net/icons/2/free-youtube-logo-icon-2431-thumb.png"'
        ' alt="Youtube" width="24" style="height:auto;display:block;border:0;" />'
    ),
}


def set_connection_str() -> str:
    """Populate DB connection string"""
    host = os.getenv("HOST")
    password = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")
    user = os.getenv("DBUSER")
    port = os.getenv("PORT", "5432")

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def fetch_data(query) -> tuple:
    """Fetch query from db"""
    connect_str = set_connection_str()
    engine = create_engine(connect_str)

    return pd.io.sql.read_sql(query, engine)


def format_thousand(x: any) -> any:
    """Format numbers to have comma seperated thousands"""
    try:
        y = float(x)
        y = f"{y:,.0f}"
        return y
    except:
        return x


def campaign_plan(camp: pd.Series) -> pd.DataFrame:
    """
    Create a `squad` based on the content plan given during brief creation.
    This fake squad is used to create the benchmark comparisson if a campaign
    has yet to select their own squad.

    camp : pd.Series
            A single campaign represented as a dataframe row

    returns pd.DataFrame
            The fake squad based on the campaigns content plan
    """
    fake_squad = pd.DataFrame(columns=["social_platform", "band"])
    errors = 0

    if camp["content_plan"] is not None:
        content_plan = json.loads(camp["content_plan"])

        for key in content_plan.keys():
            ig_list = ["instagram"] * content_plan[key]["instagram"]
            tt_list = ["tiktok"] * content_plan[key]["tiktok"]
            yt_list = ["youtube"] * content_plan[key]["youtube"]

            if len(ig_list) > 0 or len(tt_list) > 0 or len(yt_list) > 0:
                fake_squad = pd.concat(
                    [
                        fake_squad,
                        pd.DataFrame(
                            {
                                "band": [key.lower()]
                                * (len(ig_list) + len(tt_list) + len(yt_list)),
                                "social_platform": [*ig_list, *tt_list, *yt_list],
                            }
                        ),
                    ]
                )
            else:
                errors = errors + 1

        if errors == len(content_plan.keys()):
            # default bench, one of each
            socials = ["instagram", "tiktok", "youtube"]

            for key in ["nano", "micro", "mid", "macro", "mega"]:
                fake_squad = pd.concat(
                    [
                        fake_squad,
                        pd.DataFrame(
                            {"band": [key] * len(socials), "social_platform": socials}
                        ),
                    ]
                )

    return fake_squad


def adjust_benchmarks(
    benchmark: pd.DataFrame, grp_cols: list, stat_cols=EXPECTED_COLS
) -> pd.DataFrame:
    """
    Due to a variety of reasons a campaign may not have a squad, desired region
    nor desired category. As such, the benchmark comparrison must be adjusted
    accordingly, based on various group columns, we want to find the average
    performance, then deflate it by 2 standard deviations of the set.

    benchmark: pd.DataFrame
            The data frame containing the benchmark performance of campaigns

    grp_cols: list
            A list of columns present in `benchmark` that will group them

    stat_cols: list
            The column names of the benchmark statistics
    """
    grp = (
        benchmark.groupby(grp_cols)
        .agg({col: ["mean", "std"] for col in stat_cols})
        .reset_index()
    )

    benchmark = grp.copy()

    for col in stat_cols:
        benchmark[(col, "")] = benchmark.loc[:, (col, "mean")].apply(
            lambda x: 0 if x < 0 else x
        )  # - (2 * benchmark.loc[:, (col, 'std')]).apply(lambda x: 0 if x < 0 else x)
        benchmark.drop(inplace=True, columns=[(col, "mean"), (col, "std")])
    benchmark.columns = benchmark.columns.droplevel(1)
    return benchmark


def format_benchmark(
    camp: pd.Series, results: pd.DataFrame, benchmark: pd.DataFrame
) -> dict:
    """
    Format the structure of the benchmark section into a readible dictionary
    ready for campaign monitor. The dictionary should contain the benchmark
    engagment, impressions & reach one could expect from the selected squad or
    content plan

    campaign : pd.Series
            A single campaign represented as a data frame row which is then
            formatted

    returns : dict
            The formatted benchmark section ready for campaign monitor
    """
    regions = camp["regions"]
    categories = camp["categories"]
    camp["campaign_id"]
    squad = results.query("campaign_id == @camp_id")
    stat_cols = EXPECTED_COLS
    bench_cols = ["region", "social_platform", "band", "category"]

    if len(squad) > 0:
        deliverables = squad
        bench_cols = [*bench_cols, "deliverable_type"]
    else:
        # get details from campaign
        deliverables = campaign_plan(camp)
        benchmark = adjust_benchmarks(benchmark=benchmark, grp_cols=bench_cols)

    # alter benchmarks to average regions when region not specified
    if len(regions) == 0 or regions[0] is None:
        regions = []
        bench_cols = [col for col in bench_cols if col != "region"]
        benchmark = adjust_benchmarks(benchmark=benchmark, grp_cols=bench_cols)

    # alter benchmarks to average categories when category not specified
    if len(categories) == 0 or categories[0] is None:
        categories = []
        bench_cols = [col for col in bench_cols if col != "category"]
        benchmark = adjust_benchmarks(benchmark=benchmark, grp_cols=bench_cols)

    # Create masks for applicable benchmarks, do here as benchmarks changes above
    mask = benchmark["social_platform"].isin(deliverables["social_platform"])

    if len(regions) > 0:
        mask = mask & benchmark["region"].isin(regions)

    if len(categories) > 0:
        mask = mask & benchmark["category"].isin(categories)

    merge_cols = (
        ["social_platform", "band", "deliverable_type"]
        if "deliverable_type" in benchmark.columns
        else ["social_platform", "band"]
    )
    deliverables = deliverables.loc[
        :, [col for col in deliverables.columns if col not in stat_cols]
    ]
    applicable = deliverables.merge(
        benchmark.loc[mask, :],
        how="left",
        left_on=merge_cols,
        right_on=merge_cols,
        suffixes=("_actual", ""),
    )

    # TODO: format ints
    bench = applicable.loc[:, stat_cols].sum().astype(int).to_dict()
    upper_b = 1.3
    lower_b = 0.7

    return {
        "categories": ", ".join(categories),
        "regions": ", ".join(regions),
        **{
            k: {
                "upperBound": int(bench[k] * upper_b),
                "lowerBound": int(bench[k] * lower_b),
            }
            for k in bench.keys()
        },
    }


def expected_social_audience(squad: pd.DataFrame) -> dict:
    """Get the aggregate social audience based off the squad & deliverables"""
    followers = squad.groupby(["influencer_id"]).agg({"followers_count": "first"})

    upper = followers.sum().iloc[0]
    std = followers.std().iloc[0]

    return {
        "upperBound": int(upper),
        "lowerBound": int((upper - (2 * std)) if upper > (2 * std) else 0),
    }


def expected_engagements(
    followers_count: int, engagement_rate: float, social_type: str
) -> int:
    """Linear model of expected engagements"""
    engagement_rate = engagement_rate if engagement_rate > 0 else 0.001
    log_followers = math.log(followers_count + 1)
    log_engagement_rate = math.log(engagement_rate)
    social_type = 1 if social_type == "story" else 0
    result = (
        4.281810
        + 0.333010 * log_followers
        + 0.351721 * log_engagement_rate
        - 6.188532 * social_type
    )
    return round(math.exp(result), 0)


def expected_impressions(
    followers_count: int, engagement_rate: float, social_type: str
) -> int:
    """Linear model of expected impressions"""
    engagement_rate = engagement_rate if engagement_rate > 0 else 0.001
    log_followers = math.log(followers_count + 1)
    log_engagement_rate = math.log(engagement_rate)
    social_type = 1 if social_type == "story" else 0
    result = (
        1.670552
        + 0.874800 * log_followers
        + 0.569204 * log_engagement_rate
        - 1.910629 * social_type
    )
    return round(math.exp(result), 0)


def expected_reach(
    followers_count: int, engagement_rate: float, social_type: str
) -> int:
    """Linear model of expected reach"""
    engagement_rate = engagement_rate if engagement_rate > 0 else 0.001
    log_followers = math.log(followers_count + 1)
    log_engagement_rate = math.log(engagement_rate)
    social_type = 1 if social_type == "story" else 0
    result = (
        1.419314
        + 0.880711 * log_followers
        + 0.554041 * log_engagement_rate
        - 1.913101 * social_type
    )
    return round(math.exp(result), 0)


def calculate_expected(row: pd.Series) -> pd.DataFrame:
    """
    Calculated the expected engagment, imopressions and reach for each
    squad member

    row : pd.Series
            The dataframe row containing the squad members details

    return pd.Series
            A new row, containing the expected performance of the squad member.
    """
    engagement = expected_engagements(
        row["followers_count"], row["engagement_rate"], row["deliverable_type"]
    )
    impressions = expected_impressions(
        row["followers_count"], row["engagement_rate"], row["deliverable_type"]
    )
    reach = expected_reach(
        row["followers_count"], row["engagement_rate"], row["deliverable_type"]
    )

    return pd.Series(
        {"engagement": engagement, "impressions": impressions, "reach": reach},
        index=EXPECTED_COLS,
    )


def format_current_performance(campaign: pd.Series, deliverables: pd.DataFrame) -> dict:
    """
    Format the structure of the current performance section into a readible dictionary
    ready for campaign monitor. The dictionary should contain the current
    engagment, impressions & reach as well as the percentage of live deliverables.

    campaign : pd.Series
            A single campaign represented as a data frame row which is then
            formatted

    deliverables : pd.DataFrame
            The dataframe containing all deliverables including the squad of the
            current campaign

    returns : dict
            The formatted current performance section ready for campaign monitor
    """
    campaign["campaign_id"]
    squad = deliverables.query("campaign_id == @camp_id")

    if len(squad) > 0:
        # Model expected performance
        squad_performance = squad.loc[:, EXPECTED_COLS]

        current_section = squad_performance.sum().astype(int).to_dict()
        live = (squad["is_live"].sum() / len(squad)) * 100
        missing_stats = (
            squad["impressions"].isna()
            & squad["reach"].isna()
            & squad["engagement"].isna()
        ).sum() / len(squad)
        missing_stats = int(missing_stats * 100)
    else:
        current_section = {k: 0 for k in EXPECTED_COLS}
        live = 0
        missing_stats = 0

    return {
        **current_section,
        "live": int(live),
        "missing": missing_stats,
        "talent": squad["influencer_id"].nunique(),
        "social_audience": expected_social_audience(squad)["upperBound"],
    }


def format_squad_estimates(campaign: pd.Series, deliverables: pd.DataFrame) -> dict:
    """
    Format the structure of the squad estimate section into a readible dictionary
    ready for campaign monitor. The dictionary should contain the expected
    engagment, impressions & reach for the currently selected squad.

    campaign : pd.Series
            A single campaign represented as a data frame row which is then
            formatted

    deliverables : pd.DataFrame
            The dataframe containing all deliverables including the squad of the
            current campaign

    returns : dict
            The formatted squad estimate section ready for campaign monitor
    """
    campaign["campaign_id"]
    squad = deliverables.query("campaign_id == @camp_id")

    if len(squad) > 0:
        # Model expected performance
        squad_expectation = squad.apply(calculate_expected, axis=1)

        # format upper & lower bounds
        upper = squad_expectation.sum()
        lower = upper - (2 * squad_expectation.std())

        squad_section = {
            u[0]: {"upperBound": u[1], "lowerBound": l[1]}
            for u, l in zip(
                upper.astype("int", errors="ignore").items(),
                lower.astype("int", errors="ignore").items(),
            )
        }
    else:
        squad_section = {k: {} for k in EXPECTED_COLS}

    return {
        **squad_section,
        "talent": squad["influencer_id"].nunique(),
        "social_audience": expected_social_audience(squad),
    }


def format_brief_estimates(campaign: pd.Series) -> dict:
    """
    Format the structure of the brief estimate section into a readible dictionary
    ready for campaign monitor. The dictionary should contain the original and
    adjusted estimates quoted during the `brief` creation.

    Please note that this function should be applied to the rows of a dataframe,
    and it expects that the deflating the estimates based on the percentage of
    tokens spent have occured. see: `transform_campaigns(campaigns, results)`

    campaign : pd.Series
            A single campaign represented as a data frame row which is then
            formatted
    """
    brief_section = {}
    brief_cols = ["engagement", "impressions", "reach", "social_audience", "talent"]
    col_prefix = {"adjusted": "deflated_estimated_", "original": "estimated_"}

    brief_section = {
        col: {
            "adjusted": campaign[f'{col_prefix["adjusted"]}{col}'],
            "original": json.loads(campaign[f'{col_prefix["original"]}{col}']),
        }
        for col in brief_cols
        if campaign[f"estimated_{col}"] is not None
    }

    if 1 > campaign["rel_remaining_tokens"] > 0:
        brief_section["budget"] = int((1 - campaign["rel_remaining_tokens"]) * 100)
    else:
        brief_section["budget"] = 100

    return brief_section


def defalte_quote_spend(campaign: pd.Series, quote_col: str) -> pd.Series:
    """Deflate what ever the quote was by how much of their budget theyve spent"""

    if campaign[quote_col] is not None:

        try:
            quote = json.loads(campaign[quote_col])

            if 1 > campaign["rel_remaining_tokens"] > 0:
                quote["lowerBound"] = int(
                    quote["lowerBound"] * (1 - campaign["rel_remaining_tokens"])
                )
                quote["upperBound"] = int(
                    quote["upperBound"] * (1 - campaign["rel_remaining_tokens"])
                )

            return quote
        except Exception as e:
            print(e)
            print(quote)

    return campaign[quote_col]


def transform_campaigns(campaigns: pd.DataFrame, results: pd.DataFrame) -> pd.DataFrame:

    # calculate management tokens & remaining tokens
    available = campaigns["total_coins"]
    spent = campaigns["spent_coins"] + campaigns["additional_coins"]

    campaigns["remaining_tokens"] = available - spent
    campaigns["rel_remaining_tokens"] = (available - spent) / available

    adjusted = campaigns.copy()
    for col in [
        "estimated_engagement",
        "estimated_impressions",
        "estimated_reach",
        "estimated_social_audience",
        "estimated_talent",
    ]:
        try:
            adjusted[f"deflated_{col}"] = campaigns.apply(
                lambda row: defalte_quote_spend(row, col), axis=1
            )
        except Exception as e:
            print(e)
            print(campaigns.apply(lambda row: defalte_quote_spend(row, col), axis=1))

    return adjusted


def get_icon(campaign, section, stat):
    # TODO: Make a donut graph of current stats to lower bound
    # perc = campaign['compare'][section][stat] * 100 if campaign['compare'][section][stat] <= 1 else 100
    # return percentage_html.format(percentage=int(perc))
    icon = "🫠"

    try:
        if 1 > campaign["compare"][section][stat] >= 0.5:
            icon = "⚠️"
        elif campaign["compare"][section][stat] >= 1:
            icon = "✅"
    except:
        icon = ""

    return icon


def render_statistic(stat):
    if isinstance(stat, dict):
        try:
            return f"{stat['lowerBound']:,} - {stat['upperBound']:,}"
        except:
            return ""
    elif str(stat).isnumeric():
        return f"{stat:,}"
    elif isinstance(stat, str):
        return stat

    return ""


def format_html_rows(campaign: pd.Series, section: str, ignore: list) -> list:
    """ """
    return [
        performance_statistic.format(
            css_class="",
            icon=get_icon(campaign, section, key),
            stat=str(key).replace("_", " ").capitalize(),
            value=render_statistic(
                campaign[section][key]["adjusted"]
                if isinstance(campaign[section][key], dict)
                and "adjusted" in campaign[section][key].keys()
                else campaign[section][key]
            ),
        )
        for key in sorted(campaign[section].keys())
        if key not in ignore and bool(campaign[section][key])
    ]


def format_html(campaign: pd.Series, section: str, ignore: list) -> str:

    stat_rows = format_html_rows(campaign=campaign, section=section, ignore=ignore)
    return (
        performance_sections.format(table_rows="".join(stat_rows))
        .replace("\t", "")
        .replace("\n", "")
    )


def format_template(
    campaign: pd.Series, results: pd.DataFrame, benchmark: pd.DataFrame
) -> pd.Series:
    """
    Format the HTML template for pricing insights. This creates 3 tables of
    insights and highlights any that are outside the specified statistic ranges

    campaigns : pd.DataFrame
            The dataframe containing the active campaigns

    results : pd.DataFrame
            The dataframe containing the deliverables for each campaign

    return : dict
            The formatted dictionary for the email
    """

    # add budget section
    campaign["quote"] = format_brief_estimates(campaign)
    campaign["squad"] = format_squad_estimates(campaign, results)
    campaign["current"] = format_current_performance(campaign, results)

    campaign["bench"] = format_benchmark(campaign, results, benchmark)
    campaign["compare"] = compare_sections(campaign)

    campaign["quote_html_stats"] = format_html(campaign, "quote", ["budget"])
    campaign["squad_html_stats"] = format_html(campaign, "squad", [])
    campaign["bench_html_stats"] = format_html(
        campaign, "bench", ["categories", "regions"]
    )
    campaign["current"] = format_numbers(campaign["current"])

    return campaign


def compare(campaign, section, stat):

    try:
        actual = campaign["current"][stat]
    except:
        logger.info(
            f"Statistic {stat} could not be found in the current campaign"
            f" {campaign['campaign_id']}"
        )

    try:
        if "adjusted" in campaign[section][stat].keys():
            lower = campaign[section][stat]["adjusted"].get("lowerBound")
            upper = campaign[section][stat]["adjusted"].get("upperBound")
        else:
            lower = campaign[section][stat].get("lowerBound")
            upper = campaign[section][stat].get("upperBound")
    except:
        lower = campaign[section][stat]
        upper = None

    result = 0

    # fail safe for campaigns with no squad selected
    if (lower is None or lower == 0) and upper is None:
        result = 0

    if upper is not None:
        if (upper >= actual >= lower) or upper == 0:
            result = 1
        elif actual > upper:
            result = actual / upper
        else:
            result = actual / lower

    else:
        result = actual / lower

    return result if result in [0, 1] else result // 0.01 / 100


def compare_sections(campaign_data, sections=["quote", "squad", "bench"]):
    (100 - campaign_data["current"]["missing"]) / 100
    ignore_map = {"bench": ["categories", "regions"], "quote": ["budget"]}

    return {
        section: {
            key: compare(campaign=campaign_data, section=section, stat=key)
            for key in campaign_data[section]
            if key not in ignore_map.get(section, [])
            and bool(campaign_data[section][key])
        }
        for section in sections
    }


def format_numbers(obj: dict) -> dict:

    for key in obj.keys():

        if isinstance(obj[key], dict):
            obj[key] = format_numbers(obj[key])

        else:
            try:
                y = float(obj[key])
                y = f"{y:,.0f}"
                obj[key] = y
            except:
                obj[key] = obj[key]
            continue

    return obj


def create_email(event: any, context: any) -> None:
    """
    Create the campaign performance email. This function is the entry point
    for the AWS lambda, it querys the DB for the campaigns & their performance,
    formats the HTML email and finally sends it off using campaign monitor.
    This lambda should be triggered by a cron job at the end of every week for
    the previous week

    event : aws lambda default arg
            Not used by the function

    context : aws lambda default arg
            Not used by the function
    """
    RECIPIENTS = os.getenv("EMAIL_LIST").split(",")
    CM_API_KEY = os.getenv("CM_API_KEY")
    CM_EMAIL_TEMPLATE = os.getenv("CM_CAMP_PERF_TEMPLATE")

    campaigns = fetch_data(CAMPAIGNS)
    campaigns = campaigns.merge(
        fetch_data(CAMPAIGN_CAT_REGION),
        how="left",
        left_on="campaign_id",
        right_on="campaign_id",
    )

    results = fetch_data(DELIVERABLES)
    benchmark = fetch_data(BENCH_MARK)

    # Filter out any campaigns that dont have deliverables to report on
    campaigns = campaigns.loc[
        campaigns["campaign_id"].isin(results["campaign_id"].unique()), :
    ]

    logger.info(f"Processing { len(campaigns) } campaign(s) for performance email")
    campaigns = transform_campaigns(campaigns, results)
    email_data = campaigns.apply(
        lambda campaign: format_template(campaign, results, benchmark), axis=1
    )
    final_cols = [
        "campaign_id",
        "campaign_name",
        "quote",
        "quote_html_stats",
        "squad",
        "squad_html_stats",
        "bench",
        "bench_html_stats",
        "current",
        "compare",
    ]

    consent_to_track = "no"
    auth = {"api_key": CM_API_KEY}
    errors = 0
    error_threshold = 0.1

    for camp in email_data.loc[:, final_cols].to_dict("records"):
        try:
            tx_mailer = Transactional(auth)
            # Send the message and save the response
            # print(json.dumps(camp, indent=4))

            # TODO: replace RECIPIENTS with campaign owner email (where not a vamp email)
            response = tx_mailer.smart_email_send(
                CM_EMAIL_TEMPLATE, RECIPIENTS, consent_to_track, data=camp
            )

            # TODO: Log any that are really bad
        except Exception as e:
            logger.info("An error occured whilst sending the email")
            logger.error(e)
            logger.info(json.dumps(camp, indent=4))

            errors = errors + 1

    if errors / len(campaigns) > error_threshold:
        # Raise error to make data team aware of issue/potential bug.
        raise Exception(
            f"More than { errors // len(campaigns) }% of campaign performance emails"
            " are failing to send"
        )


if __name__ == "__main__":
    """For testing purposes"""
    create_email(None, None)

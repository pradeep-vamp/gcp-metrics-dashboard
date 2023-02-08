"""
 pricing-insights.py

 @ticket:	https://vampdash.atlassian.net/browse/DAS-8606
 @date:		2022-03-16
 @auth:		Daniel Stratti < daniels@vamp.me >

 @desc:
 This lambda function is triggered via scheduling to collect pricing insights
 and send out a newsletter monthly. The things to consider in this email are:

 - Percentage of deliverables by channel and country that are above 5 tokens in price.
 (Limited to countries with at least 200 brief requirements in the month)

 - Flag countries/channels with rates above 10%

 - Application rates by country
 (flagging countries with application rates outside of 20-40%)

 - Average price changes by country and deliverable type (In major markets)
 (Flagg bigest changes in each region)
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


"""
This query counts all the deliverables, based on the data from the previous month
"""
ALL_TOKENS = """
	SELECT d.id
		, inf.country
		, sp.code AS platform
		, cur.code AS currency_code
		, cur.symbol AS currency_symbol
		, ctv.token_value AS campaign_token_value
		, (d.reward_value / br.token_cost) AS actual_token_value
		, d.reward_value AS reward_value
		, br.token_cost AS token_cost
		, camp.cogs
	FROM brief_requirements br
	JOIN briefs ON briefs.id = br.brief_id
	JOIN influencers inf ON inf.id = briefs.influencer_id
	JOIN deliverables d ON d.brief_id = briefs.id
		AND d.deliverable_type_id = br.deliverable_type_id
	JOIN deliverable_types dt ON dt.id = br.deliverable_type_id
	JOIN social_platforms sp ON sp.id = dt.social_platform_id
	JOIN campaigns as camp on camp.id = briefs.campaign_id
	JOIN campaign_token_values ctv ON ctv.campaign_id = camp.id
		AND ctv.social_platform_id = dt.social_platform_id
	JOIN currencies cur ON cur.id = camp.currency_id
	JOIN teams as t on t.id = camp.team_id
	WHERE t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
	AND (camp.desired_age_ranges<>'100-999' OR camp.desired_age_ranges IS NULL)
	AND (
		br.inserted_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
		AND br.inserted_at < DATE_TRUNC('month', CURRENT_DATE)
	)
	AND br.quantity > 0;
"""


"""
This query counts all the applications sent, notified, viewed, applied and
selected for a campaign the data in this query is then transformed to get the
application rate inside of the `format_template` function.
"""
APPLICATION_RATES = """
	SELECT countries.region as region
		, countries.name as country
		, count(*) as sent
		, SUM(case when notified is not null THEN 1 ELSE 0 END) as notifications
		, sum(case when DATE_PART('day',b.inserted_at- last_active_brief_sent) < 32 THEN 1 ELSE 0 END) as active
		, sum(case when is_viewed = True then 1 else 0 end) as viewed
		, sum(case when b.brief_status_id in (
					select id
					from brief_statuses
					where code in ('invitation_accepted','shortlisted','approved','rejected','fulfilled','completed','media_uploaded','media_accepted','processing_payment' )
				)
				THEN 1
				ELSE 0
			END) as applied
		, sum(case when b.brief_status_id in (
					select id
					from brief_statuses
					where code in ('approved','fulfilled','completed','media_uploaded','media_accepted','processing_payment' )
				)
				THEN 1
				ELSE 0
			END) as selected

	from briefs as b
	inner join influencer_countries as ic on ic.influencer_id = b.influencer_id
	inner join countries on countries.id = ic.country_id
	left join (select distinct brief_id, 1 as notified from notifications) as n on n.brief_id = b.id
	inner join campaigns as c on c.id = b.campaign_id
	inner join teams as t on t.id = c.team_id
	where t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
	AND (c.desired_age_ranges<>'100-999' OR c.desired_age_ranges IS NULL)
	AND (
		c.started_on >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
		AND c.started_on < DATE_TRUNC('month', CURRENT_DATE)
	)
	GROUP BY 1,2
		HAVING COUNT(b) > 200;
"""


"""
This query calculates the average price adjustment for creators grouped by the
deliverable type, country and currency. This query also only looks at markets
that had at least 10 changed prices
"""
PRICE_CHANGE = """
	SELECT sp.code AS platform
		, dt.name AS deliverable
		, cntry.name AS country
		, cur.code AS currency
		, ROUND(AVG(((br.custom_price - br.max_price) / br.max_price) * 100), 2) AS avg_percent
		, COUNT(br) AS changed_count
	FROM brief_requirements br
	JOIN deliverable_types dt ON dt.id = br.deliverable_type_id
	JOIN social_platforms sp ON sp.id = dt.social_platform_id
	JOIN rate_cards rc ON rc.id = br.rate_card_id
	JOIN countries cntry ON cntry.id = rc.country_id
	JOIN currencies cur ON cur.id = rc.currency_id
	JOIN briefs ON briefs.id = br.brief_id
	JOIN campaigns as camp on camp.id = briefs.campaign_id
	JOIN teams as t on t.id = camp.team_id
	WHERE t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
		AND (camp.desired_age_ranges<>'100-999' OR camp.desired_age_ranges IS NULL)
		AND (
			camp.started_on >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
			AND camp.started_on < DATE_TRUNC('month', CURRENT_DATE)
		)
		AND br.custom_price IS NOT NULL
		AND cur.code IN ('AUD', 'EUR', 'GBP', 'USD')
		AND br.quantity > 0
		AND br.max_price > 0
	GROUP BY 1, 2, 3, 4
		HAVING COUNT(br) >= 10
			AND ROUND(AVG(((br.custom_price - br.max_price) / br.max_price) * 100), 2) >= 50;
"""


""" Generic structure for the deliverable table rows """
deliverable_row = """
	<tr class="{css_class}">
			<td class="table-row" style="width: 24px">{platform}</td>
			<td style="padding:0 0 0 0;width: 30%">
				{percentage} ({count})
			</td>
			<td style="text-align: right; width: 50%"> [{recommend}]</td>
	</tr>
"""

deliverable_section = """
	<h3>
		{icon}
		{country}
	</h3>
	<table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;">
		{table_rows}
	</table>
"""


""" Generic structure for the application table rows """
country_row = """
	<tr class="{css_class}">
		<td class="table-row" style="width: auto">{country}</td>
		<td style="text-align: right; width: 30%">{percentage} %</td>
	</tr>
"""


""" Generic structure for the price change table rows """
price_row = """
	<tr class="{css_class}">
		<td class="table-row" style="width: auto;">{country}</td>
		<td style="text-align: right;width: 35%">{percentage} %</td>
	</tr>
"""

price_section_platform = """
	<h3>
		{icon}
		{platform}
	</h3>
"""

price_section_deliverable = """
	<h4>{deliverable_name}</h4>
	<table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;">
		{table_rows}
	</table>
"""


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


def fetch_deliverables() -> tuple:
    """Fetch the deliverables above 5 tokens insights"""
    connect_str = set_connection_str()
    engine = create_engine(connect_str)

    return pd.io.sql.read_sql(ALL_TOKENS, engine)


def fetch_applications() -> pd.DataFrame:
    """Fetch the application rate insights"""
    connect_str = set_connection_str()
    engine = create_engine(connect_str)

    return pd.io.sql.read_sql(APPLICATION_RATES, engine)


def fetch_price_change() -> pd.DataFrame:
    """Fetch the price change insights"""
    connect_str = set_connection_str()
    engine = create_engine(connect_str)

    return pd.io.sql.read_sql(PRICE_CHANGE, engine)


def build_deliverable_section(deliverables: pd.DataFrame) -> str:
    """
    Generate the  email section displaying the average deliverable price
    increase, aggregated by platform, deliverable & country, based on the
    deliverables processed in the previous month

    price : pd.DataFrame
            The datframe resulting from the `PRICE_CHANGE` query

    returns : str
            The HTML required to populate the average price change section
    """
    global deliverable_row
    global platform_icons
    global deliverable_section

    deliverables.sort_values(by=["percent_above_5"], ascending=False, inplace=True)
    countries = deliverables["country"].unique()
    groups = deliverables.groupby(["country"])

    d_section = ""

    for country in countries:
        del_rows = [
            deliverable_row.format(
                css_class="highlight" if row["percent_above_5"] > 10 else "",
                platform=platform_icons.get(row["platform"], ""),
                percentage=f"{row['percent_above_5']}%",
                count=row["five_tokens_count"],
                recommend=(
                    f"({row['currency_code']})"
                    f" {row['currency_symbol']} {row['recomended_token_value']}"
                ),
            )
            for idx, row in groups.get_group(country).iterrows()
        ]

        platform_section = deliverable_section.format(
            icon="", country=country.capitalize(), table_rows="".join(del_rows)
        )

        d_section = f"{d_section}{platform_section}"

    return d_section


def format_price_rows(price: pd.DataFrame, row_template: str) -> list:
    """Format the `price_rows` template"""
    return [
        row_template.format(
            css_class="" if -75 <= row["avg_percent"] <= 75 else "highlight",
            country=row["country"],
            percentage=row["avg_percent"],
        )
        for idx, row in price.iterrows()
    ]


def build_price_section(price: pd.DataFrame) -> str:
    """
    Generate the  email section displaying the average deliverable price
    increase, aggregated by platform, deliverable & country, based on the
    deliverables processed in the previous month

    price : pd.DataFrame
            The datframe resulting from the `PRICE_CHANGE` query

    returns : str
            The HTML required to populate the average price change section
    """
    global price_row
    global platform_icons
    global price_section_platform
    global price_section_deliverable

    price.sort_values(by=["avg_percent"], ascending=False, inplace=True)

    price_section = ""

    for platform, deliverables in price.groupby(["platform"]):
        platform_section = price_section_platform.format(
            icon=platform_icons.get(platform, "").replace(
                "display:block;", "display:inline-block;vertical-align:middle;"
            ),
            platform=platform.capitalize(),
        )

        for deliverable, countries in deliverables.groupby("deliverable"):
            deliverable_rows = format_price_rows(countries, price_row)
            deliverable_section = price_section_deliverable.format(
                deliverable_name=deliverable,
                table_rows="".join(deliverable_rows),
            )

            platform_section = f"{platform_section}{deliverable_section}"

        price_section = f"{price_section}{platform_section}"

    return price_section


def format_template(
    deliverables: pd.DataFrame, applications: pd.DataFrame, price: pd.DataFrame
) -> dict:
    """
    Format the HTML template for pricing insights. This creates 3 tables of
    insights and highlights any that are outside the specified statistic ranges

    deliverables : pd.DataFrame
            The dataframe containing the delivarables above 5 tokens

    applications : pd.DataFrame
            The dataframe containing the application rates by country

    price : pd.DataFrame
            The datafram containing the average price change by country and deliverable type

    return : str
            The formatted HTML as a string ready to be emailed
    """
    applications["app_rate"] = (
        (applications["applied"] / applications["viewed"]) * 100
    ).round(decimals=2)

    applications.sort_values(by=["app_rate"], ascending=False, inplace=True)
    app_country_rows = [
        country_row.format(
            css_class="" if 20 <= row["app_rate"] <= 40 else "highlight",
            country=row["country"],
            percentage=row["app_rate"],
        )
        for idx, row in applications.fillna(0).iterrows()
    ]

    return dict(
        deliverable_section=build_deliverable_section(deliverables),
        country_rows="".join(app_country_rows),
        price_section=build_price_section(price),
    )


def calc_token_value(row):
    """Using a fixed token cost of 5, determine the token value"""
    token_cost = 5
    top = (1.1 * row["reward_value"]) / token_cost
    bottom = 100 / row["cogs"]

    return top / bottom


def recommended_token_value(group):
    """
    Based on deliverables grouped by 'country', 'platform' & 'currency_code'
    determine the recommended token value in order to only have 10% of
    deliverables above 5 tokens. If a group already has less than 10%
    deliverables the recommended token value is the campaign token value

    group : pd.DataFrameGroupBy
            Should be all_tokens grouped by 'country', 'platform' & 'currency_code'
            but only after the `5_token_value` has been calculated for each deliverable

    returns : pd.Series
            Returns a formatted row ready for emailing
    """
    percent = 0.1
    five_tokens = (
        group.query("token_cost > 5").sort_values(["5_token_value"]).reset_index()
    )
    ten_p_ceil = math.ceil(len(group) * percent)
    ten_p_floor = math.floor(len(group) * percent)

    rtoken_val = group.iloc[0]["campaign_token_value"]
    five_perc = len(five_tokens) / len(group)

    if len(five_tokens) > ten_p_ceil or len(five_tokens) > ten_p_floor:
        rtoken_val = five_tokens.iloc[ten_p_floor : ten_p_ceil + 1][
            "5_token_value"
        ].mean()

    return pd.Series(
        {
            "currency_symbol": group.iloc[0]["currency_symbol"],
            "percent_above_5": round(five_perc * 100, 2),
            "five_tokens_count": len(five_tokens),
            "all_tokens_count": len(group),
            "campaign_token_value": group.iloc[0]["campaign_token_value"],
            "recomended_token_value": round(rtoken_val, 2),
        },
        index=[
            "currency_symbol",
            "percent_above_5",
            "five_tokens_count",
            "all_tokens_count",
            "campaign_token_value",
            "recomended_token_value",
        ],
    )


def calculate_token_stats():
    all_tokens = fetch_deliverables()

    # calculate token value if token cost was 5
    all_tokens["5_token_value"] = all_tokens.apply(calc_token_value, axis=1)

    # calculate percentage of deliverables > 5 tokens for each country & platform
    formatted_deliverables = (
        all_tokens.sort_values(["5_token_value"])
        .groupby(["country", "platform", "currency_code"])
        .apply(recommended_token_value)
    )

    return formatted_deliverables.query("percent_above_5 > 0").reset_index()


def create_email(event: any, context: any) -> None:
    """
    Create the pricing insight newsletter email. This function is the entry point
    for the AWS lambda, it querys the DB for the insights, formats the HTML email
    and finally sends it off. This lambda should be triggered by a cron job at
    the beginiing of every month for the previous month

    event : aws lambda default arg
            Not used by the function

    context : aws lambda default arg
            Not used by the function
    """
    RECIPIENTS = os.getenv("EMAIL_LIST").split(",")
    CM_API_KEY = os.getenv("CM_API_KEY")
    CM_EMAIL_TEMPLATE = os.getenv("CM_EMAIL_TEMPLATE")

    deliverables = calculate_token_stats()
    applications = fetch_applications()
    price = fetch_price_change()

    # The message
    email_data = format_template(deliverables, applications, price)
    consent_to_track = "no"  # Valid: 'yes', 'no', 'unchanged'
    auth = {"api_key": CM_API_KEY}

    try:
        print(json.dumps(email_data, indent=4))
        tx_mailer = Transactional(auth)
        # Send the message and save the response
        response = tx_mailer.smart_email_send(
            CM_EMAIL_TEMPLATE, RECIPIENTS, consent_to_track, data=email_data
        )
    except Exception as e:
        logger.info("An error occured whilst sending the email")
        logger.error(e)
    else:
        logger.info(f"Email sent!")


if __name__ == "__main__":
    """For testing purposes"""
    create_email(None, None)

"""
 data/influencer_usage.py

 @ticket: https://vampdash.atlassian.net/browse/DAS-7706
 @date:   2021-05-05
 @auth:   Daniel Stratti < daniels@vamp.me >

 @desc:
 This file is used to fetch the data from postgres required by the
 influencer_usage page. The two main data components are the data table showing
 usage stats for influencers that match a filter criteria, the second is a
 cumulative proportion graph of the proportion of campaings vs proportion of
 influencers
"""
import pandas as pd
from psycopg2 import sql

from data.functions import fetch_from_postgres

"""
Fetch list of applicable regions
"""


def fetch_region(start_date=None, end_date=None, team=None, customer_type=None):
    query = """
        SELECT DISTINCT
            region AS label,
            region AS value
        FROM
            countries
            JOIN influencer_countries inf_country ON
                inf_country.country_id = countries.id
            JOIN influencers inf ON
                inf.id = inf_country.influencer_id
            JOIN briefs ON
                briefs.influencer_id = inf.id
            JOIN campaigns ON
                campaigns.id = briefs.campaign_id
            JOIN teams ON
                teams.id = campaigns.team_id
        WHERE
            region IS NOT NULL
            AND campaigns.deleted_at IS NULL """
    if start_date is not None:
        query = f"{query} AND briefs.inserted_at >= '{start_date}'"

    if end_date is not None:
        query = f"{query} AND briefs.inserted_at <= '{end_date}'"

    if team is not None:
        query = f"{query} AND teams.id = {team}"

    if customer_type is not None:
        query = f"{query} AND teams.type = '{customer_type}'"

    return fetch_from_postgres(sql.SQL(query))


"""
Fetch the list of applicable teams
"""


def fetch_teams(start_date, end_date, region=None, customer_type=None):
    query = """
        SELECT DISTINCT
            COALESCE(teams.name, teams.code) AS display_name,
            teams.*
        FROM
            teams
            JOIN campaigns ON
                campaigns.team_id = teams.id
            JOIN campaign_statuses status ON
                status.id = campaigns.campaign_status_id
            JOIN briefs ON
                briefs.campaign_id = campaigns.id
            JOIN influencers inf ON
                briefs.influencer_id = inf.id
            JOIN influencer_countries inf_country ON
                inf_country.influencer_id = inf.id
            JOIN countries ON
                countries.id = inf_country.country_id
        WHERE
            status.code IN (
                'ready_for_shortlisting',
                'ready_for_approval',
                'approved',
                'fulfilled',
                'active',
                'paid')
            AND campaigns.self_brief = FALSE
            AND campaigns.deleted_at IS NULL """

    if start_date is not None:
        query = f"{query} AND briefs.inserted_at >= '{start_date}'"

    if end_date is not None:
        query = f"{query} AND briefs.inserted_at <= '{end_date}'"

    if region is not None:
        query = (
            "{q} AND (countries.region = '{area}' OR countries.sub_region = '{area}')"
            .format(q=query, area=region)
        )

    if customer_type is not None:
        query = f"{query} AND teams.type = '{customer_type}'"

    query = f"{query} ORDER BY display_name;"

    return fetch_from_postgres(sql.SQL(query))


"""
Query summary stats on influencer usage of all applicable briefs based on the
current date range & team
@param start_date {Date}: The date the campaign must start on or after
@param end_date {Date}: The date the campaign must end on or before
@param team {Integer}: The specific organisation campaigns to display

@return {DataFrame}: The brie usage data ready for mapping
"""


def fetch_iu_briefs(
    start_date,
    end_date,
    team=None,
    region=None,
    customer_type=None,
    service_level=None,
):

    query = """
    SELECT briefs.id AS brief_id
        , briefs.influencer_id
        , social.id AS social_id
        , social.followers_count
        , (
          CASE
            WHEN b_status.code IN ('approved',
                                  'fulfilled',
                                  'completed',
                                  'media_uploaded',
                                  'media_accepted',
                                  'processing_payment')
              THEN 1
            ELSE 0
          END
        ) AS participation
        , briefs.similarity_score * 100 AS similarity_score
        , social.engagement_rate * 100 AS engagement_rate
        , countries.name AS country
        , countries.region
        , countries.sub_region
    FROM briefs
    JOIN brief_statuses b_status ON b_status.id = briefs.brief_status_id
    JOIN campaigns ON campaigns.id = briefs.campaign_id
    JOIN teams ON teams.id = campaigns.team_id
    JOIN influencers inf ON inf.id = briefs.influencer_id
    JOIN social_accounts social ON social.influencer_id = inf.id
    JOIN influencer_countries ic ON ic.influencer_id = inf.id
    JOIN countries ON countries.id = ic.country_id

    WHERE b_status.code IN ('invitation_accepted',
                            'shortlisted',
                            'approved',
                            'rejected',
                            'fulfilled',
                            'completed',
                            'media_uploaded',
                            'media_accepted',
                            'processing_payment')

    AND campaigns.started_on >= '{start_date}'
    AND campaigns.started_on <= '{end_date}'
    AND campaigns.deleted_at IS NULL
    AND social_platform_id = 1
  """.format(
        start_date=start_date, end_date=end_date
    )

    if team is not None:
        query = f"{query} AND teams.id = {team}"

    if customer_type is not None:
        query = f"{query} AND teams.type = '{customer_type}'"

    if region is not None:
        query = (
            "{q} AND (countries.region = '{area}' OR countries.sub_region = '{area}')"
            .format(q=query, area=region)
        )

    if service_level is not None:
        query = f"{query} AND campaigns.has_managed_service= {service_level}"

    return fetch_from_postgres(sql.SQL(query))


"""
Query the average similarity scores for successful and unsuccessful briefs
@param start_date {Date}: The date the campaign must start on or after
@param end_date {Date}: The date the campaign must end on or before
@param team {String | None}: The team to look at, None looks at all teams
@param region {String | None}: The region to be displayed, None shows all
@param customer_type {String | None}: The type of teams to look at

@return {DataFrame}: A single record containing the average similarity for
                    successful and unsuccessful briefs
"""


def fetch_avg_sim(start_date, end_date, team=None, region=None, customer_type=None):
    query = """
    SELECT AVG(
        CASE
          WHEN b_status.code IN ('shortlisted',
                                'approved',
                                'fulfilled',
                                'completed',
                                'media_uploaded',
                                'media_accepted',
                                'processing_payment')
            THEN briefs.similarity_score
          ELSE NULL
        END
      ) * 100 AS avg_won_similarity
      , AVG(
        CASE
          WHEN b_status.code NOT IN ('shortlisted',
                                    'approved',
                                    'fulfilled',
                                    'completed',
                                    'media_uploaded',
                                    'media_accepted',
                                    'processing_payment')
            THEN briefs.similarity_score
          ELSE NULL
        END
      ) * 100 AS avg_lost_similarity

    FROM briefs
    JOIN brief_statuses b_status ON b_status.id = briefs.brief_status_id
    JOIN campaigns ON campaigns.id = briefs.campaign_id
    JOIN teams ON teams.id = campaigns.team_id
    JOIN influencers inf ON inf.id = briefs.influencer_id
    JOIN influencer_countries ic ON ic.influencer_id = inf.id
    JOIN countries ON countries.id = ic.country_id
    WHERE b_status.code IN ('invitation_accepted',
                            'shortlisted',
                            'approved',
                            'rejected',
                            'fulfilled',
                            'completed',
                            'media_uploaded',
                            'media_accepted',
                            'processing_payment')
    AND briefs.inserted_at >= '{start_date}'
    AND briefs.inserted_at <= '{end_date}'
    AND campaigns.deleted_at IS NULL
  """.format(
        start_date=start_date, end_date=end_date
    )

    if team is not None:
        query = f"{query} AND teams.id = {team}"

    if customer_type is not None:
        query = f"{query} AND teams.type = '{customer_type}'"

    if region is not None:
        query = (
            "{q} AND (countries.region = '{area}' OR countries.sub_region = '{area}')"
            .format(q=query, area=region)
        )

    print(query)
    return fetch_from_postgres(sql.SQL(query))


"""
Query for influencer usage statistics based on filter criteria
@param start_date {Date}: The date the campaign must start on or after
@param end_date {Date}: The date the campaign must end on or before
@param briefs {List}: The list of influencer IDs based of the briefs to include
@param region {String | None}: The region to be displayed, None shows all

@return {DataFrame}: The influencer usage data ready for mapping
"""


def fetch_iu_stats(start_date, end_date, briefs=[], region=None):
    query = """
    SELECT inf.id
        , inf.gender
        , inf.date_of_birth
        , inf.influencer_status_id
        , inf.last_active

        , countries.name AS country
        , countries.sub_region
        , countries.region

        , CASE
            WHEN inf.last_active IS NULL OR DATE_PART('day', NOW() - inf.last_active) > 31
              THEN 'Inactive'
            ELSE 'Active'
          END
        , DATE_PART('year', NOW()) - DATE_PART('year', inf.date_of_birth) AS age
        , i_status.name

        , social.handle
        /*, social.engagement_rate * 100 AS engagement_rate*/
        , social.followers_count

    FROM influencers inf
    JOIN influencer_countries inf_country ON inf_country.influencer_id = inf.id
    JOIN countries ON countries.id = inf_country.country_id
    JOIN social_accounts social ON social.influencer_id = inf.id
    JOIN influencer_statuses i_status ON i_status.id = inf.influencer_status_id

    WHERE
      /* remove test accounts */
      (DATE_PART('year', NOW()) - DATE_PART('year', inf.date_of_birth)) < 90
      AND social_platform_id = 1
    """

    if len(briefs) > 0:
        query = "{q} AND inf.id IN ({brief_ids})".format(
            q=query, brief_ids=", ".join(map(str, briefs))
        )

    if region is not None:
        query = (
            "{q} AND (countries.region = '{area}' OR countries.sub_region = '{area}')"
            .format(q=query, area=region)
        )

    data = fetch_from_postgres(sql.SQL(query))
    return data


"""
Query which influencer has briefs in each of the brief status, that also fall
within a filtered range
@param start_date {Date}: The date the campaign must start on or after
@param end_date {Date}: The date the campaign must end on or before
@param team {String | None}: The team to look at, None looks at all teams
@param region {String | None}: The region to be displayed, None shows all
@param customer_type {String | None}: The type of teams to look at

@return {DataFrame}: The influencer lists of each brief status
"""


def fetch_iu_influencer_briefs(
    start_date,
    end_date,
    team=None,
    region=None,
    customer_type=None,
    service_level=None,
):
    query = """
    SELECT b_status.code
      , array_agg(DISTINCT briefs.influencer_id) AS influencer_ids
    FROM briefs
    JOIN brief_statuses b_status ON b_status.id = briefs.brief_status_id
    JOIN campaigns ON campaigns.id = briefs.campaign_id
    JOIN teams ON teams.id = campaigns.team_id
    JOIN influencer_countries ic ON ic.influencer_id = briefs.influencer_id
    JOIN countries ON countries.id = ic.country_id
    WHERE b_status.code IN ('invitation_accepted',
                            'shortlisted',
                            'approved',
                            'rejected',
                            'fulfilled',
                            'completed',
                            'media_uploaded',
                            'media_accepted',
                            'processing_payment')
      AND briefs.inserted_at >= '{start_date}'
      AND briefs.inserted_at <= '{end_date}'
      AND campaigns.deleted_at IS NULL
  """.format(
        start_date=f"{start_date}", end_date=f"{end_date}"
    )

    if team is not None:
        query = f"{query} AND teams.id = {team}"

    if customer_type is not None:
        query = f"{query} AND teams.type = '{customer_type}'"

    if region is not None:
        query = (
            "{q} AND (countries.region = '{area}' OR countries.sub_region = '{area}')"
            .format(q=query, area=region)
        )

    if service_level is not None:
        query = f"{query} AND campaigns.has_managed_service= '{service_level}'"

    query = f"{query} GROUP BY b_status.code"
    data = fetch_from_postgres(sql.SQL(query))
    return data


"""
Query fetch the local audience stats of each influencer
@param influencers {List}: A list of influencer IDs to lookup
@param region {String | None}: The region to be displayed, None shows all

@return {DataFrame}: The influencer usage data ready for mapping
"""


def fetch_iu_local_audience(influencers=[], region=None):
    query = """
    SELECT social.influencer_id
          , social.id AS social_id
          , CAST(
            audience_val.percentage AS DOUBLE PRECISION
          ) * 100 AS local_audience
          , social.followers_count
          , countries.name AS country
          , countries.region
          , countries.sub_region
    FROM social_accounts social
    LEFT JOIN audience_insights audience ON audience.social_account_id = social.id
    LEFT JOIN audience_insight_values audience_val ON audience_val.audience_insight_id = audience.id
    LEFT JOIN countries ON countries.code = audience_val.tag
    JOIN influencer_countries ic ON ic.influencer_id = social.influencer_id
      AND ic.country_id = countries.id
    WHERE audience.category = 'countries'
  """

    if len(influencers) > 0:
        query = "{q} AND social.influencer_id IN ({inf_ids})".format(
            q=query, inf_ids=", ".join(map(str, influencers))
        )

    if region is not None:
        query = (
            "{q} AND (countries.region = '{area}' OR countries.sub_region = '{area}')"
            .format(q=query, area=region)
        )

    data = fetch_from_postgres(sql.SQL(query))
    return data


"""
Query the influecer engagement rates and local audience
see: data/segmentation.py for original query
@param influencers {List}: The list of influencers to gather stats on

@return {DataFrame}: Influencers engagement rate, local audience rates & follower count
"""


def fetch_local_engagement(influencers=[]):

    query = """
    SELECT si.influencer_id
      , followers_count
      , engagement_rate
      , engagement_rate * followers_count as engagements
      , country
      , local_audience
      , local_audience * followers_count as local_audience_value
      , country_sub_code
    FROM (
      SELECT s.id AS social_account_id
        , is_business
        , influencer_id
        , gender
        , date_of_birth
        , influencer_status_id
        , followers_count
        , engagement_rate
        , last_active
      FROM influencers AS i
      INNER JOIN social_accounts AS s ON i.id = s.influencer_id
    ) AS si
    INNER JOIN (
      SELECT influencer_id
        , country_id
        , name AS country
        , code AS country_code
        , sub_code as country_sub_code
      FROM influencer_countries AS infc
      INNER JOIN countries AS ctr ON ctr.id = infc.country_id
    ) AS country ON si.influencer_id = country.influencer_id
    LEFT JOIN (
      SELECT *
        FROM (
          SELECT social_account_id
            , id AS audience_insight_id
          FROM audience_insights
          WHERE category = 'countries'
        ) AS ai
      INNER JOIN (
          SELECT audience_insight_id
            , tag AS country_code
            , percentage AS local_audience
          FROM audience_insight_values
      ) AS aiv ON ai.audience_insight_id = aiv.audience_insight_id
    ) AS aud_insight ON (aud_insight.social_account_id, aud_insight.country_code ) = (si.social_account_id, country.country_code )
  """.format(
        inf=", ".join(map(str, influencers))
    )

    if len(influencers) == 0:
        return pd.DataFrame(
            columns=[
                "influencer_id",
                "followers_count",
                "engagement_rate",
                "engagements",
                "country",
                "local_audience",
                "local_audience_value",
                "country_sub_code",
            ]
        )

    elif len(influencers) == 1:
        query = f"{query} WHERE si.influencer_id = {influencers[0]}"

    else:
        query = "{query} WHERE si.influencer_id IN ({inf})".format(
            query=query, inf=", ".join(map(str, influencers))
        )

    data = fetch_from_postgres(sql.SQL(query))
    return data

"""
 data/campaign_lookup.py

 @ticket: https://vampdash.atlassian.net/browse/DAS-7702
 @date:   2021-05-05
 @auth:   Daniel Stratti < daniels@vamp.me >

 @desc:
 This file is used to fetch the data from postgres required by the
 campaign_lookup page. The two main data components are the data table showing
 campaign details & the briefs sent out for the campaign
"""
import pandas as pd
from psycopg2 import sql

from data.functions import fetch_from_postgres

"""
Fetch the list of applicable campaigns
"""


def fetch_campaigns(search_term=None):
    query = """
    SELECT DISTINCT CONCAT('[', LPAD(CAST(campaigns.id AS VARCHAR), 6, '0'), '] ', campaigns.name) AS text_value
      , c_status.name as status
      , currencies.symbol AS currency_symbol
      , currencies.code AS currency_code
      , campaigns.*
    FROM campaigns
    JOIN campaign_statuses c_status ON c_status.id = campaigns.campaign_status_id
    JOIN currencies ON currencies.id = campaigns.currency_id
    WHERE campaigns.campaign_status_id NOT IN (8)
  """
    # ignore rejected campaigns

    if search_term is not None:
        query = (
            f"{query} AND( CAST(campaigns.id AS VARCHAR) LIKE '%{search_term}%' OR"
            f" campaigns.name LIKE '%{search_term}%')"
        )

    query = f"{query} ORDER BY text_value LIMIT 100;"

    return fetch_from_postgres(sql.SQL(query))


"""
Fetch the list of applicable briefs
"""


def fetch_briefs_influencers(campaign_id):
    query = """
    SELECT DISTINCT inf.*
      , sp.name AS platform
      , sa.*
      , briefs.id AS brief_id
      , briefs.last_active_brief_sent AS brief_last_active_brief_sent
      , briefs.inserted_at AS brief_inserted_at
      , briefs.is_viewed AS brief_is_viewed
      , briefs.similarity_score
      , briefs.reward_value
      , b_status.name as brief_status
      , b_status.id as brief_status_id
      , CAST(
            audience_val.percentage AS DOUBLE PRECISION
          ) * 100 AS local_audience
    FROM briefs
    JOIN brief_statuses b_status ON b_status.id = briefs.brief_status_id
    LEFT JOIN influencers inf ON inf.id = briefs.influencer_id
    JOIN social_accounts sa ON sa.influencer_id = inf.id
    JOIN social_platforms sp ON sp.id = sa.social_platform_id
    JOIN influencer_countries ic on ic.influencer_id = inf.id
    LEFT JOIN countries ON countries.id= ic.country_id
    LEFT JOIN audience_insights audience ON audience.social_account_id = sa.id
      AND audience.category = 'countries'
    LEFT JOIN audience_insight_values audience_val ON audience_val.audience_insight_id = audience.id
      AND countries.code = audience_val.tag
    WHERE briefs.campaign_id = {camp}
      AND briefs.brief_status_id != 1
    ORDER BY b_status.name;
  """.format(
        camp=campaign_id
    )

    return fetch_from_postgres(sql.SQL(query))


"""
"""


def fetch_notifications(brief_ids=[]):

    if len(brief_ids) > 0:
        query = """
      SELECT *
      FROM notifications note
      WHERE note.notification_error_message IS NULL
        AND note.brief_id IN ({})
    """.format(
            ", ".join(map(str, brief_ids))
        )
        return fetch_from_postgres(sql.SQL(query))

    return pd.DataFrame()  # return empty df

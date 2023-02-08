"""
 data/influencer_usage.py

 @ticket: https://vampdash.atlassian.net/browse/DAS-7704
 @date:   2021-05-10
 @auth:   Daniel Stratti < daniels@vamp.me >

 @desc:
 This file is used to fetch the data from postgres required by the
 influencer_lookup page. The two main data components are the data table showing
 campaign stats for influencers that match a filter criteria, the second are
 some demographics about the influencer
"""
from psycopg2 import sql

from data.functions import fetch_from_postgres


def fetch_ig_token(handle):
    query = sql.SQL(
        """
            SELECT
                sa.social_id,
                sa.social_token
            FROM
                social_accounts sa
            WHERE
                sa.handle = {handle}; """
    ).format(handle=sql.Literal(handle))
    return fetch_from_postgres(query).iloc[0]


def fetch_social_accounts():
    """Fetch the socail account id and handle of all active influencers"""
    query = """
    SELECT DISTINCT sa.id
        , CONCAT(sa.handle, ' [', sp.name, ']') AS handle
    FROM social_accounts sa
    JOIN social_platforms sp ON sp.id = sa.social_platform_id
    JOIN influencers inf ON inf.id = sa.influencer_id
    WHERE inf.influencer_status_id IN (3) --4, 8, 9, 10
      AND sa.social_account_status_id IN (4, 6)
    ORDER BY 2
  """

    return fetch_from_postgres(sql.SQL(query))


def fetch_social_demographics(social_id):
    """
    Fetch the social demographics of a specified influecner

    social_id : integer
      The social_accounts.id of the influencer to fetch

    returns : DataFrame
      The social account id, influener id, handle, media, followers, follows,
      engagement and the influencers status, age, gender, country, login, last_active
    """
    query = """
    SELECT sa.id
        , sa.influencer_id
        , sa.handle
        , sa.media_count
        , COALESCE(sa.followers_count, 0) AS followers_count
        , COALESCE(sa.follows_count, 0) AS follows_count
        , COALESCE(sa.engagement_rate, 0) * 100 AS engagement_percent
        , i_status.code
        , i_status.name AS status
        , DATE_PART('year', NOW()) - DATE_PART('year', inf.date_of_birth) AS age
        , inf.gender
        , cou.name as country
        , inf.last_login_at
        , inf.last_active
        , inf.inserted_at
        , sa.token_valid
    FROM social_accounts sa
    JOIN influencers inf ON inf.id = sa.influencer_id
    JOIN influencer_countries ic on ic.id = inf.id
    JOIN countries cou on cou.id = ic.country_id
    JOIN influencer_statuses i_status ON i_status.id = inf.influencer_status_id
    WHERE sa.id = {social}
      AND inf.influencer_status_id IN (3)
  """.format(
        social=social_id
    )

    return fetch_from_postgres(sql.SQL(query))


def fetch_il_briefs(social_id, start_date=None, end_date=None):
    """
    Fetch all the briefs related to a specific social id within the specified
    period.

    social_id : integer
      The social_accounts.id of the influencer to fetch

    start_date : Date
      The date briefs must start before

    end_date : Date
      The date briefs must end before

    returns : DataFrame
      The campaign name, id, start_date and the brief reward value, photos, status
      and viewed status
    """
    query = """
    SELECT campaigns.name
      , campaigns.id AS campaign_id
      , to_char(campaigns.start_date, 'YYYY-MM-DD') AS start_date
      , briefs.reward_value
      , briefs.total_photos_required
      , b_status.name AS status
      , briefs.is_viewed
    FROM social_accounts social
    JOIN influencers inf ON inf.id = social.influencer_id
    JOIN briefs ON briefs.influencer_id = inf.id
    JOIN brief_statuses b_status ON b_status.id = briefs.brief_status_id
    JOIN campaigns ON campaigns.id = briefs.campaign_id
      AND social.id = {social}
      AND inf.influencer_status_id IN (3)
  """.format(
        social=social_id
    )

    if start_date is not None and end_date is not None:
        query = (
            f"{query} AND briefs.start_date >= '{start_date}' AND briefs.end_date <="
            f" '{end_date}'"
        )

    print(query)
    return fetch_from_postgres(sql.SQL(query))


def fetch_stat_distributions(social_id):
    """
    Fetch the social accounts stats of all the active accounts that fall within
    the same rate card as a specified influecner

    social_id : integer
      The social_accounts.id of the influencer to fetch

    returns : DataFrame
      The influecner id, social account id and handle, the rate card coin count,
      criteria, min & max range, as well as the social account followers, follows,
      media and engagement
    """
    query = """
    SELECT DISTINCT inf.id AS influencer_id
      , sa.id
      , sa.handle
      , sa_rc.coin_count
      , sa_rc.criteria
      , sa_rc.min_range
      , sa_rc.max_range
      , sa.followers_count
      , sa.follows_count
      , sa.media_count
      , sa.engagement_rate * 100 AS engagement_percent
      , sa.token_valid
    FROM social_accounts sa
    JOIN influencers inf ON inf.id = sa.influencer_id
    JOIN influencer_countries ic on ic.influencer_id = inf.id
    JOIN countries cou on cou.id = ic.country_id
    JOIN influencer_statuses i_status ON i_status.id = inf.influencer_status_id
    JOIN (
      SELECT DISTINCT rc1.coin_count
        , rc1.criteria
        , rc1.min_range
        , rc1.max_range
        , country1.name AS country
        , sa1.social_platform_id
      FROM social_accounts sa1
      JOIN social_platforms sp1 ON sp1.id = sa1.social_platform_id
      JOIN influencers inf1 ON inf1.id = sa1.influencer_id
      JOIN influencer_countries ic on ic.influencer_id = inf1.id
      JOIN countries country1 ON country1.id = ic.country_id
      JOIN rate_cards rc1 ON sa1.followers_count BETWEEN rc1.min_range AND rc1.max_range
        AND rc1.criteria LIKE CONCAT(sp1.code, '%')
        AND rc1.country_id = country1.id
        AND rc1.currency_id = country1.default_currency_id
      WHERE rc1.active = TRUE
        AND sa1.id = {social}
    ) sa_rc ON sa.followers_count BETWEEN sa_rc.min_range AND sa_rc.max_range
        AND sa_rc.social_platform_id = sa.social_platform_id
    WHERE cou.name = sa_rc.country
      AND (DATE_PART('year', NOW()) - DATE_PART('year', inf.date_of_birth)) < 90
      AND i_status.name IN ('Approved')
  """.format(
        social=social_id
    )

    return fetch_from_postgres(sql.SQL(query))


def fetch_audience_stats(social_id):
    """
    Fetch the audience stats for a specified social account

    social_id : integer
      The social_accounts.id of the influencer to fetch

    returns : DataFrame
      The social account id, the audience insight category, the audience insight
      value tag, percentage and value
    """
    query = """
    SELECT sa.id AS social_account_id
      , ai.category
      , COALESCE(countries.name, aiv.tag) AS tag
      , aiv.percentage
      , aiv.value
      , sa.token_valid
    FROM audience_insights ai
    JOIN audience_insight_values aiv ON aiv.audience_insight_id = ai.id
    JOIN social_accounts sa ON sa.id = ai.social_account_id
    LEFT JOIN countries ON countries.code = aiv.tag
    WHERE sa.id = {social}
      AND ai.category IN ('countries', 'gender', 'gender_age', 'age')
  """.format(
        social=social_id
    )

    return fetch_from_postgres(sql.SQL(query))

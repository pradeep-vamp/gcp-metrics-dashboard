import os

import pandas as pd
from psycopg2 import sql

from data.fixer import conversion
from data.functions import currency_conversions, fetch_from_postgres


def retrieve_campaigns(start_date, end_date, customer_type):
    if customer_type == "selfserve":
        enterprise_statement = (
            "(lower(team_name) not like '%huawei%' AND lower(team_name) not like"
            " '%adobe%' )"
        )
    elif customer_type == "enterprise":
        enterprise_statement = (
            """(lower(team_name) like '%huawei%' OR lower(team_name) like '%adobe%' )"""
        )
    else:
        enterprise_statement = "team_id > 0"

    query = sql.SQL(
        """
      SELECT *
      FROM (SELECT
  CASE
    WHEN cum_count.cumulative_count = 1:: numeric THEN 'new customer':: text
    WHEN cum_count.cumulative_count IS NULL THEN 'new customer':: text
    ELSE 'return customer':: text
  END AS first_customer_flag,
  safe_teams.id AS team_id,
  safe_teams.name AS team_name,
  campaigns.has_managed_service,
  campaign_statuses.name AS campaign_status,
  campaigns.name AS campaign_name,
  campaigns.id AS campaign_id,
  campaigns.budget,
  currencies.code AS currency,
  campaigns.started_on,
  date_part('month':: text, date(campaigns.started_on)) AS start_month,
  date_part('year':: text, date(campaigns.started_on)) AS start_year,
  CASE
    WHEN date_part('month':: text, date(campaigns.started_on)) >= 1:: double precision
    AND date_part('month':: text, date(campaigns.started_on)) <= 3:: double precision THEN 'quarter-3':: text
    WHEN date_part('month':: text, date(campaigns.started_on)) >= 4:: double precision
    AND date_part('month':: text, date(campaigns.started_on)) <= 6:: double precision THEN 'quarter-4':: text
    WHEN date_part('month':: text, date(campaigns.started_on)) >= 7:: double precision
    AND date_part('month':: text, date(campaigns.started_on)) <= 9:: double precision THEN 'quarter-1':: text
    ELSE 'quarter-2':: text
  END AS start_quarter,
  campaigns.desired_location
FROM
  campaigns
  LEFT JOIN (SELECT
  sum(count(campaigns.team_id)) OVER (
    PARTITION BY campaigns.team_id
    ORDER BY
      campaigns.id
  ) AS cumulative_count,
  campaigns.id,
  campaigns.team_id
FROM
  campaigns
WHERE
  campaigns.deleted_at IS NULL
  AND campaigns.campaign_status_id <> 1
GROUP BY
  campaigns.id,
  campaigns.team_id) as cum_count ON cum_count.id = campaigns.id
  JOIN (SELECT
  teams.id,
  teams.name
FROM
  teams
WHERE
  (
    teams.type:: text = ANY (
      ARRAY [ 'selfserve':: character varying,
      'portal':: character varying ]:: text [ ]
    )
  )
  AND (
    teams.name:: text <> ALL (
      ARRAY [ 'Vamp Demo':: character varying,
      'JoTestProd':: character varying,
      'Vamp Demo Whitelabel':: character varying,
      'VampVision':: character varying,
      'Digital4ge':: character varying,
      'Yourcompany':: character varying ]:: text [ ]
    )
  )) as safe_teams ON campaigns.team_id = safe_teams.id
  JOIN currencies ON campaigns.currency_id = currencies.id
  JOIN campaign_statuses ON campaigns.campaign_status_id = campaign_statuses.id
  AND campaigns.deleted_at IS NULL) as platform_stats
      WHERE {enterprise_statement}
        AND started_on >= {start_date}
        AND started_on <= {end_date}
    """
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        enterprise_statement=sql.SQL(enterprise_statement),
    )

    data = fetch_from_postgres(query)
    x = conversion(currency_conversions, data["currency"], "AUD")
    data["adjusted_budget"] = pd.to_numeric(data["budget"]) * x
    return data

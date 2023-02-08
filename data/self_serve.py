from psycopg2 import sql

from data.functions import fetch_from_postgres


def fetch_self_serve_campaigns(start_date, end_date, customer_type):

    if customer_type == "selfserve":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(teams.name) not like '%huawei%' AND lower(teams.name) not like"
            " '%adobe%' )"
        )
    elif customer_type == "enterprise":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(teams.name) like '%huawei%' OR lower(teams.name) like '%adobe%')"
        )
    else:
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = "teams.id > 0"
    query = sql.SQL(
        """
      SELECT team_id
        ,'In Draft/Rejected' AS Status
        , count(*)
      FROM campaigns
      WHERE team_id IN (
        SELECT id
        FROM teams
        WHERE type in ({customer_type})
          AND {enterprise_statement}
          AND name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
      )
        AND campaign_status_id IN (
          SELECT id
          FROM campaign_statuses
          WHERE code IN ('draft', 'rejected')
        )
        AND deleted_at is null
        AND start_date  >= {start_date}
        AND start_date <= {end_date}
      GROUP BY team_id

      UNION

      SELECT team_id
        ,'In Moderation' AS Status
        , count(*)
      FROM campaigns
      WHERE team_id IN (
        SELECT id
        FROM teams
        WHERE type in ({customer_type})
          AND {enterprise_statement}
          AND name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
      )
        AND campaign_status_id IN (
          SELECT id
          FROM campaign_statuses
          WHERE code IN ('in_review','approval_required')
        )
        AND deleted_at is null
        AND start_date >= {start_date}
        AND start_date <= {end_date}
      GROUP BY team_id

      UNION

      SELECT team_id
        ,'Live' AS Status
        , count(*)
      FROM campaigns
      WHERE team_id IN (
        SELECT id
        FROM teams
        WHERE type in ({customer_type})
          AND {enterprise_statement}
          AND name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
      )
        AND campaign_status_id IN (
          SELECT id
          FROM campaign_statuses
          WHERE code IN ('ready_for_shortlisting', 'ready_for_approval','active')
        )
        AND deleted_at is null
        AND start_date  >= {start_date}
        AND start_date <= {end_date}
      GROUP BY team_id

      UNION

      SELECT team_id
        , 'Complete' AS Status
        , count(*)
      FROM campaigns
      WHERE team_id IN (
        SELECT id
        FROM teams
        WHERE type in ({customer_type})
          AND {enterprise_statement}
          AND name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
      )
        AND deleted_at is null
        AND start_date >= {start_date}
        AND start_date <= {end_date}
        AND campaign_status_id IN (SELECT id FROM campaign_statuses WHERE code IN ('fulfilled', 'paid'))
      GROUP BY team_id

      UNION

      SELECT team_id
        ,'Deleted' AS Status
        , count(*)
      FROM campaigns
      WHERE team_id IN (
        SELECT id
        FROM teams
        WHERE type in ({customer_type})
          AND {enterprise_statement}
          AND name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
      )
        AND deleted_at is not null
        AND start_date >= {start_date}
        AND start_date <= {end_date}
      GROUP BY team_id
    """
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        customer_type=sql.SQL(",").join(map(sql.Literal, customer_type_value)),
        enterprise_statement=sql.SQL(enterprise_statement),
    )
    data = fetch_from_postgres(query)
    return data


def fetch_self_serve_campaigns_full(start_date, end_date, customer_type):
    if customer_type == "selfserve":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(teams.name) not like '%huawei%' AND lower(teams.name) not like"
            " '%adobe%' )"
        )
    elif customer_type == "enterprise":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(teams.name) like '%huawei%' OR lower(teams.name) like '%adobe%')"
        )
    else:
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = "teams.id > 0"
    query = sql.SQL(
        """
      SELECT c.id as campaign_id
        , c.team_id
        , c.name as campaign_name
        , budget
        , cur.code as currency
        , DATE(start_date) as start_date
        , DATE(end_date) as end_date
        , ss.name as team_name
        , has_managed_service
        , cs.name as status
        , desired_location
      FROM campaigns as c
      inner join (
        SELECT id
          , name
        FROM teams
        WHERE type in ({customer_type})
          AND {enterprise_statement}
          AND name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
      ) as ss on c.team_id = ss.id
      inner join (select id, code from currencies) as cur on c.currency_id = cur.id
      inner join (select id, name from campaign_statuses) as cs on c.campaign_status_id = cs.id
        AND deleted_at is null
        AND start_date >= {start_date}
        AND start_date <= {end_date}
      ORDER BY start_date desc
    """
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        customer_type=sql.SQL(",").join(map(sql.Literal, customer_type_value)),
        enterprise_statement=sql.SQL(enterprise_statement),
    )
    data = fetch_from_postgres(query)
    return data


def fetch_self_serve_new_customer(start_date, end_date, customer_type):
    if customer_type == "selfserve":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(teams.name) not like '%huawei%' AND lower(teams.name) not like"
            " '%adobe%' )"
        )
    elif customer_type == "enterprise":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(teams.name) like '%huawei%' OR lower(teams.name) like '%adobe%')"
        )
    else:
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = "teams.id > 0"
    query = sql.SQL(
        """SELECT cc.team_name, count(*)
    from campaigns inner join
    (SELECT c.team_id, ss.name as team_name
FROM campaigns as c
left join (SELECT sum(count(team_id)) OVER (PARTITION BY team_id ORDER BY id) as cumulative_count,  id, team_id
from campaigns
WHERE deleted_at is null
AND campaign_status_id != 1
AND start_date is NOT NULL
GROUP BY id, team_id) as cum_count on cum_count.id = c.id
inner join (SELECT id, name FROM teams WHERE type in ({customer_type}) AND {enterprise_statement} AND name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge',
'Yourcompany')) as ss on c.team_id = ss.id
WHERE deleted_at is null
AND start_date >= {start_date}
AND start_date <= {end_date}
AND cum_count.cumulative_count = 1) as cc on cc.team_id = campaigns.team_id
WHERE deleted_at is null
AND campaign_status_id != 1
GROUP BY cc.team_name"""
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        customer_type=sql.SQL(",").join(map(sql.Literal, customer_type_value)),
        enterprise_statement=sql.SQL(enterprise_statement),
    )
    data = fetch_from_postgres(query)
    return data


def retrieve_budget_tracking_campaigns(start_date, end_date, customer_type):
    if customer_type == "selfserve":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(teams.name) not like '%huawei%' AND lower(teams.name) not like"
            " '%adobe%' )"
        )
    elif customer_type == "enterprise":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(teams.name) like '%huawei%' OR lower(teams.name) like '%adobe%')"
        )
    else:
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = "teams.id > 0"
    query = sql.SQL(
        """
      SELECT CASE
          WHEN cum_count.cumulative_count = 1
            THEN 'new customer'
          WHEN cum_count.cumulative_count is null
            THEN 'new customer'
          ELSE 'return customer'
        END as first_customer_flag
        , ss.name as team_name
        , has_managed_service
        , cs.name as campaign_status
        , c.name as campaign_name
        , c.id as campaign_id
        , budget
        , cur.code as currency
        , DATE(start_date) as start_date
        , DATE(end_date) as end_date
      FROM campaigns as c
      left join (
        SELECT sum(count(team_id)) OVER (PARTITION BY team_id ORDER BY id) as cumulative_count
          , id
          , team_id
        from campaigns
        WHERE deleted_at is null
          AND campaign_status_id != 1
        GROUP BY id, team_id
      ) as cum_count on cum_count.id = c.id
      inner join (
        SELECT id
          , name
        FROM teams
        WHERE type in ({customer_type})
        AND {enterprise_statement}
        AND name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
      ) as ss on c.team_id = ss.id
      inner join (select id, code from currencies) as cur on c.currency_id = cur.id
      inner join (select id, name from campaign_statuses) as cs on c.campaign_status_id = cs.id
        AND deleted_at is null
        AND start_date >= {start_date}
        AND start_date <= {end_date}
      ORDER BY start_date desc
    """
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        customer_type=sql.SQL(",").join(map(sql.Literal, customer_type_value)),
        enterprise_statement=sql.SQL(enterprise_statement),
    )
    data = fetch_from_postgres(query)
    return data


def fetch_marketing_downloads(start_date, end_date):
    query = sql.SQL(
        """
    (select name, email, 'QUOTE' as tool
from quotes
where email not like '%@vamp.me%'
AND inserted_at >= {start_date}
AND inserted_at<= {end_date})
union
(select name, email, 'CAST' as tool
from samples
where email not like '%@vamp.me%'
AND inserted_at >= {start_date}
AND inserted_at<= {end_date})
"""
    ).format(start_date=sql.Literal(start_date), end_date=sql.Literal(end_date))
    data = fetch_from_postgres(query)
    return data


def fetch_self_serve_life_cycle(start_date, end_date, customer_type):
    if customer_type == "selfserve":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(teams.name) not like '%huawei%' AND lower(teams.name) not like"
            " '%adobe%' )"
        )
    elif customer_type == "enterprise":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(teams.name) like '%huawei%' OR lower(teams.name) like '%adobe%')"
        )
    else:
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = "teams.id > 0"
    query = sql.SQL(
        """SELECT cc.team_name, min(start_date), max(start_date)
    from campaigns inner join
    (SELECT c.team_id, ss.name as team_name
FROM campaigns as c
left join (SELECT sum(count(team_id)) OVER (PARTITION BY team_id ORDER BY id) as cumulative_count,  id, team_id
from campaigns
WHERE deleted_at is null
AND campaign_status_id != 1
AND start_date is not null
GROUP BY id, team_id) as cum_count on cum_count.id = c.id
inner join (SELECT id, name FROM teams WHERE type in ({customer_type}) AND {enterprise_statement} AND name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge',
'Yourcompany')) as ss on c.team_id = ss.id
AND deleted_at is null
AND start_date >= {start_date}
AND start_date <= {end_date}
AND cum_count.cumulative_count = 1) as cc on cc.team_id = campaigns.team_id
WHERE deleted_at is null
AND campaign_status_id != 1
GROUP BY cc.team_name"""
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        customer_type=sql.SQL(",").join(map(sql.Literal, customer_type_value)),
        enterprise_statement=sql.SQL(enterprise_statement),
    )
    data = fetch_from_postgres(query)
    data.to_csv("test.csv")
    return data

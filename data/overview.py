import pandas as pd
from psycopg2 import sql

from data.functions import fetch_from_postgres


# overview
def fetch_deliverables_by_campaign(start_date, end_date, customer_type):
    if customer_type == "all":
        customer_type_value = ["vamp", "selfserve", "portal"]
        enterprise_statement = "t.id > 0"
    elif customer_type == "selfserve":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(t.name) not like '%huawei%' AND lower(t.name) not like '%adobe%' )"
        )
    elif customer_type == "enterprise":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(t.name) like '%huawei%' OR lower(t.name) like '%adobe%' )"
        )
    else:
        customer_type_value = ["vamp"]
        enterprise_statement = (
            "(lower(t.name) not like '%huawei%' AND lower(t.name) not like '%adobe%' )"
        )

    query = sql.SQL(
        """
      SELECT campaign_id
        , count(*) as deliverables_count
      from deliverables as d
      inner join (
        select id
          , campaign_id
        from briefs
      ) as b on b.id = d.brief_id
      inner join campaigns as c on b.campaign_id = c.id
      inner join teams as t on t.id = c.team_id
      WHERE campaign_id in (
        select id
        from campaigns
        where started_on >= {start_date}
          AND started_on <= {end_date}
          AND (
            desired_age_ranges<>'100-999'
            OR desired_age_ranges IS NULL
          )
      )
        AND deliverable_status_id is not null
        AND c.deleted_at is null
        AND t.type in ({customer_type})
        AND {enterprise_statement}
        AND t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
        group by campaign_id
    """
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        customer_type=sql.SQL(",").join(map(sql.Literal, customer_type_value)),
        enterprise_statement=sql.SQL(enterprise_statement),
    )
    data = fetch_from_postgres(query)
    return data


# overview
def fetch_brief_times_by_campaign(start_date, end_date, customer_type):
    if customer_type == "all":
        customer_type_value = ["vamp", "selfserve", "portal"]
        enterprise_statement = "t.id > 0"
    elif customer_type == "selfserve":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(t.name) not like '%huawei%' AND lower(t.name) not like '%adobe%' )"
        )
    elif customer_type == "enterprise":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(t.name) like '%huawei%' OR lower(t.name) like '%adobe%' )"
        )
    else:
        customer_type_value = ["vamp"]
        enterprise_statement = (
            "(lower(t.name) not like '%huawei%' AND lower(t.name) not like '%adobe%' )"
        )

    query = sql.SQL(
        """
      SELECT c.id
        , c.inserted_at
        , b.sent_date
        , DATE_PART('day', b.sent_date - c.inserted_at) as days_in_draft
      from campaigns as c
      inner join (
        select campaign_id
          , min(inserted_at) as sent_date
        from briefs
        group by campaign_id
      ) as b on b.campaign_id = c.id
      inner join teams as t on t.id = c.team_id
      WHERE started_on >= {start_date} AND started_on <= {end_date}
        AND c.deleted_at is null
        AND t.type in ({customer_type})
        AND {enterprise_statement} AND t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
        AND (
          desired_age_ranges<>'100-999'
          OR desired_age_ranges IS NULL
        )
    """
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        customer_type=sql.SQL(",").join(map(sql.Literal, customer_type_value)),
        enterprise_statement=sql.SQL(enterprise_statement),
    )
    data = fetch_from_postgres(query)
    return data


def fetch_talent_by_campaign(start_date, end_date, customer_type):
    if customer_type == "all":
        customer_type_value = ["vamp", "selfserve", "portal"]
        enterprise_statement = "t.id > 0"
    elif customer_type == "selfserve":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(t.name) not like '%huawei%' AND lower(t.name) not like '%adobe%' )"
        )
    elif customer_type == "enterprise":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(t.name) like '%huawei%' OR lower(t.name) like '%adobe%' )"
        )
    else:
        customer_type_value = ["vamp"]
        enterprise_statement = (
            "(lower(t.name) not like '%huawei%' AND lower(t.name) not like '%adobe%' )"
        )

    query = sql.SQL(
        """
      SELECT campaign_id, count(*) as talent_count
      from briefs
      inner join campaigns as c on briefs.campaign_id = c.id
      inner join teams as t on t.id = c.team_id
      WHERE campaign_id in (
        select id
        from campaigns
        where started_on >= {start_date}
        AND started_on <= {end_date}
        AND (
          desired_age_ranges<>'100-999'
          OR desired_age_ranges IS NULL
        )
      )
        AND brief_status_id in (6,8,11,12,13)
        AND c.deleted_at is null
        AND t.type in ({customer_type})
        AND {enterprise_statement}
        AND t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
      group by campaign_id
    """
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        customer_type=sql.SQL(",").join(map(sql.Literal, customer_type_value)),
        enterprise_statement=sql.SQL(enterprise_statement),
    )
    data = fetch_from_postgres(query)
    return data


def fetch_deliverable_types_by_campaign(start_date, end_date, customer_type):
    if customer_type == "all":
        customer_type_value = ["vamp", "selfserve", "portal"]
        enterprise_statement = "t.id > 0"
    elif customer_type == "selfserve":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(t.name) not like '%huawei%' AND lower(t.name) not like '%adobe%' )"
        )
    elif customer_type == "enterprise":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(t.name) like '%huawei%' OR lower(t.name) like '%adobe%' )"
        )
    else:
        customer_type_value = ["vamp"]
        enterprise_statement = (
            "(lower(t.name) not like '%huawei%' AND lower(t.name) not like '%adobe%' )"
        )

    query = sql.SQL(
        """
      SELECT dt.name as deliverable_type
        , count(*) as deliverables_count
      from deliverables as d
      inner join (
        select id
          , campaign_id
        from briefs
      ) as b on b.id = d.brief_id
      inner join campaigns as c on b.campaign_id = c.id
      inner join teams as t on t.id = c.team_id
      inner join deliverable_types as dt on d.deliverable_type_id = dt.id
      WHERE campaign_id in (
        select id
        from campaigns
        where started_on >= {start_date}
          AND started_on <= {end_date}
          AND (
            desired_age_ranges<>'100-999'
            OR desired_age_ranges IS NULL
          )
      )
        AND deliverable_status_id is not null
        AND dt.name not in ('Product Purchase','Product Distribution')

        AND c.deleted_at is null
        AND t.type in ({customer_type})
        AND {enterprise_statement}
        AND t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge','Yourcompany')
      group by dt.name
    """
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        customer_type=sql.SQL(",").join(map(sql.Literal, customer_type_value)),
        enterprise_statement=sql.SQL(enterprise_statement),
    )
    data = fetch_from_postgres(query)
    return data


def fetch_campaigns(start_date, end_date, customer_type):
    if customer_type == "all":
        customer_type_value = ["vamp", "selfserve", "portal"]
        enterprise_statement = "t.id > 0"
    elif customer_type == "selfserve":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(t.name) not like '%huawei%' AND lower(t.name) not like '%adobe%' )"
        )
    elif customer_type == "enterprise":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(t.name) like '%huawei%' OR lower(t.name) like '%adobe%' )"
        )
    else:
        customer_type_value = ["vamp"]
        enterprise_statement = (
            "(lower(t.name) not like '%huawei%' AND lower(t.name) not like '%adobe%' )"
        )

    query = sql.SQL(
        """
      SELECT desired_location
    	FROM campaigns as c
      inner join teams as t on t.id = c.team_id
    	WHERE started_on >= {start_date} AND started_on <= {end_date}
        AND t.type in ({customer_type})
        AND c.deleted_at is null
        AND {enterprise_statement}
        AND t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge','Yourcompany')
        AND (
          desired_age_ranges<>'100-999'
        	OR desired_age_ranges IS NULL
        )
    """
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        customer_type=sql.SQL(",").join(map(sql.Literal, customer_type_value)),
        enterprise_statement=sql.SQL(enterprise_statement),
    )
    data = fetch_from_postgres(query)
    local_dict = data["desired_location"].tolist()
    l = [i.split(",") for i in local_dict if i is not None]
    counts = (
        pd.DataFrame({"locations": [item for sublist in l for item in sublist]})[
            "locations"
        ]
        .value_counts()
        .reset_index()
    )
    data = fetch_from_postgres(
        "".join(
            [
                """
                    SELECT
                        code,
                        sub_code,
                        name AS country
                    FROM
                        countries
                    WHERE
                        active = TRUE """
            ]
        )
    )
    counts = counts.merge(data, right_on="code", left_on="index", how="right")
    counts["locations"] = counts["locations"].fillna(0)

    return counts


def fetch_campaigns_status(start_date, end_date, customer_type):
    if customer_type == "all":
        customer_type_value = ["vamp", "selfserve", "portal"]
        enterprise_statement = "t.id > 0"
    elif customer_type == "selfserve":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(t.name) not like '%huawei%' AND lower(t.name) not like '%adobe%' )"
        )
    elif customer_type == "enterprise":
        customer_type_value = ["selfserve", "portal"]
        enterprise_statement = (
            "(lower(t.name) like '%huawei%' OR lower(t.name) like '%adobe%' )"
        )
    else:
        customer_type_value = ["vamp"]
        enterprise_statement = (
            "(lower(t.name) not like '%huawei%' AND lower(t.name) not like '%adobe%' )"
        )

    query = sql.SQL(
        """
      SELECT count(*) as campaign_count
        , cs.name as campaign_status
      from campaigns as c
      inner join campaign_statuses as cs on c.campaign_status_id = cs.id
      inner join teams as t on c.team_id = t.id
      WHERE started_on >= {start_date}
        AND started_on <= {end_date}
        AND (
          desired_age_ranges<>'100-999'
          OR desired_age_ranges IS NULL
        )
        AND c.deleted_at is null
        AND t.type in ({customer_type})
        AND {enterprise_statement}
        AND t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
        GROUP BY cs.name
    """
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        customer_type=sql.SQL(",").join(map(sql.Literal, customer_type_value)),
        enterprise_statement=sql.SQL(enterprise_statement),
    )
    data = fetch_from_postgres(query)
    return data


def fetch_self_serve_customers(start_date, end_date):
    query = sql.SQL(
        """
      SELECT  count(*) as self_serve
      from teams
      where teams.id in (
        select team_id
        from campaigns
        WHERE started_on >= {start_date}
        AND started_on <= {end_date}
        AND deleted_at is null
        AND (
          desired_age_ranges<>'100-999'
          OR desired_age_ranges IS NULL
        )
        AND team_id in (
          select id
          from teams
          where type in ('selfserve', 'portal')
        )
      )
    """
    ).format(start_date=sql.Literal(start_date), end_date=sql.Literal(end_date))
    data = fetch_from_postgres(query)
    return data

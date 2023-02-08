import pandas as pd
from psycopg2 import sql

from data.fixer import conversion
from data.functions import currency_conversions, fetch_from_postgres


def fetch_booked_campaign_revenue(
    start_date, end_date, currency, customer_type, location
):

    if location is None:
        location_statement = "campaigns.id > 0"
    elif len(location) == 0:
        location_statement = "campaigns.id > 0"
    else:
        locations = [str(i) for i in location]
        string = " AND ".join(
            [
                "".join(
                    [
                        "desired_location LIKE (SELECT concat('%',code,'%') FROM"
                        " countries WHERE id IN (",
                        i,
                        ") )",
                    ]
                )
                for i in locations
            ]
        )
        location_statement = string

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
        SELECT sum(campaigns.budget) as budget
            , 'Draft' as campaign_status
            , DATE_PART('month', started_on) as start_month
            , DATE_PART('year',started_on) as start_year
            , currencies.code as currency_code
            , has_managed_service
        from campaigns
        inner join currencies on campaigns.currency_id = currencies.id
        inner join teams as t on t.id = campaigns.team_id
        WHERE campaign_status_id IN (
            SELECT id
            FROM campaign_statuses
            WHERE code IN ('draft', 'rejected')
        )
            AND started_on >= {start_date}
            AND started_on <= {end_date}
            AND (
                campaigns.desired_age_ranges <> '100-999'
                OR campaigns.desired_age_ranges IS NULL
            )
            AND deleted_at is null
            AND t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
            AND t.type in ({customer_type})
            AND {location_statement}
            AND {enterprise_statement}
        GROUP BY DATE_PART('month', started_on), DATE_PART('year',started_on),currencies.code , has_managed_service

        UNION

        SELECT sum(campaigns.budget) as budget
            , 'Active' as campaign_status
            , DATE_PART('month', started_on) as start_month
            , DATE_PART('year',started_on) as start_year
            , currencies.code as currency_code
            , has_managed_service
        from campaigns
        inner join currencies on campaigns.currency_id = currencies.id
        inner join teams as t on t.id = campaigns.team_id
        WHERE campaign_status_id in (
            SELECT id
            FROM campaign_statuses
            WHERE code IN ('in_review','approval_required','ready_for_shortlisting', 'ready_for_approval','active')
        )
            AND started_on >= {start_date}
            AND started_on <= {end_date}
            AND (
                campaigns.desired_age_ranges <> '100-999'
                OR campaigns.desired_age_ranges IS NULL
            )
            AND deleted_at is null
            AND t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
            AND t.type in ({customer_type})
            AND {location_statement}
            AND {enterprise_statement}
        GROUP BY DATE_PART('month', started_on), DATE_PART('year',started_on),currencies.code , has_managed_service

        UNION

        SELECT sum(campaigns.budget) as budget
            ,'Complete' as campaign_status
            , DATE_PART('month', started_on) as start_month
            , DATE_PART('year',started_on) as start_year, currencies.code as currency_code, has_managed_service from campaigns
        inner join currencies on campaigns.currency_id = currencies.id
        inner join teams as t on t.id = campaigns.team_id
        WHERE campaign_status_id IN (
            SELECT id
            FROM campaign_statuses
            WHERE code IN ('fulfilled', 'paid')
        )
            AND started_on <= now()
            AND started_on >= {start_date}
            AND started_on <= {end_date}
            AND (
                campaigns.desired_age_ranges <> '100-999'
                OR campaigns.desired_age_ranges IS NULL
            )
            AND deleted_at is null
            AND t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
            AND t.type in ({customer_type})
            AND {location_statement}
            AND {enterprise_statement}
        GROUP BY DATE_PART('month', started_on), DATE_PART('year',started_on),currencies.code, has_managed_service
    """
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        customer_type=sql.SQL(",").join(map(sql.Literal, customer_type_value)),
        location_statement=sql.SQL(location_statement),
        enterprise_statement=sql.SQL(enterprise_statement),
    )
    try:
        data = fetch_from_postgres(query)
        x = conversion(currency_conversions, data["currency_code"], currency)
        data["adjusted_budget"] = pd.to_numeric(data["budget"]) * x
        if data.empty:
            data = pd.DataFrame(
                {
                    "adjusted_budget": 0,
                    "budget": 0,
                    "campaign_status": "Draft",
                    "start_month": 7,
                    "start_year": 2020,
                    "currency_code": currency,
                    "has_managed_service": False,
                },
                index=[0],
            )
    except Exception as e:
        print(e)
        data = pd.DataFrame(
            {
                "adjusted_budget": 0,
                "budget": 0,
                "campaign_status": "Draft",
                "start_month": 7,
                "start_year": 2020,
                "currency_code": currency,
                "has_managed_service": False,
            },
            index=[0],
        )
    return data


def fetch_financials_campaigns(
    start_date, end_date, currency, customer_type, location, management_input
):
    if management_input != "all":
        management_statement = "c.has_managed_service = " + str(management_input)
    else:
        management_statement = "c.has_managed_service in ('true','false')"

    if location is None:
        location_statement = "c.id > 0"
    elif len(location) == 0:
        location_statement = "c.id > 0"
    else:
        locations = [str(i) for i in location]
        string = " AND ".join(
            [
                "".join(
                    [
                        "desired_location LIKE (SELECT concat('%',code,'%') FROM"
                        " countries WHERE id IN (",
                        i,
                        ") )",
                    ]
                )
                for i in locations
            ]
        )
        location_statement = string

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
            , c.started_on
            , c.end_date
            , c.budget
            , cumulative_campaigns
            , t.name AS team_name
            , t.type AS team_type
            , c.desired_location as desired_location
            , cur.code AS currency
            , cs.code AS campaign_status
        FROM (
            SELECT id
              , team_id
              , desired_age_ranges
              , started_on
              , end_date
              , campaign_status_id
              , budget
              , currency_id
              , desired_location
              , has_managed_service
              , count(id) OVER (PARTITION BY team_id ORDER BY id) AS cumulative_campaigns
            FROM campaigns
            WHERE (
                desired_age_ranges <> '100-999'
                OR desired_age_ranges IS NULL
            )
                AND deleted_at is null
            ORDER BY team_id desc, id
        ) AS c
        INNER JOIN teams AS t ON c.team_id = t.id
        INNER JOIN currencies AS cur ON cur.id = c.currency_id
        INNER JOIN campaign_statuses AS cs ON cs.id = c.campaign_status_id
        WHERE t.type in ('selfserve','portal','vamp')
            AND t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
            AND started_on >= {start_date}
            AND started_on <= {end_date}
            AND t.type in ({customer_type})
            AND {location_statement}
            AND {management_statement}
            AND {enterprise_statement}
    """
    ).format(
        start_date=sql.Literal(start_date),
        end_date=sql.Literal(end_date),
        customer_type=sql.SQL(",").join(map(sql.Literal, customer_type_value)),
        location_statement=sql.SQL(location_statement),
        management_statement=sql.SQL(management_statement),
        enterprise_statement=sql.SQL(enterprise_statement),
    )
    try:
        data = fetch_from_postgres(query)
        data["adjusted_budget"] = pd.to_numeric(data["budget"]) * conversion(
            currency_conversions, data["currency"], currency
        )
    except Exception as e:
        print(e)
        data = pd.DataFrame(
            {
                "id": 0,
                "started_on": start_date,
                "end_date": end_date,
                "budget": 0,
                "adjusted_budget": 0,
                "cumulative_campaigns": 0,
                "team_name": "none",
                "team_type": customer_type,
                "desired_location": "NA",
                "currency": currency,
                "campaign_status": "Draft",
            },
            index=[0],
        )

    if data.empty:
        data = pd.DataFrame(
            {
                "id": 0,
                "started_on": start_date,
                "end_date": end_date,
                "budget": 0,
                "adjusted_budget": 0,
                "cumulative_campaigns": 0,
                "team_name": "none",
                "team_type": customer_type,
                "desired_location": "NA",
                "currency": currency,
                "campaign_status": "Draft",
            },
            index=[0],
        )
    return data

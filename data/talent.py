from data.functions import fetch_from_bigquery


def fetch_new_talent_data(start_date, end_date, location):
    if location == None:
        location_statement = "influencer_id > 0"
    elif len(location) == 0:
        location_statement = "influencer_id > 0"
    else:
        if len(location) > 1:
            string = ",".join([str(i) for i in location])
        else:
            string = str(location[0])
        location_statement = "".join(["country_id in (", string, ")"])

    query = """SELECT status, count(*) as count
FROM `vamp-dw-prod.fact_servalan_views.talent_analysis`
WHERE DATE(inserted_at) >= DATE("{start_date}")
AND  DATE(inserted_at) <= DATE("{end_date}")
AND {location_statement}
GROUP BY status
;""".format(
        start_date=start_date,
        end_date=end_date,
        location_statement=location_statement,
    )

    data = fetch_from_bigquery(query)
    return data


def fetch_new_talent_location_data(start_date, end_date, location):
    if location == None:
        location_statement = (
            "country_id in (SELECT id from source_servalan_public.countries)"
        )
    elif len(location) == 0:
        location_statement = (
            "country_id in (SELECT id from source_servalan_public.countries)"
        )
    else:
        if len(location) > 1:
            string = ",".join([str(i) for i in location])
        else:
            string = str(location[0])
        location_statement = "".join(["country_id in (", string, ")"])

    query = """SELECT status, country_code, country, sub_region, count(*) as count
FROM `vamp-dw-prod.fact_servalan_views.talent_analysis`
WHERE DATE(inserted_at)>= DATE("{start_date}")
AND  DATE(inserted_at) <= DATE("{end_date}")
AND {location_statement}
GROUP BY 1,2,3,4
""".format(
        start_date=start_date,
        end_date=end_date,
        location_statement=location_statement,
    )

    data = fetch_from_bigquery(query)
    return data


def fetch_new_talent_campaign_application(start_date, end_date, location):
    if location == None:
        location_statement = "influencer_id > 0"
    elif len(location) == 0:
        location_statement = "influencer_id > 0"
    else:
        if len(location) > 1:
            string = ",".join([str(i) for i in location])
        else:
            string = str(location[0])
        location_statement = "".join(["country_id in (", string, ")"])

    query = """SELECT count(*) as count  from `vamp-dw-prod.fact_servalan_views.talent_analysis`
        WHERE DATE(inserted_at) >= DATE("{start_date}")
		AND  DATE(inserted_at) <= DATE("{end_date}")
    	AND {location_statement}
        AND applications > 0
        AND applications is not NULL
        """.format(
        start_date=start_date,
        end_date=end_date,
        location_statement=location_statement,
    )
    data = fetch_from_bigquery(query)
    return data


def fetch_new_talent_campaign_application_chart(start_date, end_date, location):
    if location == None:
        location_statement = "influencer_id > 0"
    elif len(location) == 0:
        location_statement = "influencer_id > 0"
    else:
        if len(location) > 1:
            string = ",".join([str(i) for i in location])
        else:
            string = str(location[0])
        location_statement = "".join(["country_id in (", string, ")"])

    query = """SELECT DISTINCT influencer_id, applications from `vamp-dw-prod.fact_servalan_views.talent_analysis`
    	where DATE(inserted_at)>= DATE("{start_date}")
		AND  DATE(inserted_at)<= DATE("{end_date}")
		AND {location_statement}
        AND applications is not NULL
        """.format(
        start_date=start_date,
        end_date=end_date,
        location_statement=location_statement,
    )
    print(query)
    data = fetch_from_bigquery(query)
    return data


def fetch_brief_response(start_date, end_date, location):
    if location == None:
        location_statement = "sent > 0"
    elif len(location) == 0:
        location_statement = "sent > 0"
    else:
        if len(location) > 1:
            string = "(" + ",".join([str(i) for i in location]) + ")"
        else:
            string = str(location[0])
        location_statement = "".join([" country_id in (", string, ")"])

    query = """SELECT sub_region, sum(sent) as sent, sum(notifications) as notifications, sum(active) as active, sum(viewed) as viewed, sum(applied) as applied, sum(selected) as selected
    FROM `vamp-dw-prod.fact_servalan_views.brief_response_by_country`
    where DATE(inserted_at) >= DATE("{start_date}")
    AND DATE(inserted_at) <= DATE("{end_date}")
    AND {location_statement}
    GROUP BY sub_region
        """.format(
        start_date=str(start_date),
        end_date=str(end_date),
        location_statement=location_statement,
    )
    print(query)
    data = fetch_from_bigquery(query)
    return data

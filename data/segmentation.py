import re

from psycopg2 import sql

from data.functions import fetch_from_postgres


def fetch_brief_participation(influencers=[]):
    query = """
        SELECT briefs.influencer_id
            , SUM((
                CASE
                    WHEN b_status.code IN ('approved',
                                          'fulfilled',
                                          'completed',
                                          'media_uploaded',
                                          'media_accepted')
                        THEN 1
                    ELSE 0
                END
            )) AS participation,
            COUNT(briefs.id) AS applications
        FROM briefs
        JOIN brief_statuses b_status ON b_status.id = briefs.brief_status_id
        WHERE b_status.code IN ('invitation_accepted',
                                'shortlisted',
                                'approved',
                                'rejected',
                                'fulfilled',
                                'completed',
                                'media_uploaded',
                                'media_accepted',
                                'processing_payment')
        AND briefs.influencer_id IN ({})
        GROUP BY influencer_id
    """.format(
        ", ".join(map(str, influencers))
    )

    data = fetch_from_postgres(query)
    return data


def fetch_segmentation_data(
    location,
    gender,
    categories,
    status,
    age,
    local_audience,
    followers,
    er,
    activity,
    platforms,
):
    # Age
    age_dict = {
        1: {"min_val": 0, "max_val": 17.99},
        2: {"min_val": 18, "max_val": 24.99},
        3: {"min_val": 25, "max_val": 34.99},
        4: {"min_val": 35, "max_val": 99.99},
    }

    age_vals = [age_dict[age[0]]["min_val"], age_dict[age[1]]["max_val"]]
    age_statement = "".join(
        [
            "EXTRACT(YEAR from AGE(date_of_birth)) >= ",
            str(age_vals[0]),
            " AND EXTRACT(YEAR from AGE(date_of_birth)) < ",
            str(age_vals[1]),
        ]
    )

    followers_dict = {
        1: {"min_val": 0, "max_val": 9999},
        2: {"min_val": 10000, "max_val": 24999},
        3: {"min_val": 25000, "max_val": 49999},
        4: {"min_val": 50000, "max_val": 99999},
        5: {"min_val": 100000, "max_val": 100000000000},
    }

    follower_vals = [
        followers_dict[followers[0]]["min_val"],
        followers_dict[followers[1]]["max_val"],
    ]
    followers_statement = "".join(
        [
            "followers_count >= ",
            str(follower_vals[0]),
            " AND followers_count <= ",
            str(follower_vals[1]),
        ]
    )

    if (local_audience[0] == 0) & (local_audience[1] == 100):
        local_audience_statement = "REMOVE"
    else:
        local_audience_statement = "".join(
            [
                "local_audience >= ",
                str(local_audience[0] / 100),
                " AND local_audience <= ",
                str(local_audience[1] / 100),
            ]
        )

    if (er[0] == 0) & (er[1] == 10):
        er_statement = "REMOVE"
    else:
        er_statement = "".join(
            [
                "engagement_rate >= ",
                str(er[0] / 100),
                " AND engagement_rate <= ",
                str(er[1] / 100),
            ]
        )

    if location == None:
        location_statement = "REMOVE"
    elif len(location) == 0:
        location_statement = "REMOVE"
    else:
        if len(location) > 1:
            string = ",".join([str(i) for i in location])
        else:
            string = str(location[0])
        location_statement = "".join(["country_id in (", string, ")"])

    if gender == None:
        gender_statement = "REMOVE"
    elif (len(gender)) == 0:
        gender_statement = "REMOVE"
    else:
        strings = ["".join(["'", i, "'"]) for i in gender]
        string = ",".join(strings)
        gender_statement = "".join(["gender in (", string, ")"])

    if categories == None:
        categories_statement = "REMOVE"
    elif (len(categories)) == 0:
        categories_statement = "REMOVE"
    else:
        strings = ["".join(["'", i, "'"]) for i in categories]
        string = ",".join(strings).lower()
        categories_statement = "".join(
            [
                "si.influencer_id in (select influencer_id from influencer_categories"
                " where category_id in (select id from categories where code in (",
                string,
                ")))",
            ]
        )

    if status == None:
        status_statement = "REMOVE"

    elif len(status) == 0:
        status_statement = "REMOVE"
    else:
        if len(status) > 1:
            string = ",".join([str(i) for i in status])

        else:
            string = str(status[0])
        status_statement = "".join(["si.influencer_status_id in (", string, ")"])

    if activity == "active":
        activity_statement = "si.last_active >= NOW() - INTERVAL '31 days'"
    elif activity == "inactive":
        activity_statement = "si.last_active < NOW() - INTERVAL '31 days'"
    else:
        activity_statement = "REMOVE"

    if platforms is not None and len(platforms) > 0:
        platform_statement = "si.platform IN ('{}')".format("', '".join(platforms))
        print(platform_statement)
    else:
        platform_statement = "REMOVE"

    where_statement = " AND ".join(
        [
            er_statement,
            local_audience_statement,
            age_statement,
            location_statement,
            gender_statement,
            categories_statement,
            status_statement,
            activity_statement,
            platform_statement,
            followers_statement,
        ]
    )
    where_statement = re.sub("REMOVE AND", "", where_statement)

    query = sql.SQL(
        """
        SELECT last_active
            , is_business
            , gender
            , date_of_birth
            , EXTRACT(YEAR from AGE(date_of_birth)) as "age"
            , influencer_status_id
            , influencer_status_name
            , followers_count
            , follows_count
            , media_count
            , engagement_rate
            , engagement_rate * followers_count as engagements
            , country
            , local_audience
            , local_audience*followers_count as local_audience_value
            , country_sub_code
            , vector
            , si.influencer_id
            , si.full_name
            , si.email
            , si.postcode
            , si.handle
            , si.platform
            , si.inserted_at

        FROM (
            SELECT s.id AS social_account_id
                , is_business
                , s.influencer_id
                , i.full_name
                , i.email
                , i.postcode
                , i.inserted_at
                , s.handle
                , gender
                , date_of_birth
                , influencer_status_id
                , i_status.name AS influencer_status_name
                , followers_count
                , engagement_rate
                , media_count
                , follows_count
                , last_active
                , i.vector
                , sp.code AS platform
            FROM influencers AS i
            INNER JOIN social_accounts AS s ON i.id = s.influencer_id
            LEFT JOIN influencer_statuses i_status ON i_status.id = i.influencer_status_id
            LEFT JOIN social_platforms sp ON sp.id = s.social_platform_id
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
        ) AS aud_insight ON (aud_insight.social_account_id, aud_insight.country_code) = (si.social_account_id, country.country_code)
        WHERE {where_statement}
    """
    ).format(where_statement=sql.SQL(where_statement))

    print(query)

    data = fetch_from_postgres(query)
    return data

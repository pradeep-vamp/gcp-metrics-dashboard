import os
import re

import boto3
import pandas as pd
from psycopg2 import sql

from data.functions import fetch_from_postgres

aws_key = os.getenv("AWS_ACCESS_KEY")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")

"""
 data/pandacop.py

 @ticket:   https://vampdash.atlassian.net/browse/DAS-8026
 @date:     2021-06-21
 @auth:     Mark Brackenrig < mark@vamp.me >

 @desc:
 This file is used to build queries for the fraud detection page (also known as pandacop).

 TODO:
 1. Find triggered influencers in DB
 2. Find Safe Search influencers
 3. Allow user to suspend influencer

"""


def retrieve_red_cards(location=None, handles=[]):
    """
    Retrieves posts where engagements are greater than reach by at least 10%
    """

    if (location is None) or (len(location) == 0):
        location_statement = sql.SQL("c.id > 0")
    else:
        location_statement = sql.SQL("c.id in ({location_list})").format(
            location_list=sql.SQL(",").join(map(sql.Literal, location))
        )

    query = sql.SQL(
        """
        select
            m.inserted_at as date
            , media_id
            , reach,impressions
            , engagement
            , social_link
            ,likes_count
            ,sa.influencer_id as influencer_id
            , handle
            , c.name as country
        from media_insights as mi
    inner join media as m on m.id = mi.media_id
    inner join social_accounts as sa on sa.influencer_id = m.influencer_id
    inner join influencer_countries as ic on ic.influencer_id = sa.influencer_id
    inner join influencers as i on i.id = sa.influencer_id
    inner join countries as c on c.id = ic.country_id
    where engagement > 1.1*reach AND reach > 30
    AND {location}
    AND sa.social_platform_id = 1
    AND i.influencer_status_id=3"""
    ).format(location=location_statement)

    red_flags = fetch_from_postgres(query)
    red_flags = red_flags.drop_duplicates().reset_index(drop=True)
    red_flags["social_link"] = [re.sub("www.", "", i) for i in red_flags["social_link"]]

    if len(handles) > 0:
        query = sql.SQL(
            """
            SELECT DISTINCT sa.influencer_id as influencer_id
                , handle
                , c.name as country
            FROM social_accounts sa
            join influencer_countries as ic on ic.influencer_id = sa.influencer_id
            join countries as c on c.id = ic.country_id
            WHERE sa.handle IN ({handles})
                AND {location};
        """
        ).format(
            handles=sql.SQL(", ").join(map(sql.Literal, handles)),
            location=location_statement,
        )

        add_red_flags = fetch_from_postgres(query)
        red_flags = pd.append([red_flags, add_red_flags])
    return red_flags


def retrieve_yellow_cards(location=None, handles=[]):
    """
    Retrieves instances of low media count or low engagement rate.
    """
    if (location is None) or (len(location) == 0):
        location_statement = sql.SQL("c.id > 0")
    else:
        location_statement = sql.SQL("c.id in ({location_list})").format(
            location_list=sql.SQL(",").join(map(sql.Literal, location))
        )

    query = sql.SQL(
        """
        select
            sa.updated_at as date
            , sa.influencer_id as influencer_id
            , handle,follows_count
            ,followers_count
            , media_count,engagement_rate
            ,c.name as country
        from social_accounts as sa
    inner join influencer_countries as ic on ic.influencer_id = sa.influencer_id
    inner join influencers as i on i.id = sa.influencer_id
    inner join countries as c on c.id = ic.country_id
    where (
    (followers_count > 2000 AND media_count < 25 AND engagement_rate < 0.01 ) OR
    (engagement_rate < 0.006)
    )
    AND {location}
    AND sa.social_platform_id = 1
    AND i.influencer_status_id=3"""
    ).format(location=location_statement)
    yellows = fetch_from_postgres(query)

    if len(handles) > 0:
        query = sql.SQL(
            """
            SELECT DISTINCT sa.influencer_id as influencer_id
                , handle
                , c.name as country
            FROM social_accounts as sa
            inner join influencer_countries as ic on ic.influencer_id = sa.influencer_id
            inner join influencers as i on i.id = sa.influencer_id
            inner join countries as c on c.id = ic.country_id
            WHERE sa.handle IN ({handles})
                AND {location}
                AND sa.social_platform_id = 1
        """
        ).format(
            handles=sql.SQL(", ").join(map(sql.Literal, handles)),
            location=location_statement,
        )

        add_yellow_flags = fetch_from_postgres(query)
        yellows = pd.append([yellows, add_yellow_flags])

    return yellows


def retrieve_safe_search(bucket, location=None):
    """
    Fetch data from the safe search
    """

    s3 = boto3.client("s3", aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)
    try:
        objects = s3.list_objects(
            Bucket=bucket,
            Prefix="influencer-poker/data/annotations/safe-search/flagged_influencers",
        )["Contents"]
        objects = [i["Key"] for i in objects if ".json" in i["Key"]]
    except:
        objects = []
    influencer_ids = [
        re.sub(
            "influencer-poker/data/annotations/safe-search/flagged_influencers/|.json",
            "",
            i,
        )
        for i in objects
    ]

    if (location is None) or (len(location) == 0):
        location_statement = sql.SQL("c.id > 0")
    else:
        location_statement = sql.SQL("c.id in ({location_list})").format(
            location_list=sql.SQL(",").join(map(sql.Literal, location))
        )

    query = sql.SQL(
        """
        SELECT
            i.id as influencer_id
            , handle
        FROM influencers as i
            inner join influencer_countries as ic on ic.influencer_id = i.id
            inner join countries as c on c.id = ic.country_id
            inner join social_accounts as sa on sa.influencer_id = i.id
            WHERE influencer_status_id in (3,4)
            AND social_platform_id = 1
            AND {location}
        """
    ).format(location=location_statement)

    data = fetch_from_postgres(query)

    data = data.loc[data["influencer_id"].isin([int(i) for i in influencer_ids])]

    print(data)
    return data


def retrieve_safe_search_influencer(influencer_id, bucket):
    key = f"influencer-poker/data/annotations/safe-search/flagged_influencers/{influencer_id}.json"

    s3 = boto3.client("s3", aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)

    safe_search_values = s3.get_object(Bucket=bucket, Key=key)
    safe_search_values = safe_search_values["Body"]
    safe_search = pd.read_json(safe_search_values)
    return safe_search


def fetch_classification_data(location=None):
    """Fetch the data to be classified for each influecner"""
    if (location is None) or (len(location) == 0):
        location_statement = sql.SQL("c.id > 0")
    else:
        location_statement = sql.SQL("c.id in ({location_list})").format(
            location_list=sql.SQL(",").join(map(sql.Literal, location))
        )

    query = sql.SQL(
        """
        SELECT
            DISTINCT sa.handle,
            sa.followers_count,
            sa.follows_count,
            sa.engagement_rate * sa.followers_count AS engagement,
            sa.media_count,
            ip.media_url
        FROM social_accounts sa
        JOIN social_platforms sp ON sp.id = sa.social_platform_id
            AND sp.id = 1
        JOIN influencer_posts ip ON ip.influencer_id = sa.influencer_id
            AND ip.media_url LIKE '%' || sp.code || '%'
        JOIN influencers inf ON inf.id = sa.influencer_id
        JOIN influencer_countries as ic on ic.influencer_id = inf.id
        JOIN countries as c on c.id = ic.country_id
        WHERE inf.email NOT LIKE '%@vamp.me%'
            AND inf.date_of_birth > NOW() - INTERVAL '90 years'
            AND {location}
            AND inf.influencer_status_id = 3
            AND ip.expires_at >= NOW();
    """
    ).format(location=location_statement)

    return fetch_from_postgres(query)


def fetch_influecner_class_data(handle=""):
    query = sql.SQL(
        """
        SELECT
            DISTINCT sa.handle,
            sa.followers_count,
            sa.follows_count,
            sa.engagement_rate * sa.followers_count AS engagement,
            sa.media_count,
            ip.media_url,
            ip.media_type
        FROM social_accounts sa
        JOIN social_platforms sp ON sp.id = sa.social_platform_id
            AND sp.id = 1
        JOIN influencer_posts ip ON ip.influencer_id = sa.influencer_id
            AND ip.media_url LIKE '%' || sp.code || '%'
        JOIN influencers inf ON inf.id = sa.influencer_id
        JOIN influencer_countries as ic on ic.influencer_id = inf.id
        JOIN countries as c on c.id = ic.country_id
        WHERE inf.email NOT LIKE '%@vamp.me%'
            AND inf.date_of_birth > NOW() - INTERVAL '90 years'
            AND sa.handle IN ({handle})
            AND inf.influencer_status_id = 3;
    """
    ).format(handle=sql.SQL(", ").join(map(sql.Literal, handle)))

    return fetch_from_postgres(query)

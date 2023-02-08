from data.functions import fetch_from_postgres


def retrieve_rate_cards(
    location=None, channel=None, campaign_type="social", currency="AUD"
):
    if location == None:
        location_statement = "country_id in (SELECT id from countries)"
    elif len(location) == 0:
        location_statement = "country_id in (SELECT id from countries)"
    else:
        if len(location) > 1:
            string = ",".join([str(i) for i in location])
        else:
            string = str(location[0])
        location_statement = "".join(["country_id in (", string, ")"])

    if (campaign_type == None) | (campaign_type == "social"):
        campaign_type_statement = (
            "criteria in"
            " ('instagram_followers','tiktok_followers','youtube_subscribers')"
        )
    elif campaign_type == "event":
        campaign_type_statement = "criteria in ('event','tiktok_event','youtube_event')"
    elif campaign_type == "content":
        campaign_type_statement = "criteria in ('content')"
    else:
        campaign_type_statement = (
            "criteria in"
            " ('instagram_followers','tiktok_followers','youtube_subscribers')"
        )

    if (campaign_type == "content") | (channel == None):
        channel_statement = "criteria like '%'"
    elif channel == "instagram":
        channel_statement = "criteria in ('event','instagram_followers')"
    elif channel == "tiktok":
        channel_statement = "criteria in ('tiktok_event','tiktok_followers')"
    elif channel == "youtube":
        channel_statement = "criteria in ('youtube_event','youtube_followers')"

    currency_statement = (
        f"currency_id in (select id from currencies where code = '{currency}')"
    )

    where_statement = (
        f"active = True AND {location_statement} AND {campaign_type_statement} AND"
        f" {channel_statement} AND {currency_statement}"
    )

    query = f"""SELECT criteria,coin_count as token_value, max(price) as max_price, (max(price)/coin_count) as token_cost
    FROM rate_cards as rc inner join deliverable_types as dt
    ON dt.id = rc.content_type_id
    WHERE {where_statement}
    GROUP BY criteria, coin_count"""
    results = fetch_from_postgres(query)
    return results


def custom_price_by_original_token_value(
    location=None, channel=None, campaign_type="social", currency="AUD"
):
    if location == None:
        location_statement = "country_id in (SELECT id from countries)"
    elif len(location) == 0:
        location_statement = "country_id in (SELECT id from countries)"
    else:
        if len(location) > 1:
            string = ",".join([str(i) for i in location])
        else:
            string = str(location[0])
        location_statement = "".join(["country_id in (", string, ")"])

    if (campaign_type == None) | (campaign_type == "social"):
        campaign_type_statement = (
            "criteria in"
            " ('instagram_followers','tiktok_followers','youtube_subscribers')"
        )
    elif campaign_type == "event":
        campaign_type_statement = "criteria in ('event','tiktok_event','youtube_event')"
    elif campaign_type == "content":
        campaign_type_statement = "criteria in ('content')"
    else:
        campaign_type_statement = (
            "criteria in"
            " ('instagram_followers','tiktok_followers','youtube_subscribers')"
        )

    if (campaign_type == "content") | (channel == None):
        channel_statement = "criteria like '%'"
    elif channel == "instagram":
        channel_statement = "criteria in ('event','instagram_followers')"
    elif channel == "tiktok":
        channel_statement = "criteria in ('tiktok_event','tiktok_followers')"
    elif channel == "youtube":
        channel_statement = "criteria in ('youtube_event','youtube_followers')"

    currency_statement = (
        f"rc.currency_id in (select id from currencies where code = '{currency}')"
    )

    where_statement = (
        f"active = True AND custom_price is not null AND {location_statement} AND"
        f" {campaign_type_statement} AND {channel_statement} AND {currency_statement}"
    )

    query = f"""SELECT  CASE WHEN quantity > 0 THEN 'selected' ELSE 'applied' END as status, has_managed_service, custom_price, coin_count as original_token_value, token_cost as current_token_value
    FROM brief_requirements as br
    INNER JOIN rate_cards as rc on br.rate_card_id = rc.id
    inner join deliverable_types as dt
    ON dt.id = rc.content_type_id
    inner join briefs as b
    on b.id = br.brief_id
    inner join influencers as i on i.id = b.influencer_id
    inner join campaigns as c on c.id = b.campaign_id
    inner join teams as t on t.id = c.team_id
    WHERE {where_statement}
    AND b.inserted_at > '2021-05-25'
    AND t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge',
'Yourcompany')
    AND (c.desired_age_ranges <> '100-999' OR c.desired_age_ranges is NULL)
    AND date_of_birth > '1930-01-01'"""
    print(query)
    results = fetch_from_postgres(query)

    print(results)
    return results

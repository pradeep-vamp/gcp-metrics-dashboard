"""
 callbacks/campaign_lookup.py

 @ticket:	https://vampdash.atlassian.net/browse/DAS-7702
 @date:		2021-07-28
 @auth:		Daniel Stratti < daniels@vamp.me >

 @desc:
 This file stores all the functions for dynamically generating the data for the
 campaign lookup page
"""
import re
from datetime import datetime as dt

import dash_bootstrap_components as dbc

# Utilities
import pandas as pd
from dash import dash_table, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Data & Components & Helpers
from components.components import *
from data.campaign_lookup import *
from data.functions import *
from graphs.graphs import *

# Dash componenets
from main import app

""" helper function """


def map_brief_status(brief_row):
    """
    Map the database brief statuses to correct text label
            brief_row : Dataframe row
                    A single row of the brief dataframe

            return : str
                    Returns the correct status lable
    """
    if brief_row["brief_status_id"] == 2 and brief_row["brief_inserted_at"].replace(
        tzinfo=None
    ) > dt(2019, 2, 12).replace(tzinfo=None):
        return (
            "Invited - Viewed"
            if brief_row["brief_is_viewed"]
            else "Invited - Not Viewed"
        )

    elif brief_row["brief_status_id"] == 3:
        return "Applied"

    elif brief_row["brief_status_id"] == 4 and brief_row["brief_inserted_at"].replace(
        tzinfo=None
    ) > dt(2019, 2, 12).replace(tzinfo=None):
        return (
            "Viewed - Did not apply"
            if brief_row["brief_is_viewed"]
            else "Invited - Not Viewed"
        )

    return brief_row["brief_status"]


def get_influencer_briefs(campaigns):
    """Collect influencers and briefs based on campaign selection"""
    if campaigns is None:
        raise PreventUpdate

    print("geting suggestions")
    campaigns = pd.read_json(campaigns, orient="split")

    if len(campaigns) != 1:
        raise PreventUpdate

    briefs = fetch_briefs_influencers(campaigns.loc[0, "id"])

    return briefs


@app.callback(Output("cl-campaigns", "data"), [Input("cl_campaign_search", "value")])
def get_campaign(search=None):
    """
    Dynamically retrieve a list of campaigns matching the search criteria, if
    there is only 1 match, also grab the influencer briefs
            start_date : Date The begining of the applicable search period
            end_date : Date The end of the applicable search period
            search : str The search query (campaign ID or name)

            return : JSON
                    Returns a JSON list of campaigns to store in the state
    """
    print("Collecting campaigns")

    search = None if search == "" else search

    # Extract campaign ID from search
    if search is not None:
        num = re.findall(r"\[\d{6}\]", search)

        if len(num) > 0:
            search = num[0]
            search = re.sub(r"(^\[0*|\]|)", "", search)

    print(search)
    campaigns = fetch_campaigns(search)
    print("Campaigns collected")

    return campaigns.to_json(orient="split", date_format="iso")


@app.callback(
    Output("cl_campaign_suggestions", "children"),
    [Input("cl-campaigns", "data")],
)
def get_campaign_suggestions(campaigns):
    """
    Based on the matching campaigns stored in the State, create a list of suggestions
            campaigns : JSON
                    The list of campaigns matching the search query stored in State

            return : JSON
                    Returns a JSON list of campaigns to store in the state
    """
    if campaigns is None:
        raise PreventUpdate

    print("geting suggestions")
    campaigns = pd.read_json(campaigns, orient="split")

    return [
        html.Option(value=word, label=word)
        for word in campaigns["text_value"].to_list()
    ]


@app.callback(Output("cl_briefs_chart", "children"), [Input("cl-campaigns", "data")])
def get_brief_stats(campaigns):
    """
    If only 1 campaign matches the search query generate and display a barchart
    of the brief statuses
            campaigns : JSON
                    The list of campaigns matching the search query stored in State

            return : Graph
                    Returns a plotly barchart
    """
    briefs = get_influencer_briefs(campaigns)

    if len(briefs) == 0:
        # replace with empty chart
        raise PreventUpdate

    brief_ids = briefs["brief_id"].to_list()
    notifications = fetch_notifications(brief_ids)

    return cl_briefs_barchart(briefs, notifications)


@app.callback(
    Output("cl_campaign_details_table", "children"),
    [Input("cl-campaigns", "data")],
)
def get_campaign_details(campaigns):
    """
    If only 1 campaign matches the search query generate and display its details
            campaigns : JSON
                    The list of campaigns matching the search query stored in State

            return : Bootstrap Table
                    Returns the campaign details as a table
    """
    if campaigns is None:
        raise PreventUpdate

    print("geting details")
    campaign = pd.read_json(campaigns, orient="split")

    if len(campaign) != 1:
        # replace with empty table
        raise PreventUpdate

    display_campaign = campaign.copy()

    display_campaign = display_campaign.loc[
        :,
        [
            "id",
            "name",
            "started_on",
            "end_date",
            "status",
            "has_managed_service",
            "budget",
            "desired_location",
            "desired_age_ranges",
            "desired_genders",
            "search_term",
            "currency_code",
            "currency_symbol",
        ],
    ]
    display_campaign["started_on"] = (
        pd.to_datetime(display_campaign["started_on"])
        .apply(lambda x: x.replace(tzinfo=None))
        .dt.strftime("%d/%m/%Y")
    )
    display_campaign["end_date"] = (
        pd.to_datetime(display_campaign["end_date"])
        .apply(lambda x: x.replace(tzinfo=None))
        .dt.strftime("%d/%m/%Y")
    )
    display_campaign["high_low"] = display_campaign["has_managed_service"].apply(
        lambda x: "High Touch" if x else "Low Touch"
    )
    display_campaign["budget_format"] = display_campaign.apply(
        lambda x: f"({x['currency_code']}) {x['currency_symbol']} {x['budget']:,.2f}",
        axis=1,
    )

    display_campaign = display_campaign.drop(
        columns=["budget", "currency_code", "currency_symbol"]
    )
    display_campaign = display_campaign.reindex(
        columns=[
            "id",
            "name",
            "started_on",
            "end_date",
            "status",
            "high_low",
            "budget_format",
            "desired_location",
            "desired_age_ranges",
            "desired_genders",
            "search_term",
        ]
    )
    display_campaign = display_campaign.rename(
        columns={
            "id": "Campaign ID",
            "name": "Campaign Name",
            "started_on": "Started On",
            "end_date": "Ended On",
            "status": "Campaign Status",
            "high_low": "Service",
            "budget_format": "Budget",
            "desired_location": "Location Filter",
            "desired_age_ranges": "Age Filter",
            "desired_genders": "Gender Filter",
            "search_term": "Search Term",
        }
    )
    display_campaign = display_campaign.transpose().reset_index()

    rows = [
        html.Tr([html.Td(row["index"]), html.Td(row[0])])
        for idx, row in display_campaign.iterrows()
    ]
    data_table = dbc.Table([html.Tbody(rows)], striped=True, bordered=True, hover=True)
    return data_table


@app.callback(
    Output("cl_influencer_table", "children"), [Input("cl-campaigns", "data")]
)
def get_influencers(campaigns):
    """
    If only 1 campaign matches the search query generate and display details of
    the influencer who were sent a brief
            campaigns : JSON
                    The list of campaigns matching the search query stored in State

            return : Table
                    Returns the influencer details as a table
    """
    influencers = get_influencer_briefs(campaigns)

    if len(influencers) == 0:
        raise PreventUpdate

    display_influencers = influencers.copy()

    display_influencers = display_influencers.loc[
        :,
        [
            "handle",
            "platform",
            "brief_status",
            "engagement_rate",
            "followers_count",
            "similarity_score",
            "local_audience",
            "brief_inserted_at",
        ],
    ]
    display_influencers["engagement_rate"] = (
        display_influencers["engagement_rate"].apply(lambda x: x * 100).round(2)
    )
    display_influencers["similarity_score"] = display_influencers[
        "similarity_score"
    ].round(4)
    display_influencers["local_audience"] = display_influencers["local_audience"].round(
        2
    )
    # last_active_sent = pd.to_datetime(briefs['brief_last_active_brief_sent']).apply(lambda x: x.replace(tzinfo=None))
    display_influencers["brief_inserted_at"] = pd.to_datetime(
        display_influencers["brief_inserted_at"]
    ).apply(lambda x: x.replace(tzinfo=None))
    display_influencers["brief_status"] = influencers.apply(
        lambda row: map_brief_status(row), axis=1
    )

    cols = [
        {"id": "handle", "name": "Handle"},
        {"id": "platform", "name": "Social Platform"},
        {"id": "brief_status", "name": "Status"},
        {"id": "engagement_rate", "name": "Engagement Rate (%)"},
        {"id": "followers_count", "name": "Followers"},
        {"id": "similarity_score", "name": "Similarity"},
        {"id": "local_audience", "name": "Local Audience"},
    ]

    data_table = dash_table.DataTable(
        id="cl_influencer_table",
        columns=cols,
        data=display_influencers.to_dict("records"),
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=20,
        style_table={"overflowX": "scroll"},
    )

    return data_table


@app.callback(
    Output("cl_influencer_download", "data"),
    [Input("cl_influencer_download_btn", "n_clicks")],
    [State("cl-campaigns", "data"), State("current_loggedin_email", "data")],
)
def generate_csv(n_clicks, campaign, current_email):
    """
    If only 1 campaign matches the search query generate a CSV download of the
    influencers details of who were sent a brief
            campaigns : JSON
                    The list of campaigns matching the search query stored in State

            return : CSV Download
                    Returns the influencer details as a CSV Download
    """
    restrict_resource(current_email)

    influencers = get_influencer_briefs(campaign)

    # Only download once clicked
    if n_clicks == 0 or n_clicks is None or len(influencers) == 0:
        raise PreventUpdate

    campaign = pd.read_json(campaign, orient="split")

    download_influencers = influencers.loc[
        :,
        [
            "handle",
            "platform",
            "full_name",
            "email",
            "mobile_phone",
            "followers_count",
            "engagement_rate",
            "is_business",
            "reward_value",
            "brief_status",
            "similarity_score",
            "local_audience",
        ],
    ]

    # download_influencers['brief_inserted_at'] = pd.to_datetime(download_influencers['brief_inserted_at']).apply(lambda x: x.replace(tzinfo=None))
    campaign_name = campaign.loc[0, "name"]
    campaign_name = campaign_name.lower().replace(" ", "_")
    download_influencers["brief_status"] = influencers.apply(
        lambda row: map_brief_status(row), axis=1
    )

    # Format data and filename ready for download
    filename = f"campaign_lookup_{campaign_name}.csv"

    return dcc.send_data_frame(
        download_influencers.to_csv, filename=filename, index=False
    )

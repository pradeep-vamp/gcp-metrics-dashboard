"""
 callbacks/influencer_usage.py

 @ticket:	https://vampdash.atlassian.net/browse/DAS-7706
 @date:		2021-05-04
 @auth:		Daniel Stratti < daniels@vamp.me >

 @desc:
 This file is used to process the data required for the `Influencer Usage` page.
 The main functionality requred is to collect and filter the influencer usage
 data ready to be graphed and tabulated. Secondly the page provides download
 functionality of the collected data.
"""
import json
from datetime import date

import dateutil.parser as datep
import numpy as np

# Utilities
import pandas as pd
from dash import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Data & Components & Helpers
from components.components import *
from data.functions import *
from data.influencer_usage import *
from graphs.graphs import *

# Dash componenets
from main import app

"""
Dynamically display a list of applicable regions to filter the search by
@param start_date {Date}: The begining of the applicable search period
@param end_date {Date}: The end of the applicable search period
@param region {Integer}: The regiojn to filter by

@return {Dataframe Records}: The applicable teams ready for display
"""


@app.callback(
    Output("iu_sales_team_drop_down", "options"),
    [
        Input("influencer_usage_date_inputs", "start_date"),
        Input("influencer_usage_date_inputs", "end_date"),
        Input("iu_region_drop_down", "value"),
    ],
)
def get_teams_dropdown(start_date, end_date, region="-1"):

    region = None if region == "-1" else region
    teams = fetch_teams(start_date, end_date, region, None)[["id", "display_name"]]
    teams.columns = ["value", "label"]

    # Add the all option
    teams = pd.concat([pd.DataFrame([{"value": "-1", "label": "All"}]), teams])
    return teams.to_dict("records")


"""
Dynamically display a list of applicable regions to filter the search by
@param start_date {Date}: The begining of the applicable search period
@param end_date {Date}: The end of the applicable search period
@param team {Integer}: The team to filter by

@return {Dataframe Records}: The applicable regions ready for display
"""


@app.callback(
    Output("iu_region_drop_down", "options"),
    [
        Input("influencer_usage_date_inputs", "start_date"),
        Input("influencer_usage_date_inputs", "end_date"),
        Input("iu_sales_team_drop_down", "value"),
    ],
)
def get_region_dropdown(start_date, end_date, team="-1"):

    team = None if team == "-1" else team
    regions = fetch_region(start_date, end_date, team, None)

    # Add the all option\
    regions = pd.concat([pd.DataFrame([{"value": "-1", "label": "All"}]), regions])

    return regions.to_dict("records")


"""
Helper function to collect, merge & calculate all influencer usage statistics
required for the page
@param start_date (date_inputs) {Date}: The start of the period to search within
@param end_date (date_inputs) {Date}: The end of the period to search within
@param team_val (ss_sales_team_drop_down) {Integer}: The id of the sales team to filter
@param region (iu_region_drop_down) {String}: The name of a country region
@param customer_type (customer_type_dropdown) {String}: The customer type to filter

@return {DataFrame}: Returns a joson encoded dictionary of all required DF's
"""
# @app.callback(Output('iu-dataset', 'data'), [
# 	Input('date_inputs', 'start_date'),
# 	Input('date_inputs', 'end_date'),
# 	Input('iu_sales_team_drop_down', 'value'),
# 	Input('iu_region_drop_down', 'value'),
# 	Input('customer_type_dropdown', 'value')
# 	])


def get_iu_stats(
    start_date, end_date, team_val, region, customer_type, service_level=None
):
    # validate team_val & region for selecting `All`
    team_val = None if team_val == "-1" else team_val
    region = None if region == "-1" else region
    customer_type = None if customer_type == "all" else customer_type
    service_level = None if service_level == "all" else service_level

    # Extract data with filters from postgres
    iu_briefs = fetch_iu_briefs(
        start_date, end_date, team_val, region, customer_type, service_level
    )
    if len(iu_briefs) == 0:
        # see: https://dash.plotly.com/sharing-data-between-callbacks
        iu_serialise = {
            "iu_table": pd.DataFrame().to_json(orient="split", date_format="iso"),
            "iu_usage": pd.DataFrame().to_json(orient="split", date_format="iso"),
        }
        return json.dumps(iu_serialise)

    # Collect additional data
    iu_stats = fetch_iu_stats(
        start_date, end_date, iu_briefs["influencer_id"].tolist(), region
    )
    iu_local_aud = fetch_iu_local_audience(iu_briefs["influencer_id"].to_list(), region)

    # use bool val to determine if brief was won or lost
    iu_briefs["was_won"] = iu_briefs["participation"]

    # Calculate Table stats
    iu_briefs_table = (
        iu_briefs.groupby(["influencer_id"])
        .agg(
            {
                "participation": "sum",
                "brief_id": "count",
                "similarity_score": "mean",
                "engagement_rate": "mean",
            }
        )
        .reset_index()
    )

    # Merge data for table
    iu_table = iu_stats.merge(
        iu_briefs_table,
        how="left",
        left_on="id",
        right_on="influencer_id",
        suffixes=("", "_"),
    )

    # extract won and lost local audience
    if region is not None:
        iu_local_table = (
            iu_local_aud.groupby(["influencer_id", "region"], as_index=False)
            .agg({"local_audience": "mean"})
            .reset_index()
        )
        merge_sum = ["influencer_id", "region"]
        merge_table = ["id", "region"]
    else:
        iu_local_table = (
            iu_local_aud.groupby(["influencer_id", "country"], as_index=False)
            .agg({"local_audience": "mean"})
            .reset_index()
        )
        merge_sum = ["influencer_id", "country"]
        merge_table = ["id", "country"]

    # Merge Audience
    iu_table = iu_table.merge(
        iu_local_table,
        how="left",
        left_on=merge_table,
        right_on=merge_sum,
        suffixes=("", "_audience"),
    )

    iu_table = iu_table.rename(columns={"brief_id": "applications"})

    # Calculate acceptance rate
    try:
        iu_table["accept_rate"] = (
            iu_table["participation"] / iu_table["applications"] * 100
        )
    except ZeroDivisionError:
        iu_table["accept_rate"] = 0

    # Data for graph
    iu_usage = iu_table.sort_values("participation")

    if len(iu_usage) > 0 and iu_usage["participation"].sum() > 0:
        iu_usage["cumsum"] = (
            iu_usage["participation"].cumsum() / iu_usage["participation"].sum()
        )
    else:
        iu_usage["cumsum"] = 0

    # see: https://dash.plotly.com/sharing-data-between-callbacks
    iu_serialise = {
        "iu_table": iu_table.to_json(orient="split", date_format="iso"),
        "iu_usage": iu_usage.to_json(orient="split", date_format="iso"),
    }

    return json.dumps(iu_serialise)


"""
Transform table date ready for display based on data from `get_iu_stats`
@param iu_serialise {JSON}: The JSON encoded data produced by the `get_iu_stats`
							function

@return {DataTable}: Returns a data table dash component ready for display
"""


@app.callback(
    Output("iu_campaigns_table", "children"),
    [
        Input("influencer_usage_date_inputs", "start_date"),
        Input("influencer_usage_date_inputs", "end_date"),
        Input("iu_sales_team_drop_down", "value"),
        Input("iu_region_drop_down", "value"),
        Input("service_level_drop_down", "value"),
    ],
)
def build_iu_table(start_date, end_date, team_val, region, service_level):

    # Load data from JSON
    iu_serialise = get_iu_stats(
        start_date, end_date, team_val, region, None, service_level
    )
    iu_display = json.loads(iu_serialise)
    iu_display = pd.read_json(iu_display["iu_table"], orient="split")

    if len(iu_display) == 0:
        raise PreventUpdate  # Stop update

    # fill NAs for display
    fillna_cols = [
        "participation",
        "accept_rate",
        "engagement_rate",
        "followers_count",
        "local_audience",
        "applications",
    ]
    iu_display[fillna_cols] = iu_display[fillna_cols].fillna(0)

    # Round rates
    round_cols = ["accept_rate", "engagement_rate", "local_audience"]
    iu_display[round_cols] = iu_display[round_cols].round(2)

    # Set table columns, ids map to column names from data/influencer_usage.py
    iu_display = iu_display.sort_values("participation", ascending=False)
    cols = [
        {"id": "handle", "name": "Handle"},
        {"id": "participation", "name": "Campaigns"},
        {"id": "accept_rate", "name": "Acceptance Rate (%)"},
        {"id": "engagement_rate", "name": "Engagement Rate (%)"},
        {"id": "followers_count", "name": "Follower Count"},
        {"id": "local_audience", "name": "Local Audience (%)"},
        {"id": "applications", "name": "Applications"},
    ]

    data_table = dash_table.DataTable(
        id="table",
        columns=cols,
        data=iu_display.to_dict("records"),
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=20,
        style_table={"overflowX": "scroll"},
        style_data_conditional=[
            {
                "if": {"filter_query": "{has_managed_service} contains true"},
                "backgroundColor": "#fe3769",
                "color": "white",
            }
        ],
    )

    return data_table


"""
Calculate and format the summary statistics ready to be displayed on the page
@param iu_serialise {JSON}: The JSON encoded data produced by the `get_iu_stats`
							function

@return {Tuple}: Returns a tuble of 8 value boxes consisting of an icon, text
				and statistic
"""


@app.callback(
    [
        Output("iu_50_percent", "children"),
        Output("iu_success_rate", "children"),
        Output("iu_avg_similarity_won", "children"),
        Output("iu_avg_similarity_lost", "children"),
        Output("iu_avg_engagement_won", "children"),
        Output("iu_avg_engagement_lost", "children"),
        Output("iu_avg_local_won", "children"),
        Output("iu_avg_local_lost", "children"),
    ],
    [
        Input("influencer_usage_date_inputs", "start_date"),
        Input("influencer_usage_date_inputs", "end_date"),
        Input("iu_sales_team_drop_down", "value"),
        Input("iu_region_drop_down", "value"),
        Input("service_level_drop_down", "value"),
    ],
)
def build_iu_summary(start_date, end_date, team_val, region, service_level):
    # Load data from JSON
    iu_serialise = get_iu_stats(
        start_date, end_date, team_val, region, None, service_level
    )
    iu_display = json.loads(iu_serialise)
    iu_table = pd.read_json(iu_display["iu_table"], orient="split")
    iu_usage = pd.read_json(iu_display["iu_usage"], orient="split")
    won_brief_status = [
        "shortlisted",
        "approved",
        "fulfilled",
        "completed",
        "media_uploaded",
        "media_accepted",
        "processing_payment",
    ]

    if len(iu_table) == 0:
        raise PreventUpdate  # Stop update

    # validate team_val & region for selecting `All`
    team_val = None if team_val == "-1" else team_val
    region = None if region == "-1" else region
    service_level = None if service_level == "all" else service_level
    # Calculate summary stats
    total_complete = iu_table["participation"].sum()
    total_applications = iu_table["applications"].sum()

    try:
        total_succes_rate = total_complete / total_applications * 100
    except ZeroDivisionError:
        total_succes_rate = 0

    if len(iu_usage) > 0:
        percent_above_50 = (
            len(iu_usage.loc[iu_usage["cumsum"] >= 0.5]) / len(iu_usage) * 100
        )
    else:
        percent_above_50 = 0

    # Fetch list of influencer with brief status'
    inf_briefs = fetch_iu_influencer_briefs(
        start_date, end_date, team_val, region, None, service_level
    )
    won_briefs = inf_briefs.loc[inf_briefs["code"].isin(won_brief_status)]
    lost_briefs = inf_briefs.loc[~inf_briefs["code"].isin(won_brief_status)]

    won_inf_ids = extract_ids(won_briefs["influencer_ids"])
    lost_inf_ids = extract_ids(lost_briefs["influencer_ids"])

    # Get engagement and local audience of won / lost by
    won_local_engage = fetch_local_engagement(won_inf_ids)
    lost_local_engage = fetch_local_engagement(lost_inf_ids)

    avg_engage_won = (
        won_local_engage["engagements"].sum()
        / won_local_engage["followers_count"].sum()
    ) * 100
    avg_local_won = (
        float(won_local_engage["local_audience_value"].sum())
        / float(won_local_engage["followers_count"].sum())
    ) * 100
    avg_engage_lost = (
        lost_local_engage["engagements"].sum()
        / lost_local_engage["followers_count"].sum()
    ) * 100
    avg_local_lost = (
        float(lost_local_engage["local_audience_value"].sum())
        / float(lost_local_engage["followers_count"].sum())
    ) * 100

    # Calc averages for won vs lost
    avg_sim = fetch_avg_sim(start_date, end_date, team_val, region, None)
    print("avg_sim", avg_sim)

    if len(avg_sim) == 1:
        avg_sim_won = avg_sim["avg_won_similarity"].iloc[0]
        avg_sim_lost = avg_sim["avg_lost_similarity"].iloc[0]
    else:
        avg_sim_won = avg_sim["avg_won_similarity"].mean()
        avg_sim_lost = avg_sim["avg_lost_similarity"].mean()

    print(type(avg_sim_won), avg_sim_won)

    # Fix Nan's for display
    avg_sim_won = avg_sim_won if not np.isnan(avg_sim_won) else 0
    avg_sim_lost = avg_sim_lost if not np.isnan(avg_sim_lost) else 0

    # Create summary stats value boxes
    vb_percent = value_box(
        "🧑‍💻 ",
        "Influencers completed over 50%",
        f"{float(percent_above_50):.2f}%",
    )
    vb_success_rate = value_box(
        "😁 ", "Success Rate", f"{float(total_succes_rate):.2f}%"
    )
    vb_avg_sim_won = value_box(
        "📝 ", "Avg Similarity (Won)", f"{float(avg_sim_won):.2f}%"
    )
    vb_avg_sim_lost = value_box(
        "📝 ", "Avg Similarity (Lost)", f"{float(avg_sim_lost):.2f}%"
    )
    vb_avg_engage_won = value_box(
        "🙌 ", "Avg Engagement (Won)", f"{float(avg_engage_won):.2f}%"
    )
    vb_avg_engage_lost = value_box(
        "🙌 ", "Avg Engagement (Lost)", f"{float(avg_engage_lost):.2f}%"
    )
    vb_avg_local_won = value_box(
        "🌍 ", "Avg Local Audience (Won)", f"{float(avg_local_won):.2f}%"
    )
    vb_avg_local_lost = value_box(
        "🌍 ", "Avg Local Audience (Lost)", f"{float(avg_local_lost):.2f}%"
    )

    # return all 8 summary stats
    return (
        vb_percent,
        vb_success_rate,
        vb_avg_sim_won,
        vb_avg_sim_lost,
        vb_avg_engage_won,
        vb_avg_engage_lost,
        vb_avg_local_won,
        vb_avg_local_lost,
    )


"""
Extract IDs from a postgress array_agg into a single array
"""


def extract_ids(series):
    ids = []

    for row in series:
        ids = [*ids, *row]

    return ids


"""
Process the cumulative usage data on campaign proportions vs influencer proportion
@param iu_serialise {JSON}: The JSON encoded data produced by the `get_iu_stats`
							function

@return {Tuple}: Returns a plotly figure
"""


@app.callback(
    Output("iu_campaigns_chart", "children"),
    [
        Input("influencer_usage_date_inputs", "start_date"),
        Input("influencer_usage_date_inputs", "end_date"),
        Input("iu_sales_team_drop_down", "value"),
        Input("iu_region_drop_down", "value"),
        Input("service_level_drop_down", "value"),
    ],
)
def build_iu_chart(start_date, end_date, team_val, region, service_level):
    # Load data from JSON
    iu_serialise = get_iu_stats(
        start_date, end_date, team_val, region, None, service_level
    )

    # Load data from JSON
    iu_display = json.loads(iu_serialise)
    iu_usage = pd.read_json(iu_display["iu_usage"], orient="split")

    if len(iu_usage) == 0:
        raise PreventUpdate

    # Generate line graph
    cum_camp_inf_chart = iu_cumulative_scatter(iu_usage)

    return cum_camp_inf_chart


"""
Generate a CSV to download of the tabled data shown on the influencer usage page
@param n_clicks {Integer | None}: Used to check if the download button was infact pressed
@param start_date (date_inputs) {Date}: The start of the period to search within
@param end_date (date_inputs) {Date}: The end of the period to search within
@param team_val (ss_sales_team_drop_down) {Integer}: The id of the sales team to filter
@param region (iu_region_drop_down) {String}: The name of a country region
"""


@app.callback(
    Output("iu_stats_download", "data"),
    [Input("iu_stats_download_btn", "n_clicks")],
    [
        State("influencer_usage_date_inputs", "start_date"),
        State("influencer_usage_date_inputs", "end_date"),
        State("iu_sales_team_drop_down", "value"),
        State("iu_region_drop_down", "value"),
        State("current_loggedin_email", "data"),
    ],
)
def generate_csv(n_clicks, start_date, end_date, team_val, region, current_email):

    restrict_resource(current_email)

    # Only download once clicked
    if n_clicks == 0 or n_clicks is None:
        raise PreventUpdate

    # Load data from JSON
    iu_serialise = get_iu_stats(start_date, end_date, team_val, region, None)
    iu_display = json.loads(iu_serialise)
    iu_display = pd.read_json(iu_display["iu_table"], orient="split")

    # Only download CSV with data
    if len(iu_display) == 0:
        raise PreventUpdate

    # Calculate acceptance rate
    iu_display[["started_on", "end_date"]] = (
        datep.parse(start_date).strftime("%d-%m-%Y"),
        datep.parse(end_date).strftime("%d-%m-%Y"),
    )
    cols = [
        "started_on",
        "end_date",
        "handle",
        "participation",
        "accept_rate",
        "engagement_rate",
        "followers_count",
        "local_audience",
        "applications",
    ]

    if region != "-1":
        iu_display["region"] = region
        cols = ["region", *cols]

    team = []
    if team_val != "-1":
        team = fetch_teams(start_date, end_date)
        team = team.loc[team["id"] == team_val]
        team = team["name"].combine_first(team["code"])

        if len(team) == 1:
            iu_display["team"] = team.iloc[0]
            cols = ["team", *cols]

    # Format data and filename ready for download
    iu_display = iu_display.sort_values("participation", ascending=False)
    data = iu_display.loc[:, cols]
    display_dates = (
        datep.parse(start_date).strftime("%d-%m-%Y"),
        datep.parse(end_date).strftime("%d-%m-%Y"),
        date.today().strftime("%d-%m-%Y"),
    )
    filename = (
        f"influencer_usage_{display_dates[0]}_{display_dates[1]}_{display_dates[2]}.csv"
    )

    if region != "-1":
        filename = f"{region}_{filename}"

    if len(team) > 0:
        filename = f"{team.iloc[0]}_{filename}"

    return dcc.send_data_frame(data.to_csv, filename=filename, index=False)

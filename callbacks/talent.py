# import basic libraries
import pandas as pd
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# import App
from components.components import *

# import data functions
from data.functions import *
from data.talent import *

# import graphing functions
from graphs.graphs import *
from main import app

##### TALENT ANALYSIS #####


@app.callback(
    [
        Output("new-talent-data", "data"),
    ],
    [
        Input("talent_date_inputs", "start_date"),
        Input("talent_date_inputs", "end_date"),
        Input("talent_location_drop_down", "value"),
    ],
)
def fetch_talent_data(start_date, end_date, location):
    data = fetch_new_talent_data(start_date, end_date, location)

    return [data.to_json(orient="split", date_format="iso")]


@app.callback(
    [
        Output("new_talent_graph", "children"),
        Output("talent_value_box", "children"),
        Output("approached_value_box", "children"),
        Output("approval_requested_value_box", "children"),
    ],
    [Input("new-talent-data", "data")],
)
def build_talent_charts(data):
    data = pd.read_json(data, orient="split")
    if data is None:
        raise PreventUpdate
    data = data.loc[
        data["status"].isin(
            [
                "Approved - Approval Requested",
                "Approved - Approached",
                "Approached",
                "Rejected",
                "Approval Requested",
            ]
        )
    ]
    print(data)
    graph = new_talent(data)
    vals = data.loc[
        data["status"].isin(["Approved - Approached", "Approved - Approval Requested"]),
        "count",
    ].sum()
    approved = value_box("🧑‍🤝‍🧑", "New Talent Approved", vals)
    vals = data.loc[
        data["status"].isin(["Approved - Approached", "Approached"]),
        "count",
    ].sum()
    approached = value_box("📢 ", "Total Approached", vals)
    vals = data.loc[
        data["status"].isin(
            [
                "Approved - Approval Requested",
                "Approval Requested",
                "Rejected",
            ]
        ),
        "count",
    ].sum()
    approval_requested = value_box("📱", "Total Approval Requested", vals)
    return [graph, approved, approached, approval_requested]


@app.callback(
    [Output("talent_application_value_box", "children")],
    [
        Input("talent_date_inputs", "start_date"),
        Input("talent_date_inputs", "end_date"),
        Input("talent_location_drop_down", "value"),
    ],
)
def build_talent_charts_2(start_date, end_date, location):
    vals = fetch_new_talent_campaign_application(start_date, end_date, location)[
        "count"
    ][0]
    print("Vals")
    print(vals)
    if vals is None:
        raise PreventUpdate
    applied = value_box("📝", "Applied for a Campaign", vals)
    return [applied]


@app.callback(
    [Output("campaigns_applied_for_graph", "children")],
    [
        Input("talent_date_inputs", "start_date"),
        Input("talent_date_inputs", "end_date"),
        Input("talent_location_drop_down", "value"),
    ],
)
def build_talent_charts_3(start_date, end_date, location):
    data = fetch_new_talent_campaign_application_chart(start_date, end_date, location)
    if data is None:
        raise PreventUpdate
    talent_applications_chart = build_campaign_applications_chart(data)
    return [talent_applications_chart]


@app.callback(
    [Output("talent_location_charts", "children")],
    [
        Input("talent_date_inputs", "start_date"),
        Input("talent_date_inputs", "end_date"),
        Input("talent_location_drop_down", "value"),
    ],
)
def build_talent_charts_4(start_date, end_date, location):
    data = fetch_new_talent_location_data(start_date, end_date, location)
    if data is None:
        raise PreventUpdate
    print(data)
    new_tal_loc = new_talent_locations(data)
    return [new_tal_loc]


@app.callback(
    [Output("brief_response_charts", "children")],
    [
        Input("talent_date_inputs", "start_date"),
        Input("talent_date_inputs", "end_date"),
        Input("talent_location_drop_down", "value"),
    ],
)
def build_talent_charts_5(start_date, end_date, location):
    try:
        data = fetch_brief_response(start_date, end_date, location)
        if data is None:
            raise PreventUpdate
        talent_funnel = talent_funnel_chart(data)
    except:
        talent_funnel = "Not Available"
    return [talent_funnel]

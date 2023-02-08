from datetime import date

import numpy as np

# import basic libraries
import pandas as pd
from dash import dash_table
from dash.dependencies import Input, Output, State

# import App
from components.components import *
from data.fixer import conversion

# import data functions
from data.functions import *
from data.self_serve import *

# import graphing functions
from graphs.graphs import *
from main import app

# Determine current fiscal date


@app.callback(
    [
        Output("self_serve_in_draft", "children"),
        Output("self_serve_moderation", "children"),
        Output("self_serve_live", "children"),
        Output("self_serve_complete", "children"),
        Output("self_serve_deleted", "children"),
        Output("self_serve_campaigns_table", "children"),
    ],
    [
        Input("self_serve_date_inputs", "start_date"),
        Input("self_serve_date_inputs", "end_date"),
        Input("self_serve_customer_type_dropdown", "value"),
    ],
)
def build_self_serve_charts(start_date, end_date, customer_type):
    data = fetch_self_serve_campaigns(start_date, end_date, customer_type)

    sales_team = fetch_from_s3(key="metrics-dashboard/sales_team.csv")
    try:
        sales_team.columns = ["sales_id", "sales_name"]
    except ValueError:
        sales_team.assign(sales_id="", sales_name="")

    sales_customer = fetch_from_s3(key="metrics-dashboard/sales_team_join.csv")
    data = data.append(sales_customer, how="left", on="team_id")
    data = data.append(sales_team, how="left", on="sales_id")

    data = data.loc[:, ["status", "count"]]
    data = data.append(
        [
            {"status": "In Draft/Rejected", "count": 0},
            {"status": "In Moderation", "count": 0},
            {"status": "Live", "count": 0},
            {"status": "Complete", "count": 0},
        ],
        ignore_index=True,
    )
    data = pd.DataFrame(data.groupby("status").sum("count")).reset_index(drop=False)
    in_draft = value_box(
        "✏️ ",
        data.loc[data["status"] == "In Draft/Rejected", "status"],
        int(data.loc[data["status"] == "In Draft/Rejected", "count"]),
        id="self_serve_in_draft_vb",
    )
    in_moderation = value_box(
        "📝 ",
        data.loc[data["status"] == "In Moderation", "status"],
        int(data.loc[data["status"] == "In Moderation", "count"]),
        id="self_serve_moderation_vb",
    )
    live = value_box(
        "🏎️ ",
        data.loc[data["status"] == "Live", "status"],
        int(data.loc[data["status"] == "Live", "count"]),
        id="self_serve_live_vb",
    )
    complete = value_box(
        "💵 ",
        data.loc[data["status"] == "Complete", "status"],
        int(data.loc[data["status"] == "Complete", "count"]),
        id="self_serve_complete_vb",
    )
    deleted = value_box(
        "❌ ",
        data.loc[data["status"] == "Deleted", "status"],
        int(data.loc[data["status"] == "Deleted", "count"]),
        id="self_serve_deleted_vb",
    )
    # full data
    data = fetch_self_serve_campaigns_full(start_date, end_date, customer_type)
    data = data.append(sales_customer, how="left", on="team_id")
    data = data.append(sales_team, how="left", on="sales_id")
    data["high_low"] = data["has_managed_service"].apply(
        lambda x: "High Touch" if x else "Low Touch"
    )

    print(data["high_low"])
    cols = [
        {"id": "campaign_id", "name": "Campaign ID"},
        {"id": "sales_name", "name": "Sales Person"},
        {"id": "campaign_name", "name": "Campaign Name"},
        {"id": "budget", "name": "Budget"},
        {"id": "currency", "name": "Currency"},
        {"id": "start_date", "name": "Start Date"},
        {"id": "end_date", "name": "End Date"},
        {"id": "team_name", "name": "Team Name"},
        {"id": "high_low", "name": "Service"},
        {"id": "status", "name": "Campaign Status"},
    ]

    data_table = dash_table.DataTable(
        id="table",
        columns=cols,
        data=data.to_dict("records"),
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

    # campaigns_count_chart = self_serve_campaigns_chart(data)
    # try:
    # self_serve_locations_chart = self_serve_locations(data)
    # except:
    # 	self_serve_locations_chart = html.P('An Error has Occured')
    return [
        in_draft,
        in_moderation,
        live,
        complete,
        deleted,
        data_table,
    ]  # ,campaigns_count_chart, self_serve_locations_chart])


@app.callback(
    [
        Output("self_serve_campaigns_chart", "children"),
        Output("self_serve_top_countries_chart", "children"),
    ],
    [
        Input("self_serve_date_inputs", "start_date"),
        Input("self_serve_date_inputs", "end_date"),
        Input("self_serve_customer_type_dropdown", "value"),
    ],
)
def generate_campaigns_charts(start_date, end_date, customer_type):
    data = fetch_self_serve_new_customer(start_date, end_date, customer_type)
    camps_chart = self_serve_campaigns_chart(data)
    data = fetch_self_serve_campaigns_full(start_date, end_date, customer_type)
    self_serve_locations_chart = self_serve_locations(data)

    return [camps_chart, self_serve_locations_chart]


@app.callback(
    [Output("self_serve_life_cycle", "children")],
    [
        Input("self_serve_date_inputs", "start_date"),
        Input("self_serve_date_inputs", "end_date"),
        Input("self_serve_customer_type_dropdown", "value"),
    ],
)
def generate_lifecycle_charts(start_date, end_date, customer_type):

    data = fetch_self_serve_life_cycle(start_date, end_date, customer_type)
    data["diff"] = data["max"] - data["min"]
    # data['diff'] = data['diff'].astype('timedelta[d]')
    print(data["diff"].dt.days.astype(int).describe())
    data["segment"] = np.where(
        data["diff"].dt.days.astype(int) < 1,
        "One Time User",
        np.where(
            data["diff"].dt.days.astype(int) < 180,
            "0-6 months",
            np.where(
                data["diff"].dt.days.astype(int) < 365,
                "6-12 months",
                np.where(
                    data["diff"].dt.days.astype(int) < 720,
                    "1-2 years",
                    "More than 2 years",
                ),
            ),
        ),
    )

    lifecycle_chart = ss_lifecycle_chart(data)
    return [lifecycle_chart]


@app.callback(
    Output("campaign_download", "data"),
    [Input("campaign_download_btn", "n_clicks")],
    [
        State("self_serve_date_inputs", "start_date"),
        State("self_serve_date_inputs", "end_date"),
        State("self_serve_customer_type_dropdown", "value"),
        State("current_loggedin_email", "data"),
    ],
)
def generate_csv(n_nlicks, start_date, end_date, customer_type, current_email):

    restrict_resource(current_email)
    if n_nlicks == 0:
        return None
    data = retrieve_budget_tracking_campaigns(start_date, end_date, customer_type)
    data["has_managed_service"] = np.where(
        data["has_managed_service"] == True, "Managed", "Self serve"
    )
    data["campaign_name"] = (
        '=HYPERLINK("https://dashboard.vamp.me/dashboard/campaign/'
        + data["campaign_id"].astype(str)
        + '","'
        + data["campaign_name"]
        + '")'
    )
    data["AUD_budget"] = round(
        conversion(currency_conversions, data["currency"], "AUD") * data["budget"],
        2,
    )
    data["GBP_budget"] = np.where(data["currency"] == "GBP", data["budget"], None)
    data["EUR_budget"] = np.where(data["currency"] == "EUR", data["budget"], None)
    data["USD_budget"] = np.where(data["currency"] == "USD", data["budget"], None)
    data["sales_person"] = None
    mappings = {
        "Draft": "Campaign in Draft",
        "Ready for Shortlisting": "Campaign Live",
        "Ready for Approval": "Campaign Live",
        "Approved": "Campaign Live",
        "Active": "Campaign Live",
        "Fulfilled": "Campaign Completed",
        "Approval Required": "Campaign in Draft",
        "Rejected": "Campaign in Draft",
        "Paid": "Paid",
        "Processing": "Processing",
        "Preparing For Launch": "Preparing For Launch",
        "In Review": "Campaign in Draft",
    }
    data["campaign_status"].replace(mappings, inplace=True)
    data["value_AUD"] = None
    data["service"] = data["has_managed_service"].apply(
        lambda x: "High Touch" if x else "Low Touch"
    )
    data = data.loc[
        :,
        [
            "first_customer_flag",
            "team_name",
            "service",
            "campaign_status",
            "sales_person",
            "campaign_name",
            "value_AUD",
            "GBP_budget",
            "EUR_budget",
            "USD_budget",
            "AUD_budget",
            "start_date",
            "end_date",
        ],
    ]

    file_name = "campaign_downloads_" + str(date.today()) + ".csv"
    # Create budget columns based on Currency
    x = dcc.send_data_frame(data.to_csv, filename=file_name, index=False)
    return x


@app.callback(
    Output("marketing_download", "data"),
    [Input("marketing_download_btn", "n_clicks")],
    [
        State("self_serve_date_inputs", "start_date"),
        State("self_serve_date_inputs", "end_date"),
        State("current_loggedin_email", "data"),
    ],
)
def generate_marketing_csv(n_clicks, start_date, end_date, current_email):
    restrict_resource(current_email)
    if n_clicks == 0:
        return None
    data = fetch_marketing_downloads(start_date, end_date)
    file_name = "marketing_downloads_" + str(date.today()) + ".csv"
    # Create budget columns based on Currency
    x = dcc.send_data_frame(data.to_csv, filename=file_name, index=False)
    return x

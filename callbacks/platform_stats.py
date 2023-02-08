"""
 callbacks/campaign_lookup.py

 @ticket:	https://vampdash.atlassian.net/browse/DAS-8663
 @date:		2021-08-25
 @auth:		Mark Brackenrig <mark@vamp.me>

 @desc:
Callbacks for platform stats."""
import datetime

# Utilities
import pandas as pd

# Dash components
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Data & Components & Helpers
from components.components import *
from data.functions import *
from data.platform_stats import *
from graphs.graphs import *
from main import app

regions = [
    {
        "sub_region": "Northern America",
        "region": "Americas",
        "Vamp": "Americas",
    },
    {"sub_region": "Eastern Asia", "region": "Asia", "Vamp": "Asia"},
    {"sub_region": "Central Asia", "region": "Asia", "Vamp": "Asia"},
    {"sub_region": "Eastern Europe", "region": "Europe", "Vamp": "Europe"},
    {"sub_region": "South-eastern Asia", "region": "Asia", "Vamp": "Asia"},
    {
        "sub_region": "Latin America and the Caribbean",
        "region": "Americas",
        "Vamp": "Americas",
    },
    {"sub_region": "Western Asia", "region": "Asia", "Vamp": "MENA"},
    {"sub_region": "Northern Europe", "region": "Europe", "Vamp": "Europe"},
    {"sub_region": "Western Europe", "region": "Europe", "Vamp": "Europe"},
    {"sub_region": "Micronesia", "region": "Oceania", "Vamp": "ANZ"},
    {"sub_region": "Polynesia", "region": "Oceania", "Vamp": "ANZ"},
    {"sub_region": "Sub-Saharan Africa", "region": "Africa", "Vamp": "MENA"},
    {"sub_region": "Melanesia", "region": "Oceania", "Vamp": "ANZ"},
    {"sub_region": "Northern Africa", "region": "Africa", "Vamp": "MENA"},
    {"sub_region": "Southern Asia", "region": "Asia", "Vamp": "Asia"},
    {"sub_region": "Southern Europe", "region": "Europe", "Vamp": "Europe"},
    {
        "sub_region": "Australia and New Zealand",
        "region": "Oceania",
        "Vamp": "ANZ",
    },
]


def find_region(x, countries, regions=regions):
    """
    Converts the sub_region and region into Vamps regional classifications

    """
    # Avoids error grabbing data pre 2020
    if x is None:
        result = "multi-region"  # used this as it was the catch all already

    elif len(x.split(",")) == 1:
        region = countries.loc[countries["code"] == x].reset_index(drop=True)
        classify = [
            i["Vamp"] for i in regions if i["sub_region"] == region["sub_region"][0]
        ][0]
        result = classify

    elif len(x.split(",")) > 1:
        region = countries.loc[countries["code"].isin(x.split(","))].reset_index(
            drop=True
        )
        classify = [
            i["Vamp"]
            for i in regions
            if i["sub_region"] in region["sub_region"].tolist()
        ]
        if len(set(classify)) > 1:
            result = "multi-region"
        else:
            result = classify[0]

    else:
        result = "multi-region"

    return result


def align_financial_year(row):
    """Map year dates to financial years i.e q1 starts 01/07"""
    if row["start_quarter"] in ["quarter-1", "quarter-2"]:
        return int(row["start_year"]) + 1

    return int(row["start_year"])


countries = fetch_countries()


@app.callback(
    Output("ps-campaigns", "data"),
    [
        Input("platform_stats_date_inputs", "start_date"),
        Input("platform_stats_date_inputs", "end_date"),
        Input("platform_stats_customer_type_dropdown", "value"),
    ],
)
def get_campaign(start_date, end_date, customer_type):
    """
    Saves campaign data to state

    """
    campaigns = retrieve_campaigns(start_date, end_date, customer_type)
    campaigns["region"] = campaigns["desired_location"].apply(
        find_region, countries=countries
    )

    return campaigns.to_json(orient="split", date_format="iso")


@app.callback(
    [
        Output("cumulative_campaigns", "children"),
        Output("high_touch_low_touch", "children"),
        Output("new_customers", "children"),
        Output("revenue_by_month", "children"),
        Output("high_touch_low_touch_revenue", "children"),
        Output("longitudinal_campaign", "children"),
        Output("longitudinal_new_vs_returning_campaign", "children"),
        Output("longitudinal_new_vs_returning_customers", "children"),
    ],
    [
        Input("ps-campaigns", "data"),
        Input("platform_stats_period_filter", "value"),
    ],
)
def platform_stats_charts_charts(campaigns, period_filter):
    """
    Generates charts for platform stats page
    """

    campaigns = pd.read_json(campaigns, orient="split")
    if campaigns is None:
        raise PreventUpdate

    campaigns["start_month"] = pd.to_datetime(
        campaigns["start_month"].astype(int), format="%m"
    )
    campaigns["year-month"] = (
        campaigns["start_year"].astype(int).astype(str)
        + "-"
        + campaigns["start_month"].dt.month_name().astype(str)
    )

    campaigns["financial_year"] = campaigns.apply(align_financial_year, axis=1).astype(
        str
    )
    campaigns["year-quarter"] = (
        campaigns["financial_year"].astype(int).astype(str)
        + "-"
        + campaigns["start_quarter"]
    )
    campaigns["start_year"] = campaigns["start_year"].astype(int).astype(str)

    cum_chart = cumulative_campaigns_bar_chart(campaigns, period_filter)
    hi_lo_chart = high_touch_low_touch_bar_chart(campaigns)
    new_cust_chart = new_customers_chart(campaigns, period_filter)
    revenue_chart = cumulative_revenue_bar_chart(campaigns, period_filter)
    longitudinal_camp = cumulative_camp_service_bar_chart(campaigns, period_filter)
    service_revenue = high_touch_low_touch_revenue_chart(campaigns)
    long_new_vs_return_camp = new_vs_returning_customer_campaigns(
        campaigns, period_filter
    )
    long_new_vs_return = new_vs_returning_customers(campaigns, period_filter)

    return [
        cum_chart,
        hi_lo_chart,
        new_cust_chart,
        revenue_chart,
        service_revenue,
        longitudinal_camp,
        long_new_vs_return_camp,
        long_new_vs_return,
    ]


@app.callback(
    Output("ps_download", "data"),
    [Input("ps_download_btn", "n_clicks")],
    [State("ps-campaigns", "data"), State("current_loggedin_email", "data")],
)
def generate_csv(n_clicks, campaigns, current_email):
    """ """
    restrict_resource(current_email)

    # Only download once clicked
    if n_clicks == 0 or n_clicks is None:
        raise PreventUpdate

    campaigns = pd.read_json(campaigns, orient="split")
    if campaigns is None:
        raise PreventUpdate

    campaigns["start_month"] = pd.to_datetime(
        campaigns["start_month"].astype(int), format="%m"
    )
    campaigns["year-month"] = (
        campaigns["start_year"].astype(int).astype(str)
        + "-"
        + campaigns["start_month"].dt.month_name().astype(str)
    )

    campaigns["financial_year"] = campaigns.apply(align_financial_year, axis=1).astype(
        str
    )
    campaigns["year-quarter"] = (
        campaigns["financial_year"].astype(int).astype(str)
        + "-"
        + campaigns["start_quarter"]
    )
    campaigns["start_year"] = campaigns["start_year"].astype(int).astype(str)
    campaigns["start_month"] = campaigns["start_month"].dt.month_name().astype(str)

    # Format data and filename ready for download
    today = datetime.datetime.today()
    filename = f"platform_stats_{today.strftime('%Y_%m_%d')}.csv"

    return dcc.send_data_frame(campaigns.to_csv, filename=filename, index=False)

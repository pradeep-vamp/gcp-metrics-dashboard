import numpy as np

# import basic libraries
import pandas as pd
from dash.dependencies import Input, Output

# import App
from components.components import *
from data.financials import *

# import data functions
from data.functions import *

# import graphing functions
from graphs.graphs import *
from main import app


##### FINANCIALS ######
@app.callback(
    [
        Output("booked_revenue_chart", "children"),
        Output("booked_managed_revenue_chart", "children"),
        Output("self_serve_revenue_vb", "children"),
        Output("vamp_revenue_vb", "children"),
        Output("new_business_vb", "children"),
        Output("returning_business_vb", "children"),
        Output("new_vs_returning_business_chart", "children"),
        Output("brief_locations_chart", "children"),
        Output("ave_campaign_value_vb", "children"),
    ],
    [
        Input("finance_date_inputs", "start_date"),
        Input("finance_date_inputs", "end_date"),
        Input("currency_drop_down", "value"),
        Input("finance_customer_type_dropdown", "value"),
        Input("location_drop_down_finance", "value"),
        Input("campaign_status_drop_down", "value"),
        Input("management_drop_down", "value"),
    ],
)
def build_financial_charts(
    start_date,
    end_date,
    currency,
    customer_type,
    locations,
    campaign_status_input,
    management_input,
):
    data = fetch_booked_campaign_revenue(
        start_date, end_date, currency, customer_type, locations
    )
    if campaign_status_input == None:
        campaign_status_input = []
    if len(campaign_status_input) > 0:
        data = data.loc[data["campaign_status"].isin(campaign_status_input)]
    if management_input != "all":
        data = data.loc[data["has_managed_service"] == management_input]
    print(data)
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
    booked_revenue_chart = build_booked_revenue_chart(data)
    managed_revenue_chart = build_managed_revenue_chart(data)
    data = fetch_financials_campaigns(
        start_date,
        end_date,
        currency,
        customer_type,
        locations,
        management_input,
    )
    data["status"] = np.where(
        data["campaign_status"].isin(["draft", "rejected"]),
        "Draft",
        np.where(
            data["campaign_status"].isin(["in_review", "approval_required"]),
            "In Moderation",
            np.where(
                data["campaign_status"].isin(
                    [
                        "ready_for_shortlisting",
                        "ready_for_approval",
                        "approved",
                        "active",
                    ]
                ),
                "Active",
                np.where(
                    data["campaign_status"].isin(["fulfilled", "paid"]),
                    "Complete",
                    "Other",
                ),
            ),
        ),
    )
    if len(campaign_status_input) > 0:
        data = data.loc[data["status"].isin(campaign_status_input)].reset_index(
            drop=True
        )
    # print(str(data.loc[:,['team_type','adjusted_budget']].groupby('team_type')['adjusted_budget'].sum()))
    val = "{:,}".format(
        round(data.loc[data["team_type"] == "vamp", "adjusted_budget"].sum())
    )
    vamp_revenue = value_box("💵 ", "Vamp Revenue", val, id="vamp_revenue_value_box_fin")
    val = "{:,}".format(
        round(
            data.loc[
                data["team_type"].isin(["selfserve", "portal"]),
                "adjusted_budget",
            ].sum()
        )
    )
    selfserve_revenue = value_box(
        "💳 ", "Self Serve Revenue", val, id="self_serve_revenue_value_box_fin"
    )
    val = "{:,}".format(
        round(data.loc[data["cumulative_campaigns"] == 1, "adjusted_budget"].sum())
    )
    new_revenue = value_box("💸 ", "New Revenue", val, id="new_revenue_value_box_fin")
    val = "{:,}".format(
        round(data.loc[data["cumulative_campaigns"] > 1, "adjusted_budget"].sum())
    )
    existing_revenue = value_box(
        "💰 ", "Returning Revenue", val, id="returning_revenue_value_box_fin"
    )
    new_vs_return = new_vs_returning_business_chart(data, currency)
    briefs_locations = brief_locations_chart(data, currency)

    val = "{:,}".format(round(data["adjusted_budget"].mean()))
    ave_campaigns_value = value_box(
        "💲 ",
        "Average Campaign Value",
        val,
        id="average_campaign_value_box_fin",
    )

    return [
        booked_revenue_chart,
        managed_revenue_chart,
        selfserve_revenue,
        vamp_revenue,
        new_revenue,
        existing_revenue,
        new_vs_return,
        briefs_locations,
        ave_campaigns_value,
    ]

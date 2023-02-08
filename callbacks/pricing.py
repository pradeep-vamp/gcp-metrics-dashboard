from dash import dash_table
from dash.dependencies import Input, Output

# import basic libraries
# import App
from components.components import *

# import data functions
from data.functions import *
from data.pricing import *

# import graphing functions
from graphs.graphs import *
from main import app


##### OVERVIEW #####
@app.callback(
    [
        Output("rate_cards_dt", "children"),
    ],
    [
        Input("pricing_location_drop_down", "value"),
        Input("channel_drop_down", "value"),
        Input("event_drop_down", "value"),
        Input("currency_pricing_drop_down", "value"),
    ],
)
def rate_cards_data_table(location, channel, campaign_type, currency):
    data = retrieve_rate_cards(location, channel, campaign_type, currency)
    max_token_cost = data.groupby("criteria").max("token_cost")
    max_token_cost = max_token_cost.reset_index()
    max_token_cost["max_cost"] = max_token_cost["token_cost"]
    max_cost = max_token_cost.loc[:, ["criteria", "max_cost"]]
    print(max_cost)
    data = data.merge(max_cost, left_on="criteria", right_on="criteria")
    cols = [
        {"id": "criteria", "name": "Criteria"},
        {"id": "token_value", "name": "Token Value"},
        {"id": "max_price", "name": "Price"},
        {"id": "token_cost", "name": "Token Cost"},
        {"id": "max_cost", "name": "Max Cost", "hidden": True},
    ]

    print(data)
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
                "if": {"filter_query": "{token_cost} = {max_cost}"},
                "backgroundColor": "#fe3769",
                "color": "white",
            },
            {
                "if": {
                    "column_id": "max_cost",
                },
                "display": "None",
            },
        ],
        style_header_conditional=[
            {
                "if": {
                    "column_id": "max_cost",
                },
                "display": "None",
            }
        ],
    )

    return [data_table]


@app.callback(
    [
        Output("custom_price_boxplot", "children"),
        Output("custom_price_barchart", "children"),
    ],
    [
        Input("pricing_location_drop_down", "value"),
        Input("channel_drop_down", "value"),
        Input("event_drop_down", "value"),
        Input("currency_pricing_drop_down", "value"),
    ],
)
def build_custom_price_charts(location, channel, campaign_type, currency):
    data = custom_price_by_original_token_value(
        location, channel, campaign_type, currency
    )
    pricing_bp = pricing_boxplot(data, currency)
    pricing_bar = pricing_barchart(data, currency)
    return [pricing_bp, pricing_bar]

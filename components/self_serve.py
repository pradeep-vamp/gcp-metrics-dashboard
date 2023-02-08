from datetime import date
from datetime import datetime as dt

import dash_bootstrap_components as dbc
from dash import dcc, html

from data.functions import fetch_from_s3

sales_team = fetch_from_s3(key="metrics-dashboard/sales_team.csv")

try:
    sales_team.columns = ["value", "label"]
except ValueError:
    sales_team.assign(value="", label="")

# Determine current fiscal date
if date.today().month < 7:
    current_fiscal = dt(date.today().year - 1, 7, 1)
else:
    current_fiscal = dt(date.today().year, 7, 1)

FILTERS = dbc.Container(
    [
        dbc.Row([html.H5("Filters")], className="filter_row"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Date Range"),
                        dcc.DatePickerRange(
                            id="self_serve_date_inputs",
                            min_date_allowed=dt(2016, 7, 1),
                            max_date_allowed=dt(
                                date.today().year + 1,
                                date.today().month,
                                date.today().day,
                            ),
                            initial_visible_month=date.today(),
                            end_date=date.today(),
                            start_date=current_fiscal,
                            display_format="D-M-YYYY",
                        ),
                    ],
                    md=6,
                ),
                dbc.Col(
                    [
                        html.Label("Customer Type"),
                        dcc.Dropdown(
                            id="self_serve_customer_type_dropdown",
                            options=[
                                {"label": "All", "value": "all"},
                                {"label": "Self-serve", "value": "selfserve"},
                                {"label": "Enterprise", "value": "enterprise"},
                            ],
                            value="all",
                            placeholder="Customer Type",
                            multi=False,
                        ),
                    ],
                    md=6,
                ),
            ]
        ),
    ]
)

SELF_SERVE = dbc.Tab(
    label="Campaigns",
    children=[
        dbc.Row(
            [
                html.P(
                    "Note: Data shown on this page relates to campaigns with a start"
                    ' date, within the specified period. The "start date" is different'
                    ' to the "started on" date used on other pages - as campaigns in'
                    ' draft/rejected/moderation will not have a "started on" date.',
                    style={
                        "color": "red",
                        "font-weight": "300",
                        "font-style": "italic",
                    },
                )
            ]
        ),
        FILTERS,
        dbc.Row(
            [
                dcc.Loading(
                    type="default",
                    children=[html.Div(id="self_serve_in_draft")],
                ),
                dcc.Loading(
                    type="default",
                    children=[html.Div(id="self_serve_moderation")],
                ),
                dcc.Loading(type="default", children=[html.Div(id="self_serve_live")]),
                dcc.Loading(
                    type="default",
                    children=[html.Div(id="self_serve_complete")],
                ),
                dcc.Loading(
                    type="default",
                    children=[html.Div(id="self_serve_deleted")],
                ),
            ],
            style={"marginTop": 30, "justify-content": "space-evenly"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    [
                                        html.H5(
                                            "Number of Campaigns Performed by New"
                                            " Customers"
                                        )
                                    ]
                                ),
                                dcc.Loading(
                                    type="default",
                                    children=[
                                        dbc.CardBody(id="self_serve_campaigns_chart")
                                    ],
                                ),
                            ]
                        )
                    ],
                    md=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader([html.H5("Top Countries")]),
                                dcc.Loading(
                                    type="default",
                                    children=[
                                        dbc.CardBody(
                                            id="self_serve_top_countries_chart"
                                        )
                                    ],
                                ),
                            ]
                        )
                    ],
                    md=6,
                ),
            ],
            style={"marginTop": 30},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    [html.H5("New Customers by Time on Platform")]
                                ),
                                dcc.Loading(
                                    type="default",
                                    children=[dbc.CardBody(id="self_serve_life_cycle")],
                                ),
                            ]
                        )
                    ],
                    md=12,
                )
            ],
            style={"marginTop": 30},
        ),
        dbc.Row(
            [dbc.Col([html.Div(id="self_serve_campaigns_table")], md=12)],
            style={"marginTop": 30},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.Button(
                                    "Download campaigns",
                                    id="campaign_download_btn",
                                ),
                                dcc.Download(id="campaign_download"),
                            ]
                        )
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.Button(
                                    "Download Marketing Leads",
                                    id="marketing_download_btn",
                                ),
                                dcc.Download(id="marketing_download"),
                            ]
                        )
                    ],
                    md=3,
                ),
            ],
            style={"marginTop": 15, "marginBottom": 15},
        ),
        # Download Warning
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P(
                            "Note: If you are unable to download data you feel you"
                            " should have access to, please contact the data team",
                            style={
                                "color": "red",
                                "font-weight": "300",
                                "font-style": "italic",
                            },
                        )
                    ],
                    md=12,
                ),
            ]
        ),
        dbc.Tooltip(
            "Draft campaigns have not started yet. Rejected campaigns are campaigns"
            " that have failed moderation.",
            target="self_serve_in_draft_vb",
            placement="bottom",
        ),
        dbc.Tooltip(
            "Campaigns that require CSM review before being sent. Campaigns in"
            " moderation are likely to go ahead.",
            target="self_serve_moderation_vb",
            placement="bottom",
        ),
        dbc.Tooltip(
            "Live campaigns are campaigns that have been sent to influencers.",
            target="self_serve_live_vb",
            placement="bottom",
        ),
        dbc.Tooltip(
            "Campaigns where all allocated content has been completed.",
            target="self_serve_complete_vb",
            placement="bottom",
        ),
        dbc.Tooltip(
            "Campaigns that were deleted before going live.",
            target="self_serve_deleted_vb",
            placement="bottom",
        ),
    ],
)

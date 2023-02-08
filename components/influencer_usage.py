"""
 components/influencer_usage.py

 @ticket:   https://vampdash.atlassian.net/browse/DAS-7706
 @date:     2021-05-04
 @auth:     Daniel Stratti < daniels@vamp.me >

 @desc:
 This file is used to display the data & layout required for the
 `Influencer Usage` page. The page is split into 3 main section, high-level
 stats & graphs, table data, downloads
"""
from datetime import date
from datetime import datetime as dt

import dash_bootstrap_components as dbc
from dash import dcc, html

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
                            id="influencer_usage_date_inputs",
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
                )
            ]
        ),
    ]
)


# Influencer Usage Page
INFLUENCER_USAGE = dbc.Tab(
    label="Influencer Usage",
    children=[
        # dcc.Store(id='iu-dataset'), # Store the ifluencer usage data once
        dbc.Row([FILTERS]),
        # Disclaimer
        dbc.Row(
            [
                html.P(
                    "Note: Data shown on this page relates to campaigns with that start"
                    " within the specified period.",
                    style={
                        "color": "red",
                        "font-weight": "300",
                        "font-style": "italic",
                    },
                )
            ]
        ),
        # High level stats & graph
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.Label("Team", style={"paddingTop": "1em"}),
                                dcc.Dropdown(id="iu_sales_team_drop_down", value="-1"),
                                html.Label(
                                    "Service Level",
                                    style={"paddingTop": "1em"},
                                ),
                                dcc.Dropdown(
                                    id="service_level_drop_down",
                                    options=[
                                        {"label": "All", "value": "all"},
                                        {"label": "High Touch", "value": True},
                                        {"label": "Low Touch", "value": False},
                                    ],
                                    value="all",
                                ),
                                html.Label("Region", style={"paddingTop": "1em"}),
                                dcc.Dropdown(id="iu_region_drop_down", value="-1"),
                            ],
                            style={"padding": "1em", "marginBottom": "1.5em"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            type="default",
                                            children=[html.Div(id="iu_50_percent")],
                                        )
                                    ],
                                    md=6,
                                ),
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            type="default",
                                            children=[html.Div(id="iu_success_rate")],
                                        )
                                    ],
                                    md=6,
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            type="default",
                                            children=[
                                                html.Div(id="iu_avg_similarity_won")
                                            ],
                                        )
                                    ],
                                    md=6,
                                ),
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            type="default",
                                            children=[
                                                html.Div(id="iu_avg_similarity_lost")
                                            ],
                                        )
                                    ],
                                    md=6,
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            type="default",
                                            children=[
                                                html.Div(id="iu_avg_engagement_won")
                                            ],
                                        )
                                    ],
                                    md=6,
                                ),
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            type="default",
                                            children=[
                                                html.Div(id="iu_avg_engagement_lost")
                                            ],
                                        )
                                    ],
                                    md=6,
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            type="default",
                                            children=[html.Div(id="iu_avg_local_won")],
                                        )
                                    ],
                                    md=6,
                                ),
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            type="default",
                                            children=[html.Div(id="iu_avg_local_lost")],
                                        )
                                    ],
                                    md=6,
                                ),
                            ]
                        ),
                    ],
                    md=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    [html.H5("Campaign Vs Influencer (Proportion)")]
                                ),
                                dcc.Loading(
                                    type="default",
                                    children=[dbc.CardBody(id="iu_campaigns_chart")],
                                ),
                            ]
                        )
                    ],
                    md=6,
                ),
            ]
        ),
        # Table
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Loading(
                            type="default",
                            children=[html.Div(id="iu_campaigns_table")],
                        )
                    ],
                    md=12,
                )
            ],
            style={"marginTop": 30},
        ),
        # Downloads
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.Button(
                                    "Download campaigns",
                                    id="iu_stats_download_btn",
                                ),
                                dcc.Loading(
                                    type="default",
                                    children=[dcc.Download(id="iu_stats_download")],
                                ),
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
    ],
)

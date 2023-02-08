"""
 components/platform_stats.py

 @ticket:   https://vampdash.atlassian.net/browse/DAS-8663
 @date:     2021-08-26
 @auth:     Mark Brackenrig < mark@vamp.me >

 @desc:
 Used to display key platform stats
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
                            id="platform_stats_date_inputs",
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
                    md=4,
                ),
                dbc.Col(
                    [
                        html.Label("Customer Type"),
                        dcc.Dropdown(
                            id="platform_stats_customer_type_dropdown",
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
                    md=4,
                ),
                dbc.Col(
                    [
                        html.Label("Display Periods"),
                        dcc.Dropdown(
                            id="platform_stats_period_filter",
                            options=[
                                {"label": "Monthly", "value": "monthly"},
                                {"label": "Quarterly", "value": "quarterly"},
                                {"label": "Financial Year", "value": "yearly"},
                            ],
                            value="monthly",
                            placeholder="Display Periods",
                            multi=False,
                        ),
                    ],
                    md=4,
                ),
            ]
        ),
    ]
)


# Influencer Usage Page
PLATFORM_STATS = dbc.Tab(
    label="Platform Statistics",
    children=[
        # DATA
        dcc.Store(id="ps-campaigns"),
        FILTERS,
        # Row 1
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader([html.H5("Cumulative Campaigns")]),
                            dcc.Loading(
                                type="default",
                                children=[dbc.CardBody(id="cumulative_campaigns")],
                            ),
                        ]
                    ),
                    md=12,
                )
            ],
            style={"marginTop": 30},
        ),
        # Row 2
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader([html.H5("New Customers")]),
                            dcc.Loading(
                                type="default",
                                children=[dbc.CardBody(id="new_customers")],
                            ),
                        ]
                    ),
                    md=12,
                )
            ],
            style={"marginTop": 30},
        ),
        # Row 3
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader([html.H5("Campaigns by Service Level")]),
                                dcc.Loading(
                                    type="default",
                                    children=[dbc.CardBody(id="high_touch_low_touch")],
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
                                dbc.CardHeader([html.H5("Revenue by Service Level")]),
                                dcc.Loading(
                                    type="default",
                                    children=[
                                        dbc.CardBody(id="high_touch_low_touch_revenue")
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
        # Row 4
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader([html.H5("Revenue By Period")]),
                            dcc.Loading(
                                type="default",
                                children=[dbc.CardBody(id="revenue_by_month")],
                            ),
                        ]
                    ),
                    md=12,
                )
            ],
            style={"marginTop": 30},
        ),
        # Row 5
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [html.H5("Period Campaigns By Service Level")]
                            ),
                            dcc.Loading(
                                type="default",
                                children=[dbc.CardBody(id="longitudinal_campaign")],
                            ),
                        ]
                    ),
                    md=12,
                )
            ],
            style={"marginTop": 30},
        ),
        # Row 6
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.H5(
                                        "Period Campaigns By New vs Returning Customers"
                                    )
                                ]
                            ),
                            dcc.Loading(
                                type="default",
                                children=[
                                    dbc.CardBody(
                                        id="longitudinal_new_vs_returning_campaign"
                                    )
                                ],
                            ),
                        ]
                    ),
                    md=12,
                )
            ],
            style={"marginTop": 30},
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [html.H5("Period New vs Returning Customers")]
                            ),
                            dcc.Loading(
                                type="default",
                                children=[
                                    dbc.CardBody(
                                        id="longitudinal_new_vs_returning_customers"
                                    )
                                ],
                            ),
                        ]
                    ),
                    md=12,
                )
            ],
            style={"marginTop": 30},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button("Download Data", id="ps_download_btn"),
                        dcc.Loading(
                            id="ps_download_loading",
                            type="default",
                            children=[dcc.Download(id="ps_download")],
                        ),
                    ]
                )
            ],
            style={"marginTop": 30},
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

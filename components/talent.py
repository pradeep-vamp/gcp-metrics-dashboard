from datetime import date
from datetime import datetime as dt

import dash_bootstrap_components as dbc
from dash import dcc, html

from components.segmentation import active_countries

# Determin current fiscal date
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
                            id="talent_date_inputs",
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
                        html.Label("Location"),
                        dcc.Dropdown(
                            id="talent_location_drop_down",
                            options=active_countries.to_dict("records"),
                            multi=True,
                        ),
                    ],
                    md=4,
                ),
            ]
        ),
    ]
)


TALENT = dbc.Tab(
    label="Talent Analysis",
    children=[
        dcc.Store(id="new-talent-data"),
        FILTERS,
        dbc.Row(
            [
                dbc.Col(
                    dcc.Loading(
                        type="default",
                        children=[html.Div(id="talent_value_box")],
                    ),
                    md=3,
                ),
                dbc.Col(
                    dcc.Loading(
                        type="default",
                        children=[html.Div(id="talent_application_value_box")],
                    ),
                    md=3,
                ),
                dbc.Col(
                    dcc.Loading(
                        type="default",
                        children=[html.Div(id="approached_value_box")],
                    ),
                    md=3,
                ),
                dbc.Col(
                    dcc.Loading(
                        type="default",
                        children=[html.Div(id="approval_requested_value_box")],
                    ),
                    md=3,
                ),
            ],
            id="talent_value_box_row",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader([html.H5("New Talent")]),
                                dcc.Loading(
                                    type="default",
                                    children=[dbc.CardBody(id="new_talent_graph")],
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
                                dbc.CardHeader(
                                    [html.H5("Number of Campaign Applications")]
                                ),
                                dcc.Loading(
                                    type="default",
                                    children=[
                                        dbc.CardBody(id="campaigns_applied_for_graph")
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
                                    [
                                        html.H5(
                                            "New Talent Locations",
                                            id="talent_locations_header",
                                        )
                                    ]
                                ),
                                dcc.Loading(
                                    type="default",
                                    children=[
                                        dbc.CardBody(id="talent_location_charts")
                                    ],
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
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader([html.H5("Response to Briefs")]),
                                dcc.Loading(
                                    type="default",
                                    children=[dbc.CardBody(id="brief_response_charts")],
                                ),
                            ]
                        )
                    ],
                    md=12,
                )
            ],
            style={"marginTop": 30},
        ),
        dbc.Tooltip(
            "Talent added to the platform who have since been approved - regardless of"
            " whether they were approached or approval requested. Based on date when a"
            " talent joined, not when they were approved.",
            target="talent_value_box",
            placement="bottom",
        ),
        dbc.Tooltip(
            "Talent added to the platform who have since been approved AND applied for"
            " a campaign.",
            target="talent_application_value_box",
            placement="bottom",
        ),
        dbc.Tooltip(
            "Total talent approached during the time period, regardless of whether they"
            " have been successfully onboarded or not.",
            target="approached_value_box",
            placement="bottom",
        ),
        dbc.Tooltip(
            'Total talent entering "approval requested" status - regardless of whether'
            " they were subsequently approved,rejected or have not been assessed.",
            target="approval_requested_value_box",
            placement="bottom",
        ),
        dbc.Tooltip(
            "Approved influencers have been split by their joining channel.",
            target="talent_locations_header",
            placement="bottom",
        ),
    ],
)

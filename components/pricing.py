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
                        html.Label("Location"),
                        dcc.Dropdown(
                            id="pricing_location_drop_down",
                            options=active_countries.to_dict("records"),
                            multi=True,
                        ),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.Label("Channel"),
                        dcc.Dropdown(
                            id="channel_drop_down",
                            options=[
                                {"label": "Instagram", "value": "instagram"},
                                {"label": "Tiktok", "value": "tiktok"},
                                {"label": "Youtube", "value": "youtube"},
                            ],
                            multi=False,
                        ),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.Label("Campaign Type"),
                        dcc.Dropdown(
                            id="event_drop_down",
                            options=[
                                {"label": "Social", "value": "social"},
                                {"label": "Event", "value": "event"},
                                {"label": "Content Only", "value": "content"},
                            ],
                            multi=False,
                            value="social",
                        ),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.Label("Currency"),
                        dcc.Dropdown(
                            id="currency_pricing_drop_down",
                            options=[
                                {"label": "$ AUD", "value": "AUD"},
                                {"label": "$ USD", "value": "USD"},
                                {"label": "$ SGD", "value": "SGD"},
                                {"label": "¥ JPY", "value": "JPY"},
                                {"label": "‎€ EUR", "value": "EUR"},
                                {"label": "£ GBP", "value": "GBP"},
                            ],
                            value="AUD",
                            multi=False,
                        ),
                    ],
                    md=3,
                ),
            ]
        ),
    ]
)

PRICING = dbc.Tab(
    label="Talent Pricing",
    children=[  # dcc.Store(id='new-talent-data'),
        FILTERS,
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    [html.H5("Custom Price by Original Token")]
                                ),
                                dcc.Loading(
                                    type="default",
                                    children=[dbc.CardBody(id="custom_price_boxplot")],
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
                                    [html.H5("Selected Deliverables by Token Value")]
                                ),
                                dcc.Loading(
                                    type="default",
                                    children=[dbc.CardBody(id="custom_price_barchart")],
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
                                dbc.CardHeader([html.H5("Rate Cards")]),
                                dcc.Loading(
                                    type="default",
                                    children=[dbc.CardBody(id="rate_cards_dt")],
                                ),
                            ]
                        )
                    ],
                    md=12,
                )
            ],
            style={"marginTop": 30},
        ),
    ],
)

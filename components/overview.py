from datetime import date
from datetime import datetime as dt

import dash_bootstrap_components as dbc
from dash import dcc, html

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
                            id="overview_date_inputs",
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
                            id="overview_customer_type_dropdown",
                            options=[
                                {"label": "All", "value": "all"},
                                {"label": "Vamp", "value": "vamp"},
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


OVERVIEW = dbc.Tab(
    label="Overview",
    children=[
        FILTERS,
        html.P(
            "Note: Data shown on this page relates to campaigns with a started on date"
            " within the specified period",
            style={
                "color": "red",
                "font-weight": "300",
                "font-style": "italic",
            },
        ),
        dbc.Row(
            [
                dbc.Col([html.Div(id="self_serve_vb")], md=3),
                dbc.Col([html.Div(id="ave_talent_per_campaign")], md=3),
                dbc.Col([html.Div(id="ave_deliverables_per_campaign")], md=3),
                dbc.Col([html.Div(id="ave_time_in_draft")], md=3),
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
                                            "Location of Opportunities - Number of"
                                            " Campaigns"
                                        )
                                    ]
                                ),
                                dcc.Loading(
                                    id="loading-1",
                                    type="default",
                                    children=[
                                        dbc.CardBody(id="campaign_locations_map")
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
                                dbc.CardHeader(
                                    [
                                        html.H5(
                                            "Deliverables by Content Type",
                                            id="deliverables_chart_title",
                                        )
                                    ]
                                ),
                                dcc.Loading(
                                    id="loading-2",
                                    type="default",
                                    children=[
                                        dbc.CardBody(id="deliverable_type_chart")
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
                                    [html.H5("Number of Campaigns by Status")]
                                ),
                                dcc.Loading(
                                    id="loading-3",
                                    type="default",
                                    children=[dbc.CardBody(id="status_chart")],
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
                                dbc.CardHeader([html.H5("Time in Draft")]),
                                dcc.Loading(
                                    id="loading-4",
                                    type="default",
                                    children=[dbc.CardBody(id="draft_times_chart")],
                                ),
                            ]
                        )
                    ],
                    md=6,
                ),
            ],
            style={"marginTop": 30},
        ),
        dbc.Tooltip(
            "A customer must have at least 1 campaign with a started on date in the"
            " period specified. Portal customers are considered to be self serve.",
            target="self_serve_vb",
            placement="bottom",
        ),
        dbc.Tooltip(
            "In campaigns with a started on date within the period specified",
            target="deliverables_chart_title",
            placement="right",
        ),
        dbc.Tooltip(
            "Time difference between when a campaign was created and when briefs were"
            " sent to talent.",
            target="ave_time_in_draft",
            placement="bottom",
        ),
        dbc.Tooltip(
            "Average number of deliverables allocated to talent in a campaign.",
            target="ave_deliverables_per_campaign",
            placement="bottom",
        ),
        dbc.Tooltip(
            "Average number of talent in a campaign.",
            target="ave_talent_per_campaign",
            placement="bottom",
        ),
    ],
)

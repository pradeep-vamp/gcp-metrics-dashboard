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
                            id="finance_date_inputs",
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
                            id="finance_customer_type_dropdown",
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


FINANCE = dbc.Tab(
    label="Financials",
    children=[
        html.P(
            "Note: Data shown on this page relates to campaigns with a started on date"
            " within the specified period. Only live and completed campaigns are"
            " displayed here.",
            style={
                "color": "red",
                "font-weight": "300",
                "font-style": "italic",
            },
        ),
        FILTERS,
        ### Filters ###
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Currency"),
                        dcc.Dropdown(
                            id="currency_drop_down",
                            options=[
                                {"label": "$ AUD", "value": "AUD"},
                                {"label": "$ USD", "value": "USD"},
                                {"label": "$ SGD", "value": "SGD"},
                                {"label": "¥ JPY", "value": "JPY"},
                                {"label": "‎€ EUR", "value": "EUR"},
                                {"label": "£ GBP", "value": "GBP"},
                            ],
                            value="AUD",
                        ),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.H5("Locations"),
                        dcc.Dropdown(
                            id="location_drop_down_finance",
                            options=active_countries.to_dict("records"),
                            multi=True,
                        ),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.H5("Management"),
                        dcc.Dropdown(
                            id="management_drop_down",
                            options=[
                                {"label": "Vamp Managed", "value": True},
                                {"label": "Self Managed", "value": False},
                                {"label": "All", "value": "all"},
                            ],
                            value="all",
                        ),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.H5("Campaign Status"),
                        dcc.Dropdown(
                            id="campaign_status_drop_down",
                            options=[
                                {"label": "Active", "value": "Active"},
                                {"label": "Draft", "value": "Draft"},
                                {"label": "Complete", "value": "Complete"},
                            ],
                            multi=True,
                        ),
                    ],
                    md=3,
                ),
            ],
            style={"marginTop": 30},
        ),
        ### Value Box Row ###
        dcc.Loading(
            id="new_vs_returning_stats_loading",
            type="default",
            children=[
                dbc.Row(
                    [
                        html.Div(id="self_serve_revenue_vb"),
                        html.Div(id="vamp_revenue_vb"),
                        html.Div(id="new_business_vb"),
                        html.Div(id="returning_business_vb"),
                        html.Div(id="ave_campaign_value_vb"),
                    ],
                    style={"marginTop": 30},
                )
            ],
            style={"width": "100%"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader([html.H5("New vs Returning Business")]),
                                dcc.Loading(
                                    id="new_vs_returning_loading",
                                    type="default",
                                    children=[
                                        dbc.CardBody(
                                            id="new_vs_returning_business_chart"
                                        )
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
                                            "Brief Location",
                                            id="brief_location_chart_title",
                                        )
                                    ]
                                ),
                                dcc.Loading(
                                    id="brief_location_loading",
                                    type="default",
                                    children=[dbc.CardBody(id="brief_locations_chart")],
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
                                    [html.H5("Monthly Revenue by Campaign Status")]
                                ),
                                dcc.Loading(
                                    id="monthly_revenue_loading",
                                    type="default",
                                    children=[dbc.CardBody(id="booked_revenue_chart")],
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
                                dbc.CardHeader(
                                    [html.H5("Monthly Revenue by Managed Service")]
                                ),
                                dcc.Loading(
                                    id="monthly_managed_revenue_loading",
                                    type="default",
                                    children=[
                                        dbc.CardBody(id="booked_managed_revenue_chart")
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
        dbc.Tooltip(
            "Budget is split evenly across multi-country campaigns",
            target="brief_location_chart_title",
            placement="top",
        ),
        dbc.Tooltip(
            "Total budget for all teams except for the Vamp team.",
            target="self_serve_revenue_value_box_fin",
            placement="bottom",
        ),
        dbc.Tooltip(
            "Total budget allocated to the vamp team. Currently the Vamp team is not in"
            " operation",
            target="vamp_revenue_value_box_fin",
            placement="bottom",
        ),
        dbc.Tooltip(
            "Budget from a teams first campaign.",
            target="new_revenue_value_box_fin",
            placement="bottom",
        ),
        dbc.Tooltip(
            "Budget from all campaigns except for a teams first campaign.",
            target="returning_revenue_value_box_fin",
            placement="bottom",
        ),
        dbc.Tooltip(
            "The average budget for a campaign.",
            target="average_campaign_value_box_fin",
            placement="bottom",
        ),
    ],
)

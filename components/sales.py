import dash_bootstrap_components as dbc
from dash import dcc, html

from data.functions import self_serve_customers

self_serve_customers.columns = ["value", "label"]

SALES_INPUT = dbc.Tab(
    label="Sales Input",
    children=[
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P(
                            "Note: Customer type has no effect on this page.",
                            style={
                                "color": "red",
                                "font-weight": "300",
                                "font-style": "italic",
                            },
                        ),
                        html.Label("Customer"),
                        dcc.Dropdown(
                            id="sales_input_drop_down",
                            options=self_serve_customers.to_dict("records"),
                            value=1,
                        ),
                    ],
                    md=3,
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader([html.H5("Add Sales Person")]),
                                dcc.Loading(
                                    type="default",
                                    children=[
                                        dbc.CardBody(
                                            id="sales_team_input_body",
                                            children=[
                                                dcc.Input(
                                                    id="sales_team_input",
                                                    placeholder="add sales team",
                                                    type="text",
                                                ),
                                                html.Button(
                                                    "Add Sales Person",
                                                    id="add_sales_person",
                                                    n_clicks=0,
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ]
                        )
                    ],
                    width={"size": 8, "offset": 2},
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
                                dbc.CardHeader([html.H5("Edited Associated Sales")]),
                                dcc.Loading(
                                    type="default",
                                    children=[dbc.CardBody(id="sales_input_card")],
                                ),
                            ]
                        )
                    ],
                    width={"size": 8, "offset": 2},
                )
            ],
            style={"marginTop": 30},
        ),
    ],
)

import dash_bootstrap_components as dbc
from dash import dcc, html

from components.campaign_lookup import *
from components.finance import *
from components.influencer_lookup import *
from components.influencer_usage import *
from components.overview import *
from components.pandacop import *
from components.platform_stats import *
from components.pricing import *
from components.segmentation import *
from components.self_serve import *
from components.talent import *

LOGO = "https://s3-eu-west-1.amazonaws.com/servalan-assets/teams/vamp/logo.png?v=1596611011"

LOGIN_PAGE = dbc.Container(
    children=[
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader([html.H5("Login")]),
                    dbc.CardBody(
                        [
                            dbc.Row(html.P("Email")),
                            dbc.Row(
                                dcc.Input(
                                    id="email_input",
                                    placeholder="email",
                                    type="email",
                                )
                            ),
                            dbc.Row(html.P("Password"), style={"marginTop": 30}),
                            dbc.Row(
                                dcc.Input(
                                    id="password_input",
                                    placeholder="password",
                                    type="password",
                                )
                            ),
                            dbc.Row(
                                [html.Button("Submit", id="submit-val", n_clicks=0)],
                                style={"marginTop": 30},
                            ),
                        ]
                    ),
                ]
            ),
            md={"offset": 3, "size": 6},
            style={"marginTop": 50},
        )
    ]
)

FAILED_LOGIN_PAGE = dbc.Container(
    children=[
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader([html.H5("Login")]),
                    dbc.CardBody(
                        [
                            dbc.Row(html.P("Email")),
                            dbc.Row(
                                dcc.Input(
                                    id="email_input",
                                    placeholder="email",
                                    type="email",
                                )
                            ),
                            dbc.Row(html.P("Password"), style={"marginTop": 30}),
                            dbc.Row(
                                dcc.Input(
                                    id="password_input",
                                    placeholder="password",
                                    type="password",
                                )
                            ),
                            dbc.Row(
                                [html.Button("Submit", id="submit-val", n_clicks=0)],
                                style={"marginTop": 30},
                            ),
                            dbc.Row(
                                html.P(
                                    "Sorry, the email & password provided are"
                                    " incorrect.",
                                    style={"color": "red"},
                                )
                            ),
                        ]
                    ),
                ]
            ),
            md={"offset": 3, "size": 6},
            style={"marginTop": 50},
        )
    ]
)


NAVBAR = dbc.Navbar(
    children=[
        # Use row and col to control vertical alignment of logo / brand
        dbc.Row(
            [
                dbc.Col(html.Img(src=LOGO, height="50px")),
                dbc.Col(
                    dbc.NavbarBrand(
                        "Vamp Dashboard",
                        className="ml-2 g-0",
                        style={"color": "#000", "padding-left": "20px"},
                    )
                ),
            ],
            align="center",
        )
    ],
    color="white",
    dark=True,
    sticky="top",
    style={
        "box-shadow": "0 2px 4px 0 rgba(0, 0, 0, .1)",
        "height": "71px",
        "padding-left": "20%",
    },
)


BODY = dbc.Container(
    [
        dcc.Tabs(
            id="tabs",
            children=[
                OVERVIEW,
                PLATFORM_STATS,
                PRICING,
                TALENT,
                SELF_SERVE,
                CAMPAIGN_LOOKUP,
                FINANCE,
                MISC,
                PANDACOP,
                INFLUENCER_USAGE,
                INFLUENCER_LOOKUP,
            ],
            style={"marginTop": 30, "width": "100%"},
        )
    ]
)

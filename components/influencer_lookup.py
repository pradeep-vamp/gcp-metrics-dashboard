"""
 components/influencer_lookup.py

 @ticket:   https://vampdash.atlassian.net/browse/DAS-7704
 @date:     2021-05-10
 @auth:     Daniel Stratti < daniels@vamp.me >

 @desc:
 This file is used to display the data & layout required for the
 `Influencer Lookup` page. The page is split into 3 main section, high-level
 demographics, campaign interactions, Audience insights
"""
from datetime import date
from datetime import datetime as dt

import dash_bootstrap_components as dbc
from dash import dcc, html

from data.influencer_lookup import fetch_social_accounts

# Determin current fiscal date
if date.today().month < 7:
    current_fiscal = dt(date.today().year - 1, 7, 1)
else:
    current_fiscal = dt(date.today().year, 7, 1)

social_accounts = fetch_social_accounts()

try:
    social_accounts.columns = ["value", "label"]
except ValueError:
    social_accounts.assign(value="", label="")
except Exception as e:
    print(e)

# Influencer Usage Page
INFLUENCER_LOOKUP = dbc.Tab(
    label="Influencer Lookup",
    children=[
        dcc.Store(id="il-brief-dataset"),  # Store the briefs
        dcc.Store(id="il-distribution-dataset"),  # Store the distirbutions
        dcc.Store(
            id="il-current-dataset"
        ),  # Store the current demogs (some maybe from APIs)
        # Disclaimer
        dbc.Row(id="il-warning-section", style={"justify-content": "center"}),
        # High-level Demographics
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.Label(
                                    "Select a social account",
                                    style={"paddingTop": "1em"},
                                ),
                                dcc.Dropdown(
                                    id="il_influencer_drop_down",
                                    options=social_accounts.to_dict("records"),
                                ),
                            ],
                            style={
                                "padding": "0.25em",
                                "marginBottom": "1.5em",
                            },
                        ),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        dcc.Loading(
                            type="default",
                            children=[html.Div(id="il_member_since")],
                        )
                    ],
                    md=3,
                ),
                dbc.Col(
                    [dcc.Loading(type="default", children=[html.Div(id="il_status")])],
                    md=3,
                ),
                dbc.Col(
                    [
                        dcc.Loading(
                            type="default",
                            children=[html.Div(id="il_country")],
                        )
                    ],
                    md=3,
                ),
            ],
            style={"margin": "1em"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Loading(
                            type="default",
                            children=[html.Div(id="il_engagement")],
                        )
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        dcc.Loading(
                            type="default",
                            children=[html.Div(id="il_followers")],
                        )
                    ],
                    md=3,
                ),
                dbc.Col(
                    [dcc.Loading(type="default", children=[html.Div(id="il_age")])],
                    md=3,
                ),
                dbc.Col(
                    [dcc.Loading(type="default", children=[html.Div(id="il_gender")])],
                    md=3,
                ),
            ]
        ),
        # Campaign Interactions
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dcc.Loading(
                                    type="default",
                                    children=[html.Div(id="il_brief_table")],
                                )
                            ]
                        )
                    ],
                    md=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader([html.H5("Proportion of Briefs")]),
                                dbc.CardBody(
                                    [
                                        dcc.DatePickerRange(
                                            id="il_date_inputs",
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
                                        dcc.Loading(
                                            type="default",
                                            children=[html.Div(id="il_brief_graph")],
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ],
                    md=6,
                ),
            ],
            style={"margin": "1em 0"},
        ),
        # Distributions
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            children=[
                                dbc.Tabs(
                                    children=[
                                        dbc.Tab(
                                            label="Cohort Comparison",
                                            children=[
                                                # Rate card details
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dcc.Loading(
                                                                    type="default",
                                                                    children=[
                                                                        html.H2(
                                                                            id="il-token-value",
                                                                            style={
                                                                                "text-align": "center",
                                                                                "font-size": "1rem",
                                                                            },
                                                                        )
                                                                    ],
                                                                )
                                                            ],
                                                            md=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dcc.Loading(
                                                                    type="default",
                                                                    children=[
                                                                        html.H2(
                                                                            id="il-criteria",
                                                                            style={
                                                                                "text-align": "center",
                                                                                "font-size": "1rem",
                                                                            },
                                                                        )
                                                                    ],
                                                                )
                                                            ],
                                                            md=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dcc.Loading(
                                                                    type="default",
                                                                    children=[
                                                                        html.H2(
                                                                            id="il-range",
                                                                            style={
                                                                                "text-align": "center",
                                                                                "font-size": "1rem",
                                                                            },
                                                                        )
                                                                    ],
                                                                )
                                                            ],
                                                            md=4,
                                                        ),
                                                    ],
                                                    style={"padding": "1em"},
                                                ),
                                                # distributions
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Tabs(
                                                                    children=[
                                                                        dbc.Tab(
                                                                            label=(
                                                                                "Engagement"
                                                                                " Rate"
                                                                            ),
                                                                            id="il-engagement-distribution",
                                                                        ),
                                                                        dbc.Tab(
                                                                            label="Followers",
                                                                            id="il-followers-distribution",
                                                                        ),
                                                                        dbc.Tab(
                                                                            label="Follows",
                                                                            id="il-follows-distribution",
                                                                        ),
                                                                        dbc.Tab(
                                                                            label=(
                                                                                "Media"
                                                                                " Count"
                                                                            ),
                                                                            id="il-media-distribution",
                                                                        ),
                                                                    ],
                                                                    style={
                                                                        "z-index": "1"
                                                                    },
                                                                )
                                                            ],
                                                            md=12,
                                                        )
                                                    ],
                                                    style={"padding": "1em"},
                                                ),
                                                # Note
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                html.P(
                                                                    "The distributions"
                                                                    " above are created"
                                                                    " based on the"
                                                                    " influencers who"
                                                                    " fall under the"
                                                                    " same rate card."
                                                                    " The red verticle"
                                                                    " line represents"
                                                                    " this influencers"
                                                                    " location in the"
                                                                    " distributions",
                                                                    style={
                                                                        "color": "red",
                                                                        "font-weight": (
                                                                            "300"
                                                                        ),
                                                                        "font-style": (
                                                                            "italic"
                                                                        ),
                                                                        "font-size": (
                                                                            "9px"
                                                                        ),
                                                                        "padding": (
                                                                            "12px"
                                                                        ),
                                                                    },
                                                                )
                                                            ],
                                                            md=12,
                                                        )
                                                    ]
                                                ),
                                            ],
                                        ),
                                        dbc.Tab(
                                            label="Social Audience",
                                            children=[
                                                dcc.Loading(
                                                    type="default",
                                                    children=[
                                                        html.Div(
                                                            id="il_audience_graph",
                                                            style={"padding": "1em"},
                                                        )
                                                    ],
                                                )
                                            ],
                                        ),
                                    ]
                                )
                            ]
                        )
                    ],
                    md=12,
                )
            ]
        ),
        # Downloads
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Button(
                                    "Download Influencers",
                                    id="il_stats_download_btn",
                                ),
                                dcc.Loading(
                                    id="il_stats_download_loading",
                                    type="default",
                                    children=[dcc.Download(id="il_stats_download")],
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

"""
 components/campaign_lookup.py

 @ticket:   https://vampdash.atlassian.net/browse/DAS-7702
 @date:     2021-07-28
 @auth:     Daniel Stratti < daniels@vamp.me >

 @desc:
 This file is used to display the data & layout required for the
 `Campaign Lookup` page. The page is split into 3 main section, search
 stats-details, table data, downloads
"""
import dash_bootstrap_components as dbc
from dash import dcc, html

# Influencer Usage Page
CAMPAIGN_LOOKUP = dbc.Tab(
    label="Campaign Lookup",
    children=[
        dcc.Store(id="cl-campaigns"),  # Store the the campaign data
        # Disclaimer
        # Campaign Search, Brief overview & campaign details
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.Label("Campaign", style={"paddingTop": "1em"}),
                                dbc.Input(
                                    id="cl_campaign_search",
                                    type="text",
                                    list="cl_campaign_suggestions",
                                    value="",
                                    placeholder="Search for campaigns by ID or Name",
                                    style={"width": "100%"},
                                ),
                                html.Datalist(
                                    id="cl_campaign_suggestions", children=[]
                                ),
                            ],
                            style={"padding": "1em", "marginBottom": "1.5em"},
                        ),
                        # Brief overview
                        dbc.Card(
                            [
                                dbc.CardHeader([html.H5("Briefs")]),
                                dcc.Loading(
                                    type="default",
                                    children=[dbc.CardBody(id="cl_briefs_chart")],
                                ),
                            ]
                        ),
                    ],
                    md=6,
                ),
                # Campaign details
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader([html.H5("Campaign Details")]),
                                dcc.Loading(
                                    type="default",
                                    children=[html.Div(id="cl_campaign_details_table")],
                                ),
                            ]
                        )
                    ],
                    md=6,
                ),
            ]
        ),
        # Influencer Table
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Loading(
                            type="default",
                            children=[html.Div(id="cl_influencer_table")],
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
                                    id="cl_influencer_download_btn",
                                ),
                                dcc.Download(id="cl_influencer_download"),
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

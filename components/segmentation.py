import dash_bootstrap_components as dbc
from dash import dcc, html

from data.functions import fetch_active_categories, fetch_active_countries

active_countries = fetch_active_countries()
active_categories = fetch_active_categories()
try:
    active_countries.columns = ["value", "label"]
    active_categories.columns = ["value", "label"]
except ValueError:
    active_countries.assign(value="", label="")
    active_categories.assign(value="", label="")

# Influecner table
INFLUECNER_TAB = html.Div(
    [
        # Influencer Table
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Loading(
                            type="default",
                            children=[html.Div(id="s_influencer_table")],
                        )
                    ],
                    md=12,
                )
            ],
            style={"marginTop": 30},
        ),
    ]
)

# Charts
CHARTS_TAB = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader([html.H5("Gender")]),
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            id="gender_chart_loading",
                                            type="default",
                                            children=[dbc.CardBody(id="gender_chart")],
                                        )
                                    ]
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
                                dbc.CardHeader([html.H5("Age")]),
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            id="age_chart_loading",
                                            type="default",
                                            children=[dbc.CardBody(id="age_chart")],
                                        )
                                    ]
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
                                dbc.CardHeader([html.H5("Followers")]),
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            id="followers_chart_loading",
                                            type="default",
                                            children=[
                                                dbc.CardBody(id="followers_chart")
                                            ],
                                        )
                                    ]
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
                                dbc.CardHeader([html.H5("Engagement Rate")]),
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            id="er_chart_loading",
                                            type="default",
                                            children=[dbc.CardBody(id="er_chart")],
                                        )
                                    ]
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
                                dbc.CardHeader([html.H5("Location")]),
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            id="locations_map_loading",
                                            type="default",
                                            children=[dbc.CardBody(id="locations_map")],
                                        )
                                    ]
                                ),
                            ]
                        )
                    ],
                    md=12,
                )
            ],
            style={"marginTop": 30, "marginBottom": 30},
        ),
    ]
)


# Page
MISC = dbc.Tab(
    label="Segmentation Tool",
    children=[
        # Rows of Filters
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Location"),
                        dcc.Dropdown(
                            id="location_drop_down",
                            options=active_countries.to_dict("records"),
                            multi=True,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        html.H5("Gender"),
                        dcc.Dropdown(
                            id="gender_drop_down",
                            options=[
                                {"label": "Male", "value": "male"},
                                {"label": "Female", "value": "female"},
                                {"label": "Unknown/Other", "value": "unknown"},
                            ],
                            multi=True,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        html.H5("Categories", id="categories_label"),
                        dcc.Dropdown(
                            id="categories_drop_down",
                            options=active_categories.to_dict("records"),
                            multi=True,
                        ),
                    ],
                    md=4,
                ),
            ],
            style={"marginTop": 30},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Age"),
                        dcc.RangeSlider(
                            id="age_slider",
                            marks={
                                1: "Under 18",
                                2: "18-24",
                                3: "25-35",
                                4: "Over 35",
                            },
                            value=[1, 4],
                            min=1,
                            max=4,
                            step=1,
                        ),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.H5("Followers"),
                        dcc.RangeSlider(
                            id="followers_slider",
                            marks={
                                1: "0-10k",
                                2: "10-25k",
                                3: "25-50k",
                                4: "50-100k",
                                5: "100k+",
                            },
                            value=[1, 5],
                            min=1,
                            max=5,
                            step=1,
                        ),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.H5("Local Audience"),
                        dcc.RangeSlider(
                            id="local_audience_slider",
                            marks={
                                0: "0%",
                                20: "20%",
                                40: "40%",
                                60: "60%",
                                80: "80%",
                                100: "100%",
                            },
                            value=[0, 100],
                            min=0,
                            max=100,
                            step=5,
                        ),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.H5("Engagement Rate"),
                        dcc.RangeSlider(
                            id="er_slider",
                            marks={
                                0: "0%",
                                2: "2%",
                                4: "4%",
                                6: "6%",
                                8: "8%",
                                10: "10%",
                            },
                            value=[0, 10],
                            min=0,
                            max=10,
                            step=0.25,
                        ),
                    ],
                    md=3,
                ),
            ],
            style={"marginTop": 30},
        ),
        # Rows of Filters
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Status"),
                        dcc.Dropdown(
                            id="status_drop_down",
                            options=[
                                {"label": "Approved", "value": 3},
                                {"label": "Approached", "value": 2},
                                {"label": "Approval Requested", "value": 4},
                                {"label": "Rejected", "value": 5},
                            ],
                            value=[3],
                            multi=True,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        html.H5("App Activity"),
                        dcc.Dropdown(
                            id="s_activity_dropdown",
                            options=[
                                {"label": "Active", "value": "active"},
                                {"label": "Inactive", "value": "inactive"},
                                {"label": "All", "value": "all"},
                            ],
                            value="all",
                        ),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.H5("Platforms"),
                        dcc.Dropdown(
                            id="s_platform_dropdown",
                            options=[
                                {"label": "Instagram", "value": "instagram"},
                                {"label": "TikTok", "value": "tiktok"},
                                {"label": "Youtube", "value": "youtube"},
                            ],
                            value=["instagram", "tiktok", "youtube"],
                            multi=True,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            "Search",
                            id="s_search_button",
                            color="primary",
                            className="mr-1 d-md-block",
                            style={"position": "absolute", "bottom": "0"},
                        )
                    ],
                    md=1,
                    style={"position": "relative"},
                ),
            ],
            style={"marginTop": 30},
        ),
        # Value Boxes
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Loading(
                            id="total_talent_segmentation_loading",
                            type="default",
                            children=[html.Div(id="total_talent_segmentation")],
                        )
                    ],
                    md=2,
                ),
                dbc.Col(
                    [
                        dcc.Loading(
                            id="loggin_talent_segmentation_loading",
                            type="default",
                            children=[html.Div(id="loggin_talent_segmentation")],
                        )
                    ],
                    md=2,
                ),
                dbc.Col(
                    [
                        dcc.Loading(
                            id="active_talent_segmentation_loading",
                            type="default",
                            children=[html.Div(id="active_talent_segmentation")],
                        )
                    ],
                    md=2,
                ),
                dbc.Col(
                    [
                        dcc.Loading(
                            id="ave_er_segmentation_loading",
                            type="default",
                            children=[html.Div(id="ave_er_segmentation")],
                        )
                    ],
                    md=2,
                ),
                dbc.Col(
                    [
                        dcc.Loading(
                            id="ave_followers_segmentation_loading",
                            type="default",
                            children=[html.Div(id="ave_followers_segmentation")],
                        )
                    ],
                    md=2,
                ),
                dbc.Col(
                    [
                        dcc.Loading(
                            id="ave_local_audience_segmentation_loading",
                            type="default",
                            children=[html.Div(id="ave_local_audience_segmentation")],
                        )
                    ],
                    md=2,
                ),
            ],
            style={"marginTop": 30},
        ),
        dbc.Tabs(
            [
                dbc.Tab(CHARTS_TAB, label="Charts"),
                dbc.Tab(INFLUECNER_TAB, label="Influencers"),
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
                                    id="s_influencer_download_btn",
                                    color="secondary",
                                ),
                                dcc.Loading(
                                    id="s_download_loading",
                                    type="default",
                                    children=[dcc.Download(id="s_influencer_download")],
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
                dbc.Tooltip(
                    "Categories are based on a creators instagram profile only."
                    " Creators without an instagram account will not be in a category.",
                    target="categories_label",
                    placement="right",
                ),
            ]
        ),
    ],
)

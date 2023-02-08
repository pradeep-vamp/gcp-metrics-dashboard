import dash_bootstrap_components as dbc
from dash import dcc, html

# from graphs.graphs import value_box
from components.segmentation import active_countries

"""
components/pandacop.py

 @ticket:   https://vampdash.atlassian.net/browse/DAS-8026
 @date:     2021-06-22
 @auth:     Mark Brackenrig < mark@vamp.me >

 @desc:
 This file is used to display the data & layout required for the
 `Fraud Detection` page - also called PandaCop. It allows the user to approve and reject talent suspected of fraudulent activity.

"""

active_countries = active_countries.append(
    {"value": -1, "label": "All"}, ignore_index=True
)


PANDACOP = dbc.Tab(
    label="Fraud Detection",
    children=[
        # Suspension Modal
        dbc.Modal(
            [
                dbc.ModalHeader(html.H2("Suspend Influencer")),
                dbc.ModalBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.P(
                                            "By suspending an influencer, they will no"
                                            " longer be able to apply to briefs or be"
                                            " displayed to Vamps clients"
                                        ),
                                        html.P(
                                            "Are you sure you would like to suspend the"
                                            " influencer XYZ",
                                            id="modal-suspension-text",
                                        ),
                                        dbc.Select(
                                            id="modal-suspension-reason",
                                            placeholder=(
                                                "Please select the reason for"
                                                " suspension"
                                            ),
                                            options=[
                                                {
                                                    "label": "Inappropriate Content",
                                                    "value": "safe_search",
                                                },
                                                {
                                                    "label": "Fraudulent Followers",
                                                    "value": "fake_followers",
                                                },
                                                {
                                                    "label": "Low Engagement",
                                                    "value": "low_engagement",
                                                },
                                                {
                                                    "label": "Suspicious Account",
                                                    "value": "suspicious_account",
                                                },
                                                {
                                                    "label": "Other",
                                                    "value": "other",
                                                },
                                            ],
                                        ),
                                        dbc.Label("Additional Notes:", width="auto"),
                                        dbc.Textarea(
                                            className="mb-3",
                                            id="modal-suspension-notes",
                                            placeholder=(
                                                "Please record your reasoning behind"
                                                " suspending this influencer"
                                            ),
                                            value="",
                                        ),
                                    ],
                                    md=12,
                                )
                            ]
                        )
                    ]
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button(
                            "Suspend",
                            color="primary",
                            id="suspend-influencer-confirmed",
                            n_clicks=0,
                        ),
                        dbc.Button(
                            "Cancel",
                            id="modal-suspension-cancel",
                            color="danger",
                            outline=True,
                            className="ms-auto",
                            n_clicks=0,
                        ),
                    ]
                ),
            ],
            id="modal-suspension",
            size="lg",
            is_open=False,
        ),
        # Approve Modal
        dbc.Modal(
            [
                dbc.ModalHeader(html.H2("Approve Influencer")),
                dbc.ModalBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.P(
                                            "By approving an influencer, they will now"
                                            " be able to apply to briefs and will be"
                                            " displayed to Vamps clients"
                                        ),
                                        html.P(
                                            "Are you sure that the flagged issues are"
                                            " irrelevant and that the influencer will"
                                            " represent the Vamp collective well?",
                                            id="modal-approval-text",
                                        ),
                                        dbc.Select(
                                            id="modal-approval-reason",
                                            placeholder=(
                                                "Please select the reason for approval"
                                            ),
                                            options=[
                                                {
                                                    "label": (
                                                        "Safe search (Images are not"
                                                        " inappropriate) "
                                                    ),
                                                    "value": "safe_search",
                                                },
                                                {
                                                    "label": (
                                                        "High engagement explainable"
                                                    ),
                                                    "value": "high_engagement",
                                                },
                                                {
                                                    "label": (
                                                        "Low engagement acceptable"
                                                    ),
                                                    "value": "low_engagement",
                                                },
                                                {
                                                    "label": "Legitimate following",
                                                    "value": "legitimate_following",
                                                },
                                                {
                                                    "label": "Other",
                                                    "value": "other",
                                                },
                                            ],
                                        ),
                                        dbc.Label("Additional Notes:", width="auto"),
                                        dbc.Textarea(
                                            className="mb-3",
                                            id="modal-approval-notes",
                                            placeholder=(
                                                "Please record your reasoning behind"
                                                " approving this influencer"
                                            ),
                                            value="",
                                        ),
                                    ],
                                    md=12,
                                )
                            ]
                        )
                    ]
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button(
                            "Approve",
                            color="primary",
                            id="approved-influencer-confirmed",
                            n_clicks=0,
                        ),
                        dbc.Button(
                            "Cancel",
                            id="modal-approval-cancel",
                            color="danger",
                            outline=True,
                            className="ms-auto",
                            n_clicks=0,
                        ),
                    ]
                ),
            ],
            id="modal-approval",
            size="lg",
            is_open=False,
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Location"),
                        dcc.Dropdown(
                            id="pandacop_location_drop_down",
                            options=active_countries.to_dict("records"),
                            value=[-1],
                            multi=True,
                        ),
                    ],
                    md=3,
                ),
                # dbc.Col([
                #     html.Label("Run Influencer Classifier task"),
                #     dbc.Button("RUN TASK", id="ic-api-btn", color="info", className="mr-1", n_clicks=0),
                #     dcc.Loading(type="default", children=[
                #         html.P(id="ic-api-results")
                #     ])
                # ], md=3)
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader([html.H5("Flagged Influencers")]),
                                dcc.Loading(
                                    type="default",
                                    children=[
                                        dbc.CardBody(
                                            id="flagged_influencers_table",
                                            children=["Hello"],
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
                        dbc.Row(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [html.H5("Details of Suspicious Activity")]
                                        ),
                                        dcc.Loading(
                                            type="default",
                                            children=[dbc.CardBody(id="flag_details")],
                                        ),
                                    ],
                                    style={"width": "100%"},
                                )
                            ],
                            style={"width": "100%"},
                        )
                    ],
                    md=6,
                ),
            ],
            style={"marginTop": 30},
        ),
    ],
)

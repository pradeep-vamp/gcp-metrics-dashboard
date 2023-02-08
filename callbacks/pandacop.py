import os
from datetime import date

import boto3
import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from components.components import *
from data.functions import *
from data.pandacop import *
from graphs.graphs import *
from main import app

analytics_bucket = os.getenv("ANALYTICS_BUCKET")
api_base = os.getenv("ANALYTICS_API_BASE")
api_key = os.getenv("ANALYTICS_API_KEY")

"""
callbacks/pandacop.py

 @ticket:   https://vampdash.atlassian.net/browse/DAS-8026
 @date:     2021-06-22
 @auth:     Mark Brackenrig < mark@vamp.me >

 @desc:
 This file contains the callbacks for the `Fraud Detection` page - also called PandaCop.
 It allows the user to approve and reject talent suspected of fraudulent activity.

"""


def icon_stat(emoji, name, value):
    return html.Div(
        [
            html.P(name, style={"text-align": "center", "font-size": "1rem"}),
            html.H3(
                "".join([emoji, str(value)]),
                style={"text-align": "center", "font-size": "1rem"},
            ),
        ]
    )


@app.callback(
    [Output("flagged_influencers_table", "children")],
    [Input("pandacop_location_drop_down", "value")],
)
def pandacop_callback(location):
    """
    Displays flagged influencers suspected of having a sponsored post with engagements greater than reach
    or having an unusually low engagement rate.
    """
    location = None if len(location) == 1 and location[0] == -1 else location

    safe_search = retrieve_safe_search(analytics_bucket, location=None)
    # Causing errors during lint, what was its purpose, the `approved_influencers`
    # should be fetched below on every call
    # try:
    #     del(approved_influencers)
    # except:
    #     print("approved_influencers not found")
    approved_influencers = fetch_from_s3(
        key="metrics-dashboard/approved_influencers.csv",
        bucket="vamp-datalake",
    )
    approved_influencers["handle"] = approved_influencers["handle"].astype(str)

    try:
        # Get latest IC classification
        ic_classification = fetch_from_s3(
            key="talent_acquisition/classify/bulk/vamp/metrics-dashboard-inf-250.csv",
            bucket=analytics_bucket,
        )
        ic_class_errors = fetch_from_s3(
            key="talent_acquisition/classify/bulk/vamp/metrics-dashboard-inf-250_error.csv",
            bucket=analytics_bucket,
        )

        mean_diff = ic_classification["difference"].mean()
        std_diff = ic_classification["difference"].std()
        yellow_class = ic_classification.query(
            f"difference <= {mean_diff - (std_diff * 3)} or difference >="
            f" {mean_diff + (std_diff * 3)}"
        )
        red_class = ic_classification.loc[ic_classification["class"] == "reject", :]

        # Remove any error handles of influencers who were accepted / revewed anyway
        ic_class_errors = ic_class_errors.loc[
            ~ic_class_errors["handle"].isin(
                ic_classification.query('`class` == ["accept", "review"]')["handle"]
            ),
            :,
        ]
    except:
        red_class = pd.DataFrame([], columns=["handle"])
        yellow_class = pd.DataFrame([], columns=["handle"])
        ic_class_errors = pd.DataFrame([], columns=["handle"])

    # Add yellow and red card cases
    red_cards = retrieve_red_cards(location, red_class["handle"].unique())
    yellow_cards = retrieve_yellow_cards(
        location,
        [
            *yellow_class["handle"].unique(),
            *ic_class_errors["handle"].unique(),
        ],
    )  #

    # Yellow
    # find all with difference of more than 2 std from mean diff
    # any API error accounts
    # yellow_cards = yellow_cards.merge(yellow_class, how='left', left_on='handle')

    # Red
    # Any that are classified as rejected

    red_cards = red_cards.merge(
        approved_influencers, left_on="handle", right_on="handle", how="left"
    )
    yellow_cards = yellow_cards.merge(
        approved_influencers, left_on="handle", right_on="handle", how="left"
    )

    red_cards["approved_date"].fillna("2010-01-01")
    yellow_cards["approved_date"].fillna("2010-01-01")

    red_cards["approved_date"] = pd.to_datetime(
        red_cards["approved_date"], format="%Y-%m-%d"
    ).apply(lambda x: x.replace(tzinfo=None))
    yellow_cards["approved_date"] = pd.to_datetime(
        yellow_cards["approved_date"], format="%Y-%m-%d"
    ).apply(lambda x: x.replace(tzinfo=None))
    red_cards["date"] = pd.to_datetime(red_cards["date"], format="%Y-%m-%d").apply(
        lambda x: x.replace(tzinfo=None)
    )
    yellow_cards["date"] = pd.to_datetime(
        yellow_cards["date"], format="%Y-%m-%d"
    ).apply(lambda x: x.replace(tzinfo=None))

    red_cards = red_cards.loc[
        (red_cards["date"] > red_cards["approved_date"])
        | (red_cards["approved_date"].isna())
    ]
    yellow_cards = yellow_cards.loc[
        (yellow_cards["date"] > yellow_cards["approved_date"])
        | (yellow_cards["approved_date"].isna())
    ]

    red_value = red_cards["handle"].value_counts()
    yellow_value = yellow_cards["handle"].value_counts()
    safe_search = safe_search["handle"].value_counts()

    red_value = red_value.reset_index()
    yellow_value = yellow_value.reset_index()
    safe_search = safe_search.reset_index()

    red_value.columns = ["handle", "red_flags"]
    yellow_value.columns = ["handle", "yellow_flags"]
    safe_search.columns = ["handle", "safe_search"]

    flagged_influencers = red_value.merge(
        yellow_value, left_on="handle", right_on="handle", how="outer"
    )
    flagged_influencers = flagged_influencers.merge(
        safe_search, left_on="handle", right_on="handle", how="outer"
    )
    flagged_influencers.fillna(0, inplace=True)

    cols = [
        {"id": "handle", "name": "Handle"},
        {"id": "red_flags", "name": "Red Cards"},
        {"id": "yellow_flags", "name": "Yellow Cards"},
        {"id": "safe_search", "name": "Inappropriate Content"},
    ]
    flagged_influencers["id"] = flagged_influencers["handle"]
    flagged_influencers_data_table = dash_table.DataTable(
        id="table_2",
        columns=cols,
        data=flagged_influencers.to_dict("records"),
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        row_selectable="single",
        page_current=0,
        page_size=20,
        style_table={"overflowX": "scroll"},
    )
    # return [[flagged_influencers_data_table], [html.P('TODO')],[html.P('TODO')]]
    return [flagged_influencers_data_table]


@app.callback(
    [Output("flag_details", "children")],
    [Input("table_2", "selected_row_ids")],
)
def influencer_flag_details(handle):
    """
    Displays instances of suspected fraudulent activity.
    """
    if handle is None:
        raise PreventUpdate

    handle = handle[0] if isinstance(handle, list) and len(handle) == 1 else handle

    # Get latest IC classification
    try:
        ic_classification = fetch_from_s3(
            key="talent_acquisition/classify/bulk/vamp/metrics-dashboard-inf-250.csv",
            bucket=analytics_bucket,
        )
        current_class = ic_classification.query("`handle` == @handle")
        mean_diff = ic_classification["difference"].mean()
        std_diff = ic_classification["difference"].std()
        yellow_class = ic_classification.query(
            f"difference <= {mean_diff - (std_diff * 3)} or difference >="
            f" {mean_diff + (std_diff * 3)}"
        )
        ic_class_errors = fetch_from_s3(
            key="talent_acquisition/classify/bulk/vamp/metrics-dashboard-inf-250_error.csv",
            bucket=analytics_bucket,
        )

        # Remove any error handles of influencers who were accepted / revewed anyway
        ic_class_errors = ic_class_errors.loc[
            ~ic_class_errors["handle"].isin(
                ic_classification.query('`class` == ["accept", "review"]')["handle"]
            ),
            :,
        ]

        yellow_ic_handles = [
            *yellow_class["handle"].to_list(),
            *ic_class_errors["handle"].to_list(),
        ]
    except:
        current_class = pd.DataFrame()
        yellow_ic_handles = []

    ic_api_body = []

    if (
        len(current_class) == 1 and current_class.iloc[0]["class"] == "reject"
    ) or handle in yellow_ic_handles:
        # Add details about red flag for ic rejection
        e_rate = (
            current_class.iloc[0]["engagement"]
            / current_class.iloc[0]["followers_count"]
        ) * 100
        class_icons = {"reject": "❌", "review": "⚠️", "accept": "✅"}
        classification = current_class.iloc[0]["class"]

        # Get images used for classification
        class_data = fetch_influecner_class_data([handle])
        images = [
            {"key": idx, "src": row["media_url"]} for idx, row in class_data.iterrows()
        ]

        ic_api_body.append(
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.A(
                                        f"https://www.instagram.com/{handle}/",
                                        href=f"https://www.instagram.com/{handle}/",
                                        target="_blank",
                                    )
                                ],
                                md=12,
                            )
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    icon_stat(
                                        f"{class_icons.get(classification, '❌')} ",
                                        "Classification",
                                        classification,
                                    )
                                ],
                                md=3,
                            ),
                            dbc.Col(
                                [icon_stat("🙌 ", "Engagement", f"{e_rate:.2f}%")],
                                md=3,
                            ),
                            dbc.Col(
                                [
                                    icon_stat(
                                        "🌍 ",
                                        "Followers",
                                        round(
                                            current_class.iloc[0]["followers_count"],
                                            0,
                                        ),
                                    )
                                ],
                                md=3,
                            ),
                            dbc.Col(
                                [
                                    icon_stat(
                                        "🧑‍💻 ",
                                        "Follows",
                                        round(
                                            current_class.iloc[0]["follows_count"],
                                            0,
                                        ),
                                    )
                                ],
                                md=3,
                            ),
                        ]
                    ),
                    html.P("Classifications"),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    icon_stat(
                                        "🖼️ ",
                                        "NIMA",
                                        "{:.2f}%".format(
                                            current_class.iloc[0]["content_prob"] * 100
                                        ),
                                    )
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    icon_stat(
                                        "📊 ",
                                        "Stats",
                                        "{:.2f}%".format(
                                            current_class.iloc[0]["nocontent_prob"]
                                            * 100
                                        ),
                                    )
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    icon_stat(
                                        "⚔️ ",
                                        "Difference",
                                        "{:.2f}%".format(
                                            current_class.iloc[0]["difference"] * 100
                                        ),
                                    )
                                ],
                                md=4,
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            html.P("Predicted Images"),
                            dbc.Carousel(
                                items=images,
                                controls=True,
                                indicators=True,
                            ),
                        ]
                    ),
                ]
            )
        )

    # Red Cards
    red_cards = retrieve_red_cards()
    try:
        red_cards = red_cards.loc[red_cards["handle"].isin([handle]), :]
    except:
        red_cards = pd.DataFrame()

    # Yellow Cards
    yellow_cards = retrieve_yellow_cards()
    try:
        yellow_cards = yellow_cards.loc[yellow_cards["handle"].isin([handle]), :]
    except:
        yellow_cards = pd.DataFrame()

    # Safe Search
    influencer_id = fetch_from_postgres(
        f"Select influencer_id from social_accounts where handle='{handle}' AND"
        " social_platform_id = 1"
    )["influencer_id"][0]
    try:
        safe_search = retrieve_safe_search_influencer(influencer_id, analytics_bucket)
    except Exception as e:
        print(e)
        safe_search = pd.DataFrame()

    safe_search_body = []
    safe_search_body.append(
        html.Div(
            [
                html.P("Social Link: "),
                html.A(
                    children=[" " + "https://instagram.com/" + handle],
                    href="https://instagram.com/" + handle,
                    target="_blank",
                ),
            ],
            style={"display": "inline-flex"},
        )
    )
    for q in safe_search.iterrows():
        i = q[1]
        safe_search_body.append(
            html.Div(
                [
                    html.P("Adult: " + str(i["safe_search_results"]["adult"])),
                    html.Br(),
                    html.P("Spoof: " + str(i["safe_search_results"]["spoof"])),
                    html.Br(),
                    html.P("Medical: " + str(i["safe_search_results"]["medical"])),
                    html.Br(),
                    html.P("Violence: " + str(i["safe_search_results"]["violence"])),
                    html.Br(),
                    html.P("Racy: " + str(i["safe_search_results"]["racy"])),
                ],
                style={"display": "inline-flex"},
            )
        )

    red_card_body = []
    for q in red_cards.iterrows():
        i = q[1]
        red_card_body.append(
            html.Div(
                [
                    html.P("Engagements: " + str(i["engagement"])),
                    html.P("Reach: " + str(i["reach"])),
                    html.Div(
                        [
                            html.P("Social Link: "),
                            html.A(
                                children=[" " + i["social_link"]],
                                href=i["social_link"],
                                target="_blank",
                            ),
                        ],
                        style={"display": "inline-flex"},
                    ),
                    html.Br(),
                ]
            )
        )

    yellow_card_body = []
    for q in yellow_cards.iterrows():
        i = q[1]
        yellow_card_body.append(
            html.Div(
                [
                    html.P(
                        "Engagement Rate: "
                        + str(round(i["engagement_rate"] * 100, 2))
                        + "%"
                    ),
                    html.P("Followers: " + str(i["followers_count"])),
                    html.Div(
                        [
                            html.P("Social Link: "),
                            html.A(
                                children=[" " + i["handle"]],
                                href="https://instagram.com/" + i["handle"],
                                target="_blank",
                            ),
                        ],
                        style={"display": "inline-flex"},
                    ),
                    html.Br(),
                ]
            )
        )

    if len(safe_search_body) > 0:
        body_4 = html.Div(
            [html.H3("Safe Search Violation"), html.Div(safe_search_body)]
        )
    else:
        body_4 = html.Div()

    if len(red_card_body) > 0:
        body_1 = html.Div(
            [
                html.H3("Engagements exceed unique reach"),
                html.Div(red_card_body),
            ]
        )
    else:
        body_1 = html.Div()

    if len(yellow_card_body) > 0:
        body_2 = html.Div([html.H3("Low Engagement Rate"), html.Div(yellow_card_body)])
    else:
        body_2 = html.Div()

    if len(ic_api_body) > 0:
        b3_heading = html.H3("Flagged by classifier")

        if handle in yellow_class["handle"].to_list():
            b3_heading = html.H3("Flagged by classifier | Disagreement")

        if handle in ic_class_errors["handle"].to_list():
            b3_heading = html.H3("Flagged by classifier | Errors in data")

        if current_class.iloc[0]["class"] == "reject":
            b3_heading = html.H3("Flagged by classifier | Rejected")

        body_3 = html.Div([b3_heading, html.Div(ic_api_body)])
    else:
        body_3 = html.Div()

    button_divs = html.Div(
        [
            html.Button("Suspend Influencer", id="suspend_influencer", n_clicks=0),
            html.Button("Approve Influencer", id="approve_influencer", n_clicks=0),
        ],
        style={
            "display": "inline-flex",
            "width": "100%",
            "place-content": "space-evenly",
        },
    )
    body = html.Div(
        [
            body_1,
            body_2,
            body_3,
            body_4,
            button_divs,
            html.Div(id="success_message"),
            html.Div(id="success_message_2"),
        ]
    )

    return [body]


@app.callback(
    [
        Output("modal-suspension", "is_open"),
        Output("modal-suspension-text", "children"),
        Output("modal-suspension-reason", "value"),
        Output("modal-suspension-notes", "value"),
    ],
    [
        Input("suspend_influencer", "n_clicks"),
        Input("modal-suspension-cancel", "n_clicks"),
        Input("suspend-influencer-confirmed", "n_clicks"),
    ],
    [
        State("modal-suspension", "is_open"),
        State("table_2", "selected_row_ids"),
    ],
)
def toggle_suspension(n1, n2, n3, is_open, handles):
    context = dash.callback_context

    if not context.triggered:
        raise PreventUpdate
    else:
        trigger = context.triggered[0]["prop_id"].split(".")[0]
        handle = handles[0] if len(handles) > 0 else ""

        if trigger == "suspend_influencer" and n1:
            return [
                not is_open,
                f"Are you sure you would like to suspend the influencer {handle}",
                "",
                "",
            ]
        elif trigger == "modal-suspension-cancel" and n2:
            return [False, "", "", ""]
        elif trigger == "suspend-influencer-confirmed" and n3:
            return [False, "", "", ""]

        return [
            is_open,
            "Are you sure you would like to suspend the influencer XYZ",
            "",
            "",
        ]


@app.callback(
    [Output("success_message", "children")],
    [Input("suspend-influencer-confirmed", "n_clicks")],
    [
        State("modal-suspension-reason", "value"),
        State("modal-suspension-notes", "value"),
        State("table_2", "selected_row_ids"),
        State("current_loggedin_email", "data"),
    ],
)
def suspend_influencer(n_clicks, reason, notes, handle, current_email):
    """
    Sends mutation to Servalan when the user clicks to suspend the influencer.
    """
    if not n_clicks:
        raise PreventUpdate

    elif n_clicks > 0:
        message = suspend_influencer_servalan(
            handle=handle[0],
            reason=reason,
            notes=notes,
            current_email=current_email,
        )

        return [html.P(message, style={"display": "inline"})]
    else:
        return [
            html.P(
                "Please Approve or Reject Influencer",
                style={"display": "none"},
            )
        ]


@app.callback(
    [
        Output("modal-approval", "is_open"),
        Output("modal-approval-text", "children"),
        Output("modal-approval-reason", "value"),
        Output("modal-approval-notes", "value"),
    ],
    [
        Input("approve_influencer", "n_clicks"),
        Input("modal-approval-cancel", "n_clicks"),
        Input("approved-influencer-confirmed", "n_clicks"),
    ],
    [State("modal-approval", "is_open"), State("table_2", "selected_row_ids")],
)
def toggle_approval(n1, n2, n3, is_open, handles):
    context = dash.callback_context

    if not context.triggered:
        raise PreventUpdate
    else:
        trigger = context.triggered[0]["prop_id"].split(".")[0]
        handle = handles[0] if len(handles) > 0 else ""

        if trigger == "approve_influencer" and n1:
            return [
                not is_open,
                "Are you sure that the flagged issues are irrelevant and that the"
                f" influencer {handle}, will represent the Vamp collective well?",
                "",
                "",
            ]
        elif trigger == "modal-approval-cancel" and n2:
            return [False, "", "", ""]
        elif trigger == "approved-influencer-confirmed" and n3:
            return [False, "", "", ""]

        return [
            is_open,
            "Are you sure that the flagged issues are irrelevant and that the"
            " influencer will represent the Vamp collective well?",
            "",
            "",
        ]


@app.callback(
    [Output("success_message_2", "children")],
    [Input("approved-influencer-confirmed", "n_clicks")],
    [
        State("modal-approval-reason", "value"),
        State("modal-approval-notes", "value"),
        State("table_2", "selected_row_ids"),
        State("current_loggedin_email", "data"),
    ],
)
def approve_influencer(n_clicks, reason, notes, handle, current_email):
    """
    Records 'approval' so user does not need to see influencer again, unless they commit a later offence.
    """
    if n_clicks > 0:
        s3 = boto3.client("s3")
        handle = handle[0]
        approved_influencers = fetch_from_s3(
            key="metrics-dashboard/approved_influencers.csv",
            bucket="vamp-datalake",
        )
        approved_influencers = approved_influencers.loc[
            approved_influencers["handle"] != handle
        ]

        approved_data = {"handle": handle, "approved_date": date.today()}
        approved_influencers = approved_influencers.append(
            approved_data, ignore_index=True
        )
        post_to_s3(
            key="metrics-dashboard/approved_influencers.csv",
            df=approved_influencers,
            bucket="vamp-datalake",
        )
        message = "Influencer has been approved"

        try:
            influencer_id = fetch_from_postgres(
                f"Select influencer_id from social_accounts where handle='{handle}' AND"
                " social_platform_id = 1"
            )["influencer_id"][0]
            s3.delete_object(
                Key=f"influencer-poker/data/annotations/safe-search/flagged_influencers/{influencer_id}.json",
                Bucket=analytics_bucket,
            )
        except Exception as e:
            print(e)

        # Send log to S3 with user suspension
        current_email = pd.read_json(current_email, orient="split")
        # record_influencer_action(
        #     employee_email=current_email.loc[0, "email"],
        #     influencer_id=influencer_id,
        #     action="approved_safe_search",
        #     reason=reason,
        #     notes=notes,
        # )

        return [html.P(message, style={"display": "inline"})]
    else:
        return [
            html.P(
                "Please Approve or Reject Influencer",
                style={"display": "none"},
            )
        ]

"""
 callbacks/influencer_lookup.py

 @ticket:	https://vampdash.atlassian.net/browse/DAS-7706
 @date:		2021-05-10
 @auth:		Daniel Stratti < daniels@vamp.me >

 @desc:
  This file is used to display the data & layout required for the
 `Influencer Usage` page. The page is split into 3 main section, high-level
 stats & graphs, table data, downloads
"""
import json
from datetime import date
from datetime import datetime as dt

import dash_bootstrap_components as dbc

# Utilities
import pandas as pd
import requests
from dash import dash_table, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dateutil.relativedelta import relativedelta

# Data & Components & Helpers
from components.components import *
from data.functions import *
from data.influencer_lookup import *
from graphs.graphs import *

# Dash componenets
from main import app

FB_API_BASE = "https://graph.facebook.com/v5.0/"
IG_BD_PARAMS = "{username,followers_count,media_count,follows_count,media{id,media_url,comments_count,like_count}}"

"""
--------------------------------------------------------------------------------
Helper functions
--------------------------------------------------------------------------------
"""
COL_MAP = {
    "engagement_percent": "engagement",
    "followers_count": "followers",
    "follows_count": "follows",
    "media_count": "media count",
}


def icon_text(title, emoji, value):
    """Variation on the view_box"""
    return html.Div(
        [
            html.H1(title, style={"text-align": "center", "font-size": "1rem"}),
            html.H2(
                f"{emoji} {value}",
                style={"text-align": "center", "font-size": "1.5rem"},
            ),
        ]
    )


def il_map_brief_status(row):
    """helper to map brief statuses"""
    if row["status"] in (
        "Approved",
        "Fulfilled",
        "Completed",
        "Processing Payment",
    ):
        return "Successful"
    elif row["status"] == "Rejected":
        return "Unsucessful"
    elif row["status"] in ("Invitation Accepted", "Shortlisted"):
        return "Applied"
    elif row["is_viewed"] and row["status"] in (
        "Invited",
        "Invitation Rejected",
    ):
        return "Viewed"
    elif not row["is_viewed"] and row["status"] in (
        "Invited",
        "Invitation Rejected",
    ):
        return "Did not view"

    return "Unknown"


def get_percentile(current, dist, key):
    """Calculate the percentile the current record sits within"""
    current_pos = current[key].iloc[0]  # noqa
    return (1 - len(dist.query(f"{key} <= @current_pos")) / len(dist)) * 100


def build_il_distributions(il_serialise, key):
    """Build the cohort distribution graphs"""
    # Load data from JSON
    distribution_data = json.loads(il_serialise)
    current_rec = pd.read_json(distribution_data["current"], orient="split")
    il_distribution = pd.read_json(distribution_data["distributions"], orient="split")

    # if current record is empty get data from IC API
    if len(il_distribution) == 0 or len(current_rec) == 0:
        raise PreventUpdate

    current_pos = current_rec[key].iloc[0]

    if key == "followers_count":
        print(current_rec[key])
        print(key)
        print("current_pos: ", current_pos)

    percentile = get_percentile(current_rec, il_distribution, key)
    print(percentile)
    percentile_text = (
        f"Influencer is in the top {round(percentile, 0)}% of their cohort for"
        f" {COL_MAP[key]}"
    )

    # Generate line graph
    distribution = il_create_distribution(current_pos, il_distribution, key)

    return [
        html.P(
            percentile_text,
            style={
                "padding": "1em",
                "color": "red",
                "font-weight": "300",
                "font-style": "italic",
            },
        ),
        distribution,
    ]


"""
--------------------------------------------------------------------------------
Callback functions
--------------------------------------------------------------------------------
"""


@app.callback(
    Output("il-brief-dataset", "data"),
    [
        Input("il_influencer_drop_down", "value"),
        Input("il_date_inputs", "start_date"),
        Input("il_date_inputs", "end_date"),
    ],
)
def get_il_briefs(social_id, start_date, end_date):
    """Fetch brief dataset for social ID and place in store"""
    if social_id is None:
        raise PreventUpdate  # Stop update

    il_briefs = fetch_il_briefs(social_id, start_date, end_date)

    return il_briefs.to_json(date_format="iso", orient="split")


@app.callback(
    Output("il-distribution-dataset", "data"),
    [
        Input("il_influencer_drop_down", "value"),
        Input("il-current-dataset", "data"),
    ],
)
def get_il_distributions(social_id, current):
    """Fetch stat distributions dataset for social ID and place in store"""
    if social_id is None:
        raise PreventUpdate  # Stop update

    il_distribution = fetch_stat_distributions(social_id)

    if current is None:
        current_rec = il_distribution.loc[il_distribution["id"] == social_id]

        dist_data = {
            "current": current_rec.to_json(date_format="iso", orient="split"),
            "distributions": il_distribution.to_json(date_format="iso", orient="split"),
        }
    else:

        dist_data = {
            "current": current,
            "distributions": il_distribution.to_json(date_format="iso", orient="split"),
        }

    return json.dumps(dist_data)


@app.callback(
    Output("il-warning-section", "children"),
    [Input("il-current-dataset", "data")],
)
def display_warning(current):
    if current is None:
        return []
    else:
        return dbc.Alert(
            "Warning! The influecners social token was outdated so some data has been"
            " collected via API's",
            color="warning",
            dismissable=True,
            is_open=True,
        )


@app.callback(
    [
        Output("il_member_since", "children"),
        Output("il_status", "children"),
        Output("il_country", "children"),
        Output("il_engagement", "children"),
        Output("il_followers", "children"),
        Output("il_age", "children"),
        Output("il_gender", "children"),
        Output("il-current-dataset", "data"),
    ],
    [Input("il_influencer_drop_down", "value")],
)
def build_demographics(social_id):
    """
    Build the influencer demographic section based on selected social account
    """
    if social_id is None:
        raise PreventUpdate

    il_demog = fetch_social_demographics(social_id)

    if len(il_demog) == 0:
        raise PreventUpdate
    else:
        il_demog = il_demog.iloc[0]

    current = None

    # If social token expired and last login older than 2 months, fetch IG BD
    if not il_demog["token_valid"] and (
        il_demog["last_active"] <= date.today() + relativedelta(months=-2)
    ):
        query_as = fetch_ig_token("strattidaniel")
        api_url = f"{FB_API_BASE}{query_as['social_id']}?fields=business_discovery.username({il_demog['handle']}){IG_BD_PARAMS}"
        headers = {"Authorization": f"Bearer {query_as['social_token']}"}

        try:
            # Query API
            response = requests.get(api_url, headers=headers)
            json_body = response.json()

        except Exception as e:
            raise Exception(api_url, str(e))

        if (
            "business_discovery" in json_body.keys()
            and "media" in json_body["business_discovery"].keys()
            and "data" in json_body["business_discovery"]["media"].keys()
        ):

            # update il_demog with API details
            api_res = json_body["business_discovery"]
            il_demog["followers_count"] = api_res.get(
                "followers_count", il_demog["followers_count"]
            )
            il_demog["follows_count"] = api_res.get(
                "follows_count", il_demog["follows_count"]
            )
            il_demog["media_count"] = api_res.get(
                "media_count", il_demog["media_count"]
            )
            il_demog["followers_count"] = api_res.get(
                "followers_count", il_demog["followers_count"]
            )
            avg_e = [
                media.get("comments_count", 0) + media.get("like_count", 0)
                for media in api_res["media"]["data"]
            ]
            avg_e = sum(avg_e) / len(avg_e)
            il_demog["engagement_percent"] = (avg_e / il_demog["followers_count"]) * 100

            # il_demog['from_api'] = True
            current = il_demog.to_frame().T
            current = current.to_json(date_format="iso", orient="split")

    # Create summary stats value boxes
    il_member_since = icon_text(
        title="Vamp Member Since",
        emoji="🧑‍💻",
        value=il_demog["inserted_at"].strftime("%b-%Y").upper(),
    )
    il_status = icon_text("Status", "🖥️", il_demog["status"].upper())
    il_country = icon_text("Country", "🌍", il_demog.get("country", "").upper())
    il_engagement = icon_text(
        "Engagement Rate",
        "🍿",
        "{:.2f}%".format(float(il_demog["engagement_percent"])),
    )
    il_followers = icon_text(
        "Followers",
        "📈",
        "{:.1f} K".format(float(il_demog["followers_count"] / 1000)),
    )

    il_demog["age"] = "No D.O.B" if pd.isnull(il_demog["age"]) else il_demog["age"]
    il_age = icon_text("Age", "🎂", il_demog["age"].round(0))
    il_gender = icon_text("Gender", "👫", il_demog["gender"].upper())

    # return all 8 summary stats
    return (
        il_member_since,
        il_status,
        il_country,
        il_engagement,
        il_followers,
        il_age,
        il_gender,
        current,
    )


@app.callback(Output("il_brief_table", "children"), [Input("il-brief-dataset", "data")])
def build_brief_table(il_serialise):
    """
    Build brief table to show status and deliverables

    il_serialise : JSON
            Dict containing the selected social ID
    """
    if il_serialise is None:
        raise PreventUpdate

    il_briefs = pd.read_json(il_serialise, orient="split")

    if len(il_briefs) == 0:
        raise PreventUpdate

    il_briefs["new_status"] = il_briefs.apply(lambda x: il_map_brief_status(x), axis=1)
    # Set table columns, ids map to column names from data/influencer_usage.py
    cols = [
        {"id": "name", "name": "Campaign"},
        {"id": "campaign_id", "name": "Campaign ID"},
        {"id": "start_date", "name": "Start Date"},
        {"id": "new_status", "name": "Status"},
        {"id": "total_photos_required", "name": "Deliverables Count"},
    ]

    il_briefs = il_briefs.sort_values(["start_date"], ascending=False)
    data_table = dash_table.DataTable(
        id="table",
        columns=cols,
        data=il_briefs.to_dict("records"),
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=18,
        style_table={"overflowX": "scroll"},
    )

    return data_table


@app.callback(Output("il_brief_graph", "children"), [Input("il-brief-dataset", "data")])
def build_il_brief_chart(il_serialise):
    """
    Process the cumulative usage data on campaign proportions vs influencer proportion
    @param iu_serialise {JSON}: The JSON encoded data produced by the `get_iu_stats`
                                                            function

    @return {Tuple}: Returns a plotly figure
    """
    if il_serialise is None:
        raise PreventUpdate

    il_briefs = pd.read_json(il_serialise, orient="split")

    if len(il_briefs) == 0:
        raise PreventUpdate

    # Generate line graph
    il_briefs["new_status"] = il_briefs.apply(lambda x: il_map_brief_status(x), axis=1)
    barchart = il_brief_barchart(il_briefs)

    return barchart


@app.callback(
    [
        Output("il-token-value", "children"),
        Output("il-criteria", "children"),
        Output("il-range", "children"),
    ],
    [Input("il-distribution-dataset", "data")],
)
def build_ratecard_desc(il_serialise):
    """
    Display the rate card details used to create the cohort distributions
    """
    distribution_data = json.loads(il_serialise)
    current_rec = pd.read_json(distribution_data["distributions"], orient="split")

    if len(current_rec) == 0:
        raise PreventUpdate

    coin_val = current_rec["coin_count"].iloc[0]
    min_f = current_rec["min_range"].iloc[0]
    max_f = current_rec["max_range"].iloc[0]
    criteria = current_rec["criteria"].iloc[0]

    return [
        f"🪙 {coin_val} Tokens",
        f"Criteria {criteria}",
        f"Followers {min_f} - {max_f}",
    ]


@app.callback(
    Output("il-engagement-distribution", "children"),
    [Input("il-distribution-dataset", "data")],
)
def build_engagement_distribution(il_serialise):
    """Build the cohort distribution engagement graph"""
    return build_il_distributions(il_serialise, "engagement_percent")


@app.callback(
    Output("il-followers-distribution", "children"),
    [Input("il-distribution-dataset", "data")],
)
def build_engagement_distribution(il_serialise):
    """Build the cohort distribution followers graph"""
    return build_il_distributions(il_serialise, "followers_count")


@app.callback(
    Output("il-follows-distribution", "children"),
    [Input("il-distribution-dataset", "data")],
)
def build_engagement_distribution(il_serialise):
    """Build the cohort distribution follows graph"""
    return build_il_distributions(il_serialise, "follows_count")


@app.callback(
    Output("il-media-distribution", "children"),
    [Input("il-distribution-dataset", "data")],
)
def build_engagement_distribution(il_serialise):
    """Build the cohort distribution media graph"""
    return build_il_distributions(il_serialise, "media_count")


@app.callback(
    Output("il_audience_graph", "children"),
    [Input("il_influencer_drop_down", "value")],
)
def build_il_audience_graphs(social_id):
    """Build the audience demographic graphs"""
    if social_id is None:
        raise PreventUpdate

    # Load data from JSON
    il_audience = fetch_audience_stats(social_id)

    if len(il_audience) == 0:
        raise PreventUpdate

    # Generate line graph
    audience_charts = il_audience_stats(il_audience)

    return audience_charts


@app.callback(
    Output("il_stats_download", "data"),
    [Input("il_stats_download_btn", "n_clicks")],
    [
        State("il-distribution-dataset", "data"),
        State("current_loggedin_email", "data"),
    ],
)
def generate_csv(n_clicks, il_serialise, current_email):
    """
    Generate a CSV to download of the social accounts audience stats
    @param n_clicks {Integer | None}: Used to check if the download button was infact pressed
    @param il_serialise {JSON}: dict containing the selected social ID
    """
    restrict_resource(current_email)

    # Only download once clicked
    if n_clicks == 0 or n_clicks is None:
        raise PreventUpdate

    if il_serialise is None:
        raise PreventUpdate

    # Load data from JSON
    distribution_data = json.loads(il_serialise)
    current_rec = pd.read_json(distribution_data["current"], orient="split")
    il_distribution = pd.read_json(distribution_data["distributions"], orient="split")

    current_rec = current_rec.reset_index(drop=True)

    # Only download CSV with data
    if len(current_rec) == 0:
        raise PreventUpdate

    handle = current_rec["handle"].iloc[0]
    social_id = current_rec["id"].iloc[0]
    e_percentile = get_percentile(current_rec, il_distribution, "engagement_percent")
    f_percentile = get_percentile(current_rec, il_distribution, "followers_count")
    f2_percentile = get_percentile(current_rec, il_distribution, "follows_count")
    m_percentile = get_percentile(current_rec, il_distribution, "media_count")
    current_rec.loc[
        0,
        [
            "followers_top_percentile",
            "follows_top_percentile",
            "media_top_percentile",
            "engagement_rate_top_percentile",
        ],
    ] = (
        round(f_percentile, 2),
        round(f2_percentile, 2),
        round(m_percentile, 2),
        round(e_percentile, 2),
    )

    il_audience = fetch_audience_stats(social_id)
    current_rec = current_rec.merge(
        il_audience, how="left", left_on="id", right_on="social_account_id"
    )
    current_rec = current_rec.rename(
        columns={
            "category": "audience_category",
            "tag": "audience_tag",
            "percentage": "audience_percentage",
            "value": "audience_value",
        }
    )

    # Format data and filename ready for download
    cols = [
        "influencer_id",
        "social_account_id",
        "handle",
        "followers_count",
        "followers_top_percentile",
        "follows_count",
        "follows_top_percentile",
        "media_count",
        "media_top_percentile",
        "engagement_percent",
        "engagement_rate_top_percentile",
        "audience_tag",
        "audience_percentage",
        "audience_value",
    ]
    data = current_rec.loc[:, cols]

    today = dt.today().strftime("%d-%m-%Y")
    filename = f"influencer_lookup_{social_id}_{handle}_{today}.csv"

    return dcc.send_data_frame(data.to_csv, filename=filename, index=False)

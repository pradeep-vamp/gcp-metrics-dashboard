import datetime
import os

# import basic libraries
import numpy as np
import requests
from dash import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from numpy.linalg import norm

# import App
from components.components import *

# import data functions
from data.functions import *
from data.segmentation import *

# import graphing functions
from graphs.graphs import *
from main import app


def fetch_cast_vector(cast_kw):
    """
    Hit the analytics API to get a vector representation of the key word search
    terms

    cast_kw : str
            The search terms to vectorise

    return : list
            THe vector representation of the search terms
    """
    api_base = os.getenv("ANALYTICS_API_BASE")
    api_key = os.getenv("ANALYTICS_API_KEY")

    url = f"{api_base}/influencer-poker/keyword-search"

    headers = {"x-api-key": api_key}
    data = {"input_text": cast_kw, "n_num": 90}
    response = requests.post(url, headers=headers, json=data)
    res = response.json()
    return res


def cosine_sim(vec1, vec2):
    """
    Calculate the cosine similarity between two vectors

    vec1 : list
    vec2 : list

    return : float
            The cosine similarity between the vectors [-1, 1]
    """
    try:
        vec1 = np.squeeze(np.array(vec1))
        vec2 = np.squeeze(np.array(vec2))

        return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))
    except:
        return 0.0


###SEGMENTATION TOOL ####
@app.callback(
    Output("s_influencer_table", "children"),
    [Input("s_search_button", "n_clicks")],
    [
        State("location_drop_down", "value"),
        State("gender_drop_down", "value"),
        State("categories_drop_down", "value"),
        State("status_drop_down", "value"),
        State("age_slider", "value"),
        State("local_audience_slider", "value"),
        State("followers_slider", "value"),
        State("er_slider", "value"),
        State("s_activity_dropdown", "value"),
        State("s_platform_dropdown", "value"),
    ],
)
def build_influencer_table(
    n_clicks,
    location,
    gender,
    categories,
    status,
    age,
    local_audience,
    followers,
    er,
    activity,
    platforms,
):

    # Only download once clicked
    if n_clicks == 0 or n_clicks is None:
        raise PreventUpdate

    data = fetch_segmentation_data(
        location,
        gender,
        categories,
        status,
        age,
        local_audience,
        followers,
        er,
        activity,
        platforms,
    )

    # format data for display
    data["engagement_rate"] = (data["engagement_rate"].astype(float) * 100).round(2)
    data["local_audience"] = (data["local_audience"].astype(float) * 100).round(2)

    cols = [
        {"id": "handle", "name": "Handle"},
        {"id": "platform", "name": "Social Platform"},
        {"id": "country", "name": "Country"},
        {"id": "age", "name": "Age"},
        {"id": "gender", "name": "Gender"},
        {"id": "influencer_status_name", "name": "Status"},
        {"id": "engagement_rate", "name": "Engagement Rate (%)"},
        {"id": "followers_count", "name": "Followers"},
        {"id": "local_audience", "name": "Local Audience"},
    ]

    return dash_table.DataTable(
        id="s_influencer_table_data",
        columns=cols,
        data=data.to_dict("records"),
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=20,
        style_table={"overflowX": "scroll"},
    )


@app.callback(
    [
        Output("gender_chart", "children"),
        Output("age_chart", "children"),
        Output("followers_chart", "children"),
        Output("er_chart", "children"),
        Output("locations_map", "children"),
    ],
    [Input("s_search_button", "n_clicks")],
    [
        State("location_drop_down", "value"),
        State("gender_drop_down", "value"),
        State("categories_drop_down", "value"),
        State("status_drop_down", "value"),
        State("age_slider", "value"),
        State("local_audience_slider", "value"),
        State("followers_slider", "value"),
        State("er_slider", "value"),
        State("s_activity_dropdown", "value"),
        State("s_platform_dropdown", "value"),
    ],
)
def build_segment_charts(
    n_clicks,
    location,
    gender,
    categories,
    status,
    age,
    local_audience,
    followers,
    er,
    activity,
    platforms,
):

    # Only download once clicked
    if n_clicks == 0 or n_clicks is None:
        raise PreventUpdate

    data = fetch_segmentation_data(
        location,
        gender,
        categories,
        status,
        age,
        local_audience,
        followers,
        er,
        activity,
        platforms,
    )
    data["engagement_rate"] = (data["engagement_rate"].astype(float) * 100).round(2)

    return [
        gender_segementation_chart(data),
        age_segementation_chart(data),
        followers_segementation_chart(data),
        er_segementation_chart(data),
        locations_map(data),
    ]


###SEGMENTATION TOOL ####
@app.callback(
    [
        Output("total_talent_segmentation", "children"),
        Output("loggin_talent_segmentation", "children"),
        Output("active_talent_segmentation", "children"),
        Output("ave_er_segmentation", "children"),
        Output("ave_followers_segmentation", "children"),
        Output("ave_local_audience_segmentation", "children"),
    ],
    [Input("s_search_button", "n_clicks")],
    [
        State("location_drop_down", "value"),
        State("gender_drop_down", "value"),
        State("categories_drop_down", "value"),
        State("status_drop_down", "value"),
        State("age_slider", "value"),
        State("local_audience_slider", "value"),
        State("followers_slider", "value"),
        State("er_slider", "value"),
        State("s_activity_dropdown", "value"),
        State("s_platform_dropdown", "value"),
    ],
)
def build_icon_summary(
    n_clicks,
    location,
    gender,
    categories,
    status,
    age,
    local_audience,
    followers,
    er,
    activity,
    platforms,
):

    # Only download once clicked
    if n_clicks == 0 or n_clicks is None:
        raise PreventUpdate

    data = fetch_segmentation_data(
        location,
        gender,
        categories,
        status,
        age,
        local_audience,
        followers,
        er,
        activity,
        platforms,
    )

    total_talent = value_box("😁 ", "Total Talent", f"{len(data):,}")
    loggin_talent = value_box(
        "☑️ ",
        "Business Tick",
        "{:,}".format(len(data.loc[data["is_business"] == True])),
    )

    last_active = len(
        data.loc[
            data["last_active"]
            >= (datetime.datetime.today() - datetime.timedelta(days=31))
        ]
    )
    active_talent = value_box("🤳 ", "Active Talent", f"{last_active:,}")

    followers = data.loc[~data["followers_count"].isna(), "followers_count"].mean()
    ave_followers = value_box("🙌 ", "Average Followers", f"{round(followers):,}")

    er_value = (data["engagements"].sum()) / data["followers_count"].sum()
    ave_er = value_box("👍 ", "Engagement Rate", str(round(er_value * 100, 2)) + "%")

    local_audience_value = (data["local_audience_value"].sum()) / data[
        "followers_count"
    ].sum()
    local_audience = value_box(
        "🌍 ", "local audience", str(round(local_audience_value * 100, 2)) + "%"
    )

    return [
        total_talent,
        loggin_talent,
        active_talent,
        ave_er,
        ave_followers,
        local_audience,
    ]


@app.callback(
    Output("s_influencer_download", "data"),
    [Input("s_influencer_download_btn", "n_clicks")],
    [
        State("location_drop_down", "value"),
        State("gender_drop_down", "value"),
        State("categories_drop_down", "value"),
        State("status_drop_down", "value"),
        State("age_slider", "value"),
        State("local_audience_slider", "value"),
        State("followers_slider", "value"),
        State("er_slider", "value"),
        State("s_activity_dropdown", "value"),
        State("s_platform_dropdown", "value"),
        State("current_loggedin_email", "data"),
    ],
)
def generate_csv(
    n_clicks,
    location,
    gender,
    categories,
    status,
    age,
    local_audience,
    followers,
    er,
    activity,
    platforms,
    current_email,
):
    """ """
    restrict_resource(current_email)
    # Only download once clicked
    if n_clicks == 0 or n_clicks is None:
        raise PreventUpdate

    data = fetch_segmentation_data(
        location,
        gender,
        categories,
        status,
        age,
        local_audience,
        followers,
        er,
        activity,
        platforms,
    )

    briefs = fetch_brief_participation(data["influencer_id"].to_list())
    data = data.merge(
        briefs, how="left", left_on="influencer_id", right_on="influencer_id"
    )

    file_cols = [
        "influencer_id",
        "applications",
        "participation",
        "country",
        "handle",
        "platform",
        "media_count",
        "followers_count",
        "follows_count",
        "engagement_rate",
        "inserted_at",
        "is_business",
        "gender",
        "last_active",
        "age",
        "influencer_status_name",
        "local_audience",
        "full_name",
        "email",
        "postcode",
    ]
    data = data.loc[:,]

    # format data for display
    data["engagement_rate"] = (data["engagement_rate"].astype(float) * 100).round(2)
    data["local_audience"] = (data["local_audience"].astype(float) * 100).round(2)

    # Format data and filename ready for download
    today = datetime.datetime.today()
    filename = f"segmentation_{today.strftime('%Y_%m_%d')}.csv"

    return dcc.send_data_frame(data.to_csv, filename=filename, index=False)

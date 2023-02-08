import datetime

import dash_bootstrap_components as dbc
import numpy as np

# Utilities
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html


def value_box(emoji, subtitle, value, id=None):

    if id != None:
        val = html.Div(
            [
                html.H1("".join([emoji, str(value)])),
                html.P(subtitle, style={"text-align": "left"}),
            ],
            id=id,
            style={"padding-left": 20},
        )
    else:
        val = html.Div(
            [
                html.H1("".join([emoji, str(value)])),
                html.P(subtitle, style={"text-align": "left"}),
            ],
            style={"padding-left": 20},
        )
    return val


def new_talent(cleaned_data):

    talent_order = [
        "Approved - Approval Requested",
        "Approved - Approached",
        "Approached",
        "Rejected",
        "Approval Requested",
    ]
    fig = px.bar(cleaned_data, x="status", y="count", text="count", orientation="v")
    fig.update_layout(
        xaxis=dict(title="", categoryorder="array", categoryarray=talent_order),
        yaxis=dict(title=""),
    )
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig.update_traces(
        hovertemplate="<i>Status:</i> %{x}<br><i>No. Talent:</i> %{y:,.0f}"
    )
    fig.update_traces(marker_color="#17bdfe")

    x = dcc.Graph(id="new-talent", figure=fig)
    return x


def new_talent_locations(data):
    data["status"] = np.where(
        data["status"].isin(
            [
                "Approved - Approval Requested",
                "Approved - Approached",
                "Approached",
                "Rejected",
                "Approval Requested",
            ]
        ),
        data["status"],
        "Other",
    )
    colours = {
        "status": [
            "Approached",
            "Approval Requested",
            "Approved - Approval Requested",
            "Approved - Approached",
            "Other",
            "Rejected",
        ],
        "colour": [
            "#c55cdb",
            "#fbbc05",
            "#07a8f3",
            "#86e0fb",
            "#bbbbbb",
            "#ff5177",
        ],
    }
    col = [
        colours["colour"][i]
        for i in range(0, 6)
        if np.any(colours["status"][i] == data["status"])
    ]

    fig = px.bar(
        data.sort_values("status"),
        x="country",
        y="count",
        color="status",
        color_discrete_sequence=col,
    )
    fig.update_layout(xaxis={"categoryorder": "total descending"})

    x = dcc.Graph(id="new-talent", figure=fig)
    regions = [
        {
            "sub_region": "Northern America",
            "region": "Americas",
            "Vamp": "Americas",
        },
        {"sub_region": "Eastern Asia", "region": "Asia", "Vamp": "Asia"},
        {"sub_region": "Central Asia", "region": "Asia", "Vamp": "Asia"},
        {"sub_region": "Eastern Europe", "region": "Europe", "Vamp": "Europe"},
        {"sub_region": "South-eastern Asia", "region": "Asia", "Vamp": "Asia"},
        {
            "sub_region": "Latin America and the Caribbean",
            "region": "Americas",
            "Vamp": "Americas",
        },
        {"sub_region": "Western Asia", "region": "Asia", "Vamp": "MENA"},
        {
            "sub_region": "Northern Europe",
            "region": "Europe",
            "Vamp": "Europe",
        },
        {"sub_region": "Western Europe", "region": "Europe", "Vamp": "Europe"},
        {"sub_region": "Micronesia", "region": "Oceania", "Vamp": "ANZ"},
        {"sub_region": "Polynesia", "region": "Oceania", "Vamp": "ANZ"},
        {
            "sub_region": "Sub-Saharan Africa",
            "region": "Africa",
            "Vamp": "MENA",
        },
        {"sub_region": "Melanesia", "region": "Oceania", "Vamp": "ANZ"},
        {"sub_region": "Northern Africa", "region": "Africa", "Vamp": "MENA"},
        {"sub_region": "Southern Asia", "region": "Asia", "Vamp": "Asia"},
        {
            "sub_region": "Southern Europe",
            "region": "Europe",
            "Vamp": "Europe",
        },
        {
            "sub_region": "Australia and New Zealand",
            "region": "Oceania",
            "Vamp": "ANZ",
        },
    ]

    data = data.merge(
        pd.DataFrame(regions), left_on="sub_region", right_on="sub_region"
    )
    cleaned_data = pd.DataFrame(data.groupby(["Vamp", "status"])["count"].sum())
    cleaned_data = cleaned_data.reset_index()
    fig = px.bar(
        cleaned_data,
        x="Vamp",
        y="count",
        color="status",
        color_discrete_sequence=col,
    )
    fig.update_layout(xaxis={"categoryorder": "total descending", "title": "Region"})

    y = dcc.Graph(id="er_graph", figure=fig)
    ELEMENTS = dcc.Tabs(
        children=[
            dbc.Tab(label="Regions", children=[y]),
            dbc.Tab(label="Countries", children=[x]),
        ],
        style={"z-index": "1"},
    )

    return ELEMENTS


def talent_funnel_chart(data):
    regions = [
        {
            "sub_region": "Northern America",
            "region": "Americas",
            "Vamp": "Americas",
        },
        {"sub_region": "Eastern Asia", "region": "Asia", "Vamp": "Asia"},
        {"sub_region": "Central Asia", "region": "Asia", "Vamp": "Asia"},
        {"sub_region": "Eastern Europe", "region": "Europe", "Vamp": "Europe"},
        {"sub_region": "South-eastern Asia", "region": "Asia", "Vamp": "Asia"},
        {
            "sub_region": "Latin America and the Caribbean",
            "region": "Americas",
            "Vamp": "Americas",
        },
        {"sub_region": "Western Asia", "region": "Asia", "Vamp": "MENA"},
        {
            "sub_region": "Northern Europe",
            "region": "Europe",
            "Vamp": "Europe",
        },
        {"sub_region": "Western Europe", "region": "Europe", "Vamp": "Europe"},
        {"sub_region": "Micronesia", "region": "Oceania", "Vamp": "ANZ"},
        {"sub_region": "Polynesia", "region": "Oceania", "Vamp": "ANZ"},
        {
            "sub_region": "Sub-Saharan Africa",
            "region": "Africa",
            "Vamp": "MENA",
        },
        {"sub_region": "Melanesia", "region": "Oceania", "Vamp": "ANZ"},
        {"sub_region": "Northern Africa", "region": "Africa", "Vamp": "MENA"},
        {"sub_region": "Southern Asia", "region": "Asia", "Vamp": "Asia"},
        {
            "sub_region": "Southern Europe",
            "region": "Europe",
            "Vamp": "Europe",
        },
        {
            "sub_region": "Australia and New Zealand",
            "region": "Oceania",
            "Vamp": "ANZ",
        },
    ]
    global_data = data.merge(
        pd.DataFrame(regions), left_on="sub_region", right_on="sub_region"
    )
    global_data = global_data.drop("sub_region", axis=1)
    global_data = pd.melt(global_data, id_vars="Vamp")
    global_data.columns = ["region", "key", "value"]
    global_data = global_data.loc[global_data["key"] != "region"]
    global_data = global_data.groupby(["region", "key"]).sum()
    global_data = global_data.reset_index()
    data = data.drop("sub_region", axis=1)
    data = data.sum(axis=0)
    data = data.transpose().reset_index()
    # rint(global_data)
    data.columns = ["key", "value"]
    data["lag"] = data["value"].shift(1)
    data["lag_key"] = data["key"].shift(1).fillna("")
    data["lag_key"] = data["lag_key"].apply(lambda x: f"of {x}" if x != "" else x)

    data["growth"] = (data["value"] / data["lag"]) * 100
    fig = px.bar(data, x="key", y="value", text="growth", custom_data=["lag_key"])
    fig.update_layout(
        xaxis={"categoryorder": "total descending", "title": "Brief Response"}
    )
    fig.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig.update_traces(
        hovertemplate="<i>%{x}:</i> %{y:,.0f} <br>%{text:.2f}% %{customdata[0]}"
    )

    # return dcc.Graph(
    #    id='brief_locations_plot',
    #    figure= fig
    # )

    y = dcc.Graph(id="er_graph", figure=fig)
    colours = {
        "status": ["ANZ", "Europe", "Asia", "MENA", "Americas"],
        "colour": ["#c55cdb", "#fbbc05", "#07a8f3", "#86e0fb", "#ff5177"],
    }

    global_data["region"] = pd.Categorical(
        global_data["region"],
        ["ANZ", "Europe", "Asia", "MENA", "Americas"],
        ordered=True,
    )
    global_data["key"] = pd.Categorical(
        global_data["key"],
        ["sent", "notifications", "active", "viewed", "applied", "selected"],
        ordered=True,
    )

    global_data = global_data.sort_values(["region", "key"])
    shifted = global_data.groupby("region")["value"].shift(1)
    global_data = global_data.reset_index(drop=True)
    shifted = shifted.reset_index()
    shifted.columns = ["index", "lag"]
    global_data = pd.concat([global_data, shifted], axis=1)
    global_data["growth"] = (global_data["value"] / global_data["lag"]) * 100
    global_data = global_data.sort_values(["region"])

    col = [
        colours["colour"][i]
        for i in range(0, 5)
        if np.any(colours["status"][i] == global_data["region"])
    ]
    fig = px.bar(
        global_data,
        x="key",
        y="value",
        color="region",
        color_discrete_sequence=col,
        text="growth",
        barmode="group",
    )
    fig.update_layout(
        xaxis={"categoryorder": "total descending", "title": "Brief Response"}
    )
    fig.update_layout(
        yaxis=dict(title="Briefs"), legend_title_text="Region", barmode="group"
    )
    fig.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig.update_traces(hovertemplate="<i>%{x}:</i> %{y:,.0f}")

    x = dcc.Graph(id="er_graph", figure=fig)
    ELEMENTS = dcc.Tabs(
        children=[
            dbc.Tab(label="Global", children=[y]),
            dbc.Tab(label="Regional", children=[x]),
        ],
        style={"z-index": "1"},
    )
    return ELEMENTS


def gender_segementation_chart(data):

    cleaned_data = pd.DataFrame(data["gender"].value_counts())
    cleaned_data = cleaned_data.reset_index()

    x = dcc.Graph(
        id="gender_graph",
        figure={
            "data": [
                {
                    "values": cleaned_data["gender"],
                    "labels": cleaned_data["index"].str.title(),
                    "type": "pie",
                    "hole": 0.6,
                    "name": "Other",
                    "marker": {"colors": ["#17bdfe", "#fe3769", "#eeeeee"]},
                }
            ],
            "layout": {"title": "", "yaxis": {"title": ""}, "hole": 0.6},
        },
    )
    return x


def age_segementation_chart(data):

    cleaned_data = pd.DataFrame(data["age"].value_counts())
    cleaned_data = cleaned_data.reset_index()

    fig = px.bar(cleaned_data, x="index", y="age")
    fig.update_layout(
        xaxis=dict(title="Age"), yaxis=dict(title="Number of Influencers")
    )
    fig.update_traces(hovertemplate="<i>%{y} Influecners are %{x} years old</i>")
    fig.update_traces(marker_color="#17bdfe")

    x = dcc.Graph(id="age_graph", figure=fig)
    return x


def followers_segementation_chart(data):
    data["followers_band"] = np.where(
        data["followers_count"] < 10000,
        "0-10k",
        np.where(
            data["followers_count"] < 25000,
            "10-25k",
            np.where(
                data["followers_count"] < 50000,
                "25-50k",
                np.where(
                    data["followers_count"] < 100000,
                    "50-100k",
                    np.where(data["followers_count"] >= 100000, "100k+", "Unknown"),
                ),
            ),
        ),
    )

    cleaned_data = pd.DataFrame(data["followers_band"].value_counts())
    cleaned_data = cleaned_data.reset_index()

    follow_order = ["0-10k", "10-25k", "25-50k", "50-100k", "100k+"]
    fig = px.bar(
        cleaned_data,
        x="index",
        y="followers_band",
        text="followers_band",
        orientation="v",
    )
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig.update_layout(
        xaxis=dict(title="", categoryorder="array", categoryarray=follow_order),
        yaxis=dict(title="Number of Influencers"),
    )
    fig.update_traces(
        hovertemplate="<i>Influencers:</i> %{y}<br><i>Followers:</i> %{x}"
    )
    fig.update_traces(marker_color="#17bdfe")

    x = dcc.Graph(id="followers_band_graph", figure=fig)
    return x


def er_segementation_chart(data):

    fig = px.histogram(data, x="engagement_rate", range_x=[0, 25])
    fig.update_layout(
        xaxis=dict(title="Engagement (%)"),
        yaxis=dict(title="Number of Influencers"),
    )
    fig.update_traces(
        hovertemplate="<i>Influencers:</i> %{y}<br><i>Engagement Rate:</i> %{x}%"
    )
    fig.update_traces(marker_color="#17bdfe")

    # set bin size
    fig.update_traces(
        xbins=dict(start=0.0, end=25.0, size=0.5)  # bins used for histogram
    )

    x = dcc.Graph(id="er_graph", figure=fig)
    return x


def locations_map(data):
    cleaned_data = pd.DataFrame(data["country_sub_code"].value_counts())
    cleaned_data = cleaned_data.reset_index()

    x = dcc.Graph(
        id="er_graph",
        figure={
            "data": [
                {
                    "locations": cleaned_data["index"],
                    "z": cleaned_data["country_sub_code"],
                    "type": "choropleth",
                    "name": "Other",
                    "locationmode": "countries",
                    "hoverinfo": "countries",
                    "colorscale": [
                        [0.00, "#17bdfe"],
                        [0.25, "#eeeeee"],
                        [1, "#fe3769"],
                    ],
                    "autocolorscale": False,
                    "marker_line_color": "white",
                }
            ],
            "layout": {
                "title": "",
                "margin": {"r": 0, "t": 0, "l": 0, "b": 0},
                "geo": {
                    "showframe": False,
                    "fitbounds": "locations",
                    "resolution": 50,
                },
            },
        },
    )
    return x


def build_draft_times_chart(data):
    data["draft_days_band"] = np.where(
        data["days_in_draft"] == 0,
        "Within 24 Hours",
        np.where(
            data["days_in_draft"] < 6,
            "1-5 Days",
            np.where(
                data["days_in_draft"] < 11,
                "6-10 Days",
                np.where(
                    data["days_in_draft"] < 21,
                    "10-20 Days",
                    "More than 20 Days",
                ),
            ),
        ),
    )

    cleaned_data = data["draft_days_band"].value_counts()
    cleaned_data = cleaned_data.reset_index()

    draft_order = [
        "Within 24 Hours",
        "1-5 Days",
        "6-10 Days",
        "10-20 Days",
        "More than 20 Days",
    ]
    fig = px.bar(
        cleaned_data,
        x="index",
        y="draft_days_band",
        text="draft_days_band",
        orientation="v",
    )
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig.update_layout(
        xaxis=dict(title="", categoryorder="array", categoryarray=draft_order),
        yaxis=dict(title=""),
    )
    fig.update_traces(hovertemplate="<i>Drafts:</i> %{y}<br><i>Time in draft:</i> %{x}")
    fig.update_traces(marker_color="#17bdfe")

    x = dcc.Graph(id="draft_times_graph", figure=fig)
    return x


def build_content_type_chart(data):

    fig = px.bar(
        data,
        x="deliverables_count",
        y="deliverable_type",
        text="deliverables_count",
        orientation="h",
    )
    fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig.update_layout(
        xaxis=dict(title=""),
        yaxis=dict(title="Deliverables", categoryorder="total ascending"),
    )
    fig.update_xaxes(range=[0, data["deliverables_count"].max() + 5])
    fig.update_traces(hovertemplate="<i>%{y}:</i> %{x}")
    fig.update_traces(marker_color="#17bdfe")

    x = dcc.Graph(id="draft_times_graph", figure=fig)
    return x


def build_campaign_status_chart(data):

    camp_stat_order = [
        "Draft",
        "Ready for Shortlisting",
        "Ready for Approval",
        "Rejected",
        "Active",
        "Fulfilled",
        "Paid",
    ]
    fig = px.bar(
        data,
        x="campaign_status",
        y="campaign_count",
        text="campaign_count",
        orientation="v",
    )
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig.update_layout(
        xaxis=dict(title="", categoryorder="array", categoryarray=camp_stat_order),
        yaxis=dict(title=""),
    )
    fig.update_traces(hovertemplate="<i>%{y} Campaigns %{x}</i>")
    fig.update_traces(marker_color="#17bdfe")

    x = dcc.Graph(id="campaign_status", figure=fig)
    return x


def campaigns_map(cleaned_data):

    x = dcc.Graph(
        id="er_graph",
        figure={
            "data": [
                {
                    "locations": cleaned_data["sub_code"],
                    "z": cleaned_data["locations"],
                    "type": "choropleth",
                    "name": "Other",
                    "locationmode": "countries",
                    "hoverinfo": "countries",
                    "colorscale": [
                        [0.00, "white"],
                        [0.25, "#9fdcf3"],
                        [1, "#17bdfe"],
                    ],
                    "autocolorscale": False,
                    "marker_line_color": "white",
                }
            ],
            "layout": {
                "title": "",
                "coloraxis_showscale": False,
                "margin": {"r": 0, "t": 0, "l": 0, "b": 0},
                "geo": {
                    "showframe": False,
                    "fitbounds": "locations",
                    "resolution": 50,
                },
            },
        },
    )
    data = cleaned_data.loc[cleaned_data["locations"] > 0].nlargest(10, "locations")
    fig = px.bar(data, x="country", y="locations", text="locations")
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig.update_traces(
        hovertemplate="<i>Country:</i> %{x} <br><i>New Opportunities:</i> %{y}"
    )
    fig.update_traces(marker_color="#17bdfe")

    y = dcc.Graph(id="draft_times_graph", figure=fig)

    ELEMENT = dcc.Tabs(
        children=[
            dbc.Tab(label="Bar Chart", children=[y]),
            dbc.Tab(label="Map", children=[x]),
        ],
        style={"z-index": "1", "margin-bottom": "-65px"},
    )

    return ELEMENT


def build_booked_revenue_chart(data):

    cat_order = [
        str(y) + "-" + pd.to_datetime(x, format="%m").month_name()
        for y in range(2017, datetime.datetime.now().year + 1)
        for x in range(1, 13)
    ]

    data["start_month"] = pd.to_datetime(data["start_month"].astype(int), format="%m")
    data["year-month"] = (
        data["start_year"].astype(int).astype(str)
        + "-"
        + data["start_month"].dt.month_name().astype(str)
    )
    cat_order = [i for i in cat_order if i in data["year-month"].tolist()]
    data["adjusted_budget"] = data["adjusted_budget"].fillna(0)
    data = pd.DataFrame(
        data.loc[:, ["adjusted_budget", "campaign_status", "year-month"]]
        .groupby(["campaign_status", "year-month"])["adjusted_budget"]
        .sum()
    ).reset_index()

    colours = {
        "status": ["Active", "Complete", "Draft", "In Moderation"],
        "colour": ["#07a8f3", "#fbbc05", "#bbbbbb", "#ff5177"],
    }
    col = [
        colours["colour"][i]
        for i in range(0, 4)
        if np.any(colours["status"][i] == data["campaign_status"])
    ]

    fig = px.bar(
        data.sort_values("campaign_status"),
        x="year-month",
        y="adjusted_budget",
        color="campaign_status",
        color_discrete_sequence=col,
    )
    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="Budget"),
        legend_title_text="Campaign Status",
    )
    x = dcc.Graph(id="booked_revenue", figure=fig)

    return x


def build_managed_revenue_chart(data):

    cat_order = [
        str(y) + "-" + pd.to_datetime(x, format="%m").month_name()
        for y in range(2017, datetime.datetime.now().year + 1)
        for x in range(1, 13)
    ]

    cat_order = [i for i in cat_order if i in data["year-month"].tolist()]
    data["adjusted_budget"] = data["adjusted_budget"].fillna(0)
    data["service"] = data["has_managed_service"].apply(
        lambda x: "High Touch" if x else "Low Touch"
    )
    data = pd.DataFrame(
        data.loc[:, ["adjusted_budget", "service", "year-month"]]
        .groupby(["service", "year-month"])["adjusted_budget"]
        .sum()
    ).reset_index()

    colours = {
        "status": ["High Touch", "Low Touch"],
        "colour": ["#07a8f3", "#fbbc05"],
    }
    col = [
        colours["colour"][i]
        for i in range(0, 2)
        if np.any(colours["status"][i] == data["service"])
    ]

    fig = px.bar(
        data,
        x="year-month",
        y="adjusted_budget",
        color="service",
        color_discrete_sequence=col,
    )
    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="Budget"),
        legend_title_text="Service",
    )
    x = dcc.Graph(id="booked_revenue_managed", figure=fig)

    return x


def build_campaign_applications_chart(data):
    data["applications_band"] = np.where(
        data["applications"] == 0,
        "0 Campaigns",
        np.where(
            data["applications"] < 6,
            "1-5 Campaigns",
            np.where(
                data["applications"] < 11,
                "6-10 Campaigns",
                np.where(
                    data["applications"] < 21,
                    "11-20 Campaigns",
                    "More than <br> 20 Campaigns",
                ),
            ),
        ),
    )

    cleaned_data = data["applications_band"].value_counts()
    cleaned_data = cleaned_data.reset_index()

    camp_order = [
        "0 Campaigns",
        "1-5 Campaigns",
        "6-10 Campaigns",
        "11-20 Campaigns",
        "More than <br> 20 Campaigns",
    ]
    fig = px.bar(
        cleaned_data,
        x="index",
        y="applications_band",
        text="applications_band",
        orientation="v",
    )
    fig.update_layout(
        xaxis=dict(title="", categoryorder="array", categoryarray=camp_order),
        yaxis=dict(title=""),
    )
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig.update_traces(
        hovertemplate="<i>No. Talent:</i> %{y:,.0f}<br><i>Applied to:</i> %{x}"
    )
    fig.update_traces(marker_color="#17bdfe")

    y = dcc.Graph(id="draft_times_graph", figure=fig)
    return y


# def build_talent_locations_chart(data):


def self_serve_campaigns_chart(data):

    data.columns = ["team_name", "campaigns_run"]
    data["campaigns_run"] = np.where(
        data["campaigns_run"] < 2,
        "1 Campaign",
        np.where(data["campaigns_run"] < 6, "2-5 Campaigns", "More than 5 Campaigns"),
    ).astype(str)
    # cleaned_data = data['team_name'].value_counts()
    # cleaned_data = cleaned_data.reset_index()
    cleaned_data = data["campaigns_run"].value_counts()
    cleaned_data = cleaned_data.reset_index()
    cleaned_data.columns = ["index", "number_of_teams"]

    data = pd.DataFrame(
        [
            {"xaxis": i, "yaxis": 0}
            for i in ["1 Campaign", "2-5 Campaigns", "More than 5 Campaigns"]
            if i not in cleaned_data["index"].unique()
        ]
    )
    data2 = pd.DataFrame(
        [
            {
                "xaxis": i,
                "yaxis": int(
                    cleaned_data.loc[cleaned_data["index"] == i]["number_of_teams"]
                ),
            }
            for i in ["1 Campaign", "2-5 Campaigns", "More than 5 Campaigns"]
            if i in cleaned_data["index"].unique()
        ]
    )

    clean_data = data.append(data2)
    clean_data["xaxis"] = pd.Categorical(
        clean_data["xaxis"],
        ["1 Campaign", "2-5 Campaigns", "More than 5 Campaigns"],
        ordered=True,
    )
    clean_data = clean_data.sort_values("xaxis").reset_index(drop=True)
    clean_data["text"] = clean_data["yaxis"] * 100 / sum(clean_data["yaxis"])
    fig = px.bar(clean_data, x="xaxis", y="yaxis", text="text")
    fig.update_layout(
        xaxis=dict(title="Number of Campaigns"),
        yaxis=dict(title="Number of Self Serve Customers"),
    )
    fig.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig.update_traces(hovertemplate="<i>%{y} Customer(s) have completed %{x}</i>")
    fig.update_traces(marker_color="#17bdfe")

    y = dcc.Graph(id="self_briefs_chart", figure=fig)
    return [
        y,
        html.P(
            "New Customer is defined as a team that started their first campaign within"
            " the specified time period.",
            style={"color": "red"},
        ),
    ]


def self_serve_locations(data):

    data = data.fillna(value="N/A")
    cleaned_data = pd.DataFrame(
        [
            {
                "locations": l,
                "managed_service": "High Touch" if q else "Low Touch",
            }
            for i, q in zip(data["desired_location"], data["has_managed_service"])
            for l in i.split(",")
            if i != None
        ]
    )
    cleaned_data = pd.DataFrame(
        cleaned_data.groupby("managed_service")["locations"].value_counts()
    )
    cleaned_data.columns = ["count"]
    cleaned_data = cleaned_data.reset_index()

    fig = px.bar(
        cleaned_data,
        x="locations",
        y="count",
        color="managed_service",
        color_discrete_sequence=["#07a8f3", "#bbbbbb"],
    )
    fig.update_layout(
        xaxis={
            "categoryorder": "total descending",
            "title": "Location",
            "type": "category",
        },
        yaxis={"title": "Campaigns"},
        legend_title_text="Services",
    )

    y = dcc.Graph(id="new_vs_returning_business", figure=fig)
    return y


def ss_lifecycle_chart(data):
    clean_data = data["segment"].value_counts()
    clean_data = clean_data.reset_index()
    clean_data.columns = ["segment", "count"]
    fig = px.bar(clean_data, x="segment", y="count")
    fig.update_layout(
        xaxis={
            "categoryorder": "total descending",
            "title": "Customer Segment",
            "type": "category",
        },
        yaxis={"title": "Customers"},
    )

    y = dcc.Graph(id="new_vs_returning_business", figure=fig)

    return [
        y,
        html.P(
            "Note that this chart only applies to customers who joined after September"
            " 2020",
            style={"color": "red"},
        ),
    ]


def new_vs_returning_business_chart(data, currency):
    data["new_business"] = np.where(
        data["cumulative_campaigns"] == 1, "New Revenue", "Returning Revenue"
    )

    plot_data = pd.DataFrame(
        data.groupby(["new_business", "status"])["adjusted_budget"].sum()
    ).reset_index()

    colours = {
        "status": ["Active", "Complete", "Draft", "In Moderation", "Other"],
        "colour": ["#07a8f3", "#fbbc05", "#bbbbbb", "#ff5177", "#ff5177"],
    }
    col = [
        colours["colour"][i]
        for i in range(0, 5)
        if np.any(colours["status"][i] == data["status"])
    ]

    fig = px.bar(
        plot_data.sort_values("status"),
        x="new_business",
        y="adjusted_budget",
        color="status",
        color_discrete_sequence=col,
    )
    fig.update_layout(
        xaxis={"title": ""},
        yaxis={"title": "Budget (" + str(currency) + ")"},
        legend_title_text="Campaign Status",
    )

    x = dcc.Graph(id="new_vs_returning_business", figure=fig)

    return x


def brief_locations_chart(data, currency):
    colours = {
        "status": ["Active", "Complete", "Draft", "In Moderation", "Other"],
        "colour": ["#07a8f3", "#fbbc05", "#bbbbbb", "#ff5177", "#ff5177"],
    }
    col = [
        colours["colour"][i]
        for i in range(0, 5)
        if np.any(colours["status"][i] == data["status"])
    ]

    cleaned_data = pd.DataFrame(
        [
            {
                "location": l,
                "status": data["status"][i],
                "budget": data["adjusted_budget"][i]
                / len(data["desired_location"][i].split(",")),
            }
            for i in range(0, len(data))
            if data["desired_location"][i] is not None
            for l in data["desired_location"][i].split(",")
        ]
    )
    plot_data = pd.DataFrame(
        cleaned_data.groupby(["location", "status"])["budget"].sum()
    ).reset_index()
    fig = px.bar(
        plot_data.sort_values("status"),
        x="location",
        y="budget",
        color="status",
        color_discrete_sequence=col,
    )
    fig.update_layout(
        xaxis={"categoryorder": "total descending", "title": "Location"},
        yaxis={"title": "Budget (" + str(currency) + ")"},
        legend_title_text="Campaign Status",
    )
    x = dcc.Graph(id="brief_locations_plot", figure=fig)
    return x


"""
--------------------------------------------------------------------------------
                        Influencer Usage Graphs
--------------------------------------------------------------------------------
"""


def iu_cumulative_scatter(data):
    # Convert porportion to percentage
    data["cumsum"] = data["cumsum"] * 100
    data["position"] = [i + 1 for i in range(len(data))]
    data["position"] = data["position"] / len(data) * 100
    data["inverse_cumsum"] = 100 - data["cumsum"]
    data["inverse_position"] = 100 - data["position"]

    # Round to 2dp
    data[["inverse_cumsum", "inverse_position"]] = data[
        ["inverse_cumsum", "inverse_position"]
    ].round(2)

    fig = px.line(
        data,
        x="position",
        y="cumsum",
        title="",
        range_x=(0, 100),
        range_y=(0, 100),
        custom_data=["inverse_cumsum", "inverse_position"],
    )

    fig.update_layout(
        xaxis={"title": "Cumulative proportion of Influencers"},
        yaxis={"title": "Cumulative proportion of Campaigns"},
        hoverlabel={"bgcolor": "white"},
    )

    fig.update_traces(
        hovertemplate="<br>".join(
            [
                "<i>Top %{customdata[1]}% of Influencers",
                "Participated in %{customdata[0]}% of briefs</i>",
            ]
        )
    )

    return dcc.Graph(id="brief_locations_plot", figure=fig)


"""
--------------------------------------------------------------------------------
                        Influencer Lookup Graphs
--------------------------------------------------------------------------------
"""


def il_brief_barchart(data):
    idx = ["Successful", "Unsucessful", "Applied", "Viewed", "Did not view"]

    # check
    status_counts = data["new_status"].value_counts()
    status_counts = (
        status_counts.reindex(idx, fill_value=0)
        .reset_index()
        .rename(columns={"index": "statuses", "new_status": "count"})
    )
    print(status_counts.head())

    fig = px.bar(status_counts, x="statuses", y="count", color="statuses")

    x = dcc.Graph(id="new-talent", figure=fig)
    return x


def il_create_distribution(current_pos, dist, key):
    max_x = dist[key].max() if key != "engagement_percent" else 50

    fig = px.histogram(dist, x=key, range_x=[0, max_x], nbins=500)
    fig.add_shape(
        type="line",
        x0=current_pos,
        y0=0,
        x1=current_pos,
        y1=20,
        line=dict(color="Red", width=3),
    )

    return dcc.Graph(id=f"il-{key}-dist", figure=fig)


def map_gender_age(tag):
    if tag.startswith("M"):
        return "Male"
    elif tag.startswith("F"):
        return "Female"
    else:
        return "Unknown"


def il_audience_stats(audience):
    not_outdated = audience.iloc[0]["token_valid"]

    coutries = audience.loc[audience["category"] == "countries"].copy()
    gender = audience.loc[audience["category"] == "gender"].copy()
    age = audience.loc[audience["category"] == "gender_age"].copy()

    coutries = coutries.sort_values(["percentage"], ascending=False)
    country_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Top 15 Countries"),
                    html.Th("Audience (%)"),
                    html.Th("Audience (#)"),
                ]
            )
        )
    ]
    country_rows = [
        html.Tr(
            [
                html.Td(row["tag"]),
                html.Td(round(row["percentage"] * 100, 2)),
                html.Td(row["value"]),
            ]
        )
        for idx, row in coutries.iloc[:15, :].iterrows()
    ]
    country_table = dbc.Table(
        country_header + [html.Tbody(country_rows)],
        striped=True,
        bordered=True,
        hover=True,
    )

    gender["tag"] = gender["tag"].apply(lambda x: map_gender_age(x))
    gender_graph = dcc.Graph(
        id="il_gender_graph",
        figure={
            "data": [
                {
                    "values": gender["value"],
                    "labels": gender["tag"],
                    "type": "pie",
                    "hole": 0.6,
                    "name": "Other",
                    "marker": {"colors": ["#17bdfe", "#fe3769", "#eeeeee"]},
                }
            ],
            "layout": {"title": "", "yaxis": {"title": ""}, "hole": 0.6},
        },
    )

    age["gender"] = age["tag"].apply(lambda x: map_gender_age(x))
    age["tag"] = age["tag"].apply(lambda x: x.split(".")[1])
    age = age.rename(columns={"tag": "ages"})
    age_fig = px.bar(age, x="ages", y="value", color="gender", barmode="group")
    age_fig.update_layout(
        xaxis={
            "categoryorder": "array",
            "categoryarray": sorted(age["ages"].unique()),
        }
    )

    age_graph = dcc.Graph(id="age_graph", figure=age_fig)

    if not_outdated:
        return dbc.Row(
            [
                dbc.Col(
                    [dbc.Col([html.Div([country_table])])],
                    md=6,
                    style={"overflow": "scroll"},
                ),
                dbc.Col(
                    [
                        dbc.Row([dbc.Col([gender_graph], md=12)]),
                        dbc.Row([dbc.Col([age_graph], md=12)]),
                    ],
                    md=6,
                ),
            ]
        )

    else:
        return dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Alert(
                            "Warning, the social token is out of date and statistics"
                            " may not be up to date",
                            color="warning",
                            dismissable=True,
                            is_open=True,
                        )
                    ],
                    md=12,
                ),
                dbc.Col(
                    [dbc.Col([html.Div([country_table])])],
                    md=6,
                    style={"overflow": "scroll"},
                ),
                dbc.Col(
                    [
                        dbc.Row([dbc.Col([gender_graph], md=12)]),
                        dbc.Row([dbc.Col([age_graph], md=12)]),
                    ],
                    md=6,
                ),
            ]
        )


"""
--------------------------------------------------------------------------------
                        Influencer Usage Graphs
--------------------------------------------------------------------------------
"""


def cl_briefs_barchart(briefs, notifications):
    # Convert porportion to percentage
    briefs = briefs.groupby(["influencer_id"]).first()

    total = len(briefs)
    successful_note = notifications["brief_id"].nunique()

    # convert dates
    # minus 31 from inserted at
    briefs["minus_days"] = 31
    last_active_sent = pd.to_datetime(briefs["brief_last_active_brief_sent"]).apply(
        lambda x: x.replace(tzinfo=None)
    )
    inserted_at = pd.to_datetime(briefs["brief_inserted_at"]).apply(
        lambda x: x.replace(tzinfo=None)
    ) - pd.to_timedelta(briefs["minus_days"], unit="d")

    total_active = len(briefs.loc[last_active_sent > inserted_at, :])
    viewed = len(briefs.loc[briefs["brief_is_viewed"] == True, :])
    applied = len(
        briefs.loc[briefs["brief_status_id"].isin([3, 5, 6, 7, 8, 11, 13]), :]
    )

    100 if total < 100 else total

    stat_order = [
        "Total Sent",
        "Successful Notification",
        "Active",
        "Viewed",
        "Applied",
    ]
    data = pd.DataFrame(
        {
            "status": stat_order,
            "value": [total, successful_note, total_active, viewed, applied],
        }
    )

    data["percent"] = data["value"] * 100 / data["value"].shift(1)
    data["percent"].fillna(0, inplace=True)
    data["percent_label"] = data["status"].shift(1)
    data["percent_label"].fillna("", inplace=True)
    data["status"] = pd.Categorical(data["status"], stat_order)
    data = data.sort_values("status")

    fig = px.bar(
        data,
        x="status",
        y="value",
        text="percent",
        custom_data=["percent_label"],
    )
    fig.update_layout(
        xaxis=dict(title="", categoryorder="array", categoryarray=stat_order),
        yaxis=dict(title=""),
    )
    fig.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig.update_traces(
        hovertemplate="<i>%{x}:</i> %{y}<br><i>%{text:.2f}% of %{customdata[0]}</i>"
    )
    fig.update_traces(marker_color="#17bdfe")

    return dcc.Graph(id="cl_brief_stats", figure=fig)


"""
--------------------------------------------------------------------------------
                        Platform Statistics Charts
--------------------------------------------------------------------------------
"""


def cumulative_campaigns_bar_chart(data, period):

    if period == "quarterly":
        cat_order = [
            str(y) + "-" + x
            for y in range(2017, datetime.datetime.now().year + 2)
            for x in ["quarter-1", "quarter-2", "quarter-3", "quarter-4"]
        ]
        cat_order_col = "year-quarter"
    elif period == "yearly":
        cat_order = [str(y) for y in range(2017, datetime.datetime.now().year + 2)]
        cat_order_col = "financial_year"
    else:
        cat_order = [
            str(y) + "-" + pd.to_datetime(x, format="%m").month_name()
            for y in range(2017, datetime.datetime.now().year + 1)
            for x in range(1, 13)
        ]
        cat_order_col = "year-month"

    cat_order = [i for i in cat_order if i in data[cat_order_col].tolist()]
    global_data = pd.DataFrame(data[cat_order_col].value_counts()).reset_index()
    global_data.columns = ["month", "count"]
    global_data["month"] = pd.Categorical(global_data["month"].astype(str), cat_order)
    global_data = global_data.sort_values(by="month", axis=0).reset_index(drop=True)
    global_data["growth"] = (
        (global_data["count"] / global_data["count"].shift(1)) - 1
    ) * 100
    global_data["growth"] = global_data["growth"].fillna(0).round(2)
    fig = px.bar(global_data, x="month", y="count", text="growth")
    fig.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig.update_traces(
        hovertemplate=(
            "<i>Period:</i> %{x} <br><i>Campaigns:</i> %{y} <br><i>Growth:</i>%{text:"
            " .2f}%"
        )
    )
    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="Campaigns"),
        legend_title_text="Month",
    )
    x = dcc.Graph(id="cumulative_campaigns_chart", figure=fig)

    region_data = pd.DataFrame(
        data.loc[:, [cat_order_col, "region"]].value_counts()
    ).reset_index()
    region_data.columns = ["month", "region", "count"]
    region_data["month"] = pd.Categorical(region_data["month"].astype(str), cat_order)
    region_data = region_data.sort_values(by="month", axis=0).reset_index(drop=True)
    shifted = region_data.groupby("region")["count"].shift(1)
    shifted = shifted.reset_index()
    shifted.columns = ["index", "lag"]
    region_data = pd.concat([region_data, shifted], axis=1)
    region_data["region"] = pd.Categorical(
        region_data["region"],
        ["ANZ", "Europe", "Asia", "MENA", "Americas", "multi-region"],
    )

    region_data["growth"] = ((region_data["count"] / region_data["lag"]) - 1) * 100

    region_data.sort_values(["region"], ascending=True, inplace=True)
    fig2 = px.bar(
        region_data,
        x="month",
        y="count",
        color="region",
        text="growth",
        barmode="group",
    )
    fig2.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="Campaigns"),
        legend_title_text="Month",
        barmode="group",
    )
    fig2.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig2.update_traces(
        hovertemplate=(
            "<i>Period:</i> %{x} <br><i>Campaigns:</i> %{y} <br><i>Growth:</i>%{text:"
            " .2f}%"
        )
    )

    y = dcc.Graph(id="cumulative_campaigns_chart_region", figure=fig2)

    ELEMENTS = [
        dcc.Tabs(
            children=[
                dbc.Tab(label="Global", children=[x]),
                dbc.Tab(label="Regional", children=[y]),
            ],
            style={"z-index": "1"},
        ),
        dbc.Row(
            [
                html.P(
                    "Campaigns are counted based on when the 'start camapign' button"
                    " was clicked. Campaigns prior to Sep 2020 are not counted as this"
                    " date was not recorded.",
                    style={
                        "color": "red",
                        "font-weight": "300",
                        "font-style": "italic",
                        "font-size": "9px",
                        "padding": "10px",
                    },
                )
            ]
        ),
    ]
    return ELEMENTS


def high_touch_low_touch_bar_chart(data):

    global_data = pd.DataFrame(data["has_managed_service"].value_counts()).reset_index()

    global_data.columns = ["service_level", "count"]
    levels = {True: "High Touch", False: "Low Touch"}
    global_data.replace({"service_level": levels}, inplace=True)
    global_data["Proportion"] = global_data["count"] * 100 / sum(global_data["count"])

    fig = px.bar(global_data, x="service_level", y="count", text="Proportion")
    fig.update_layout(
        xaxis=dict(
            categoryorder="array",
            categoryarray=["High Touch", "Low Touch"],
            title="",
        ),
        yaxis=dict(title="Campaigns"),
        legend_title_text="Service Level",
    )
    fig.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig.update_traces(
        hovertemplate=(
            "<br><i>Campaigns:</i> %{y: .0f} <br><i>Proportion: </i>%{text: .2f}%"
        )
    )

    x = dcc.Graph(id="managed_service_global_chart", figure=fig)

    region_data = pd.DataFrame(
        data.loc[:, ["has_managed_service", "region"]].value_counts()
    ).reset_index()
    region_data.columns = ["has_managed_service", "region", "count"]
    region_data.columns = ["service_level", "region", "count"]
    region_data.replace({"service_level": levels}, inplace=True)

    global_data["total_count"] = global_data["count"]
    region_data = region_data.merge(
        global_data.loc[:, ["service_level", "total_count"]],
        left_on="service_level",
        right_on="service_level",
    )
    region_data["Proportion"] = region_data["count"] * 100 / region_data["total_count"]

    region_data["region"] = pd.Categorical(
        region_data["region"],
        ["ANZ", "Europe", "Asia", "MENA", "Americas", "multi-region"],
    )
    region_data = region_data.sort_values("region")

    fig2 = px.bar(
        region_data,
        x="service_level",
        y="count",
        color="region",
        text="Proportion",
        barmode="group",
    )
    fig2.update_layout(
        xaxis=dict(
            categoryorder="array",
            categoryarray=["High Touch", "Low Touch"],
            title="",
        ),
        yaxis=dict(title="Campaigns"),
        legend_title_text="Region",
        barmode="group",
    )
    fig2.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig2.update_traces(
        hovertemplate=(
            "<i>Service Level:</i> %{x} <br><i>Campaigns:</i> %{y:,.0f}"
            " <br><i>Proportion:</i>%{text: .2f}%"
        )
    )

    y = dcc.Graph(id="managed_service_region_chart", figure=fig2)

    ELEMENTS = [
        dcc.Tabs(
            children=[
                dbc.Tab(label="Global", children=[x]),
                dbc.Tab(label="Regional", children=[y]),
            ],
            style={"z-index": "1"},
        ),
        dbc.Row(
            [
                html.P(
                    "High Touch campaigns refer to campaigns with 'campaign"
                    " management'. Low touch campaignd refer to campaigns run without"
                    " the campaign management add on.",
                    style={
                        "color": "red",
                        "font-weight": "300",
                        "font-style": "italic",
                        "font-size": "9px",
                        "padding": "10px",
                    },
                )
            ]
        ),
    ]
    return ELEMENTS


def new_customers_chart(data, period):

    if period == "quarterly":
        cat_order = [
            str(y) + "-" + x
            for y in range(2017, datetime.datetime.now().year + 2)
            for x in ["quarter-1", "quarter-2", "quarter-3", "quarter-4"]
        ]
        cat_order_col = "year-quarter"
    elif period == "yearly":
        cat_order = [str(y) for y in range(2017, datetime.datetime.now().year + 2)]
        cat_order_col = "financial_year"
    else:
        cat_order = [
            str(y) + "-" + pd.to_datetime(x, format="%m").month_name()
            for y in range(2017, datetime.datetime.now().year + 1)
            for x in range(1, 13)
        ]
        cat_order_col = "year-month"

    data = data.loc[data["first_customer_flag"] == "new customer"]

    cat_order = [i for i in cat_order if i in data[cat_order_col].tolist()]
    global_data = pd.DataFrame(
        data.groupby(cat_order_col)["team_name"].nunique()
    ).reset_index()

    global_data.columns = ["month", "count"]
    global_data["month"] = pd.Categorical(global_data["month"], cat_order)
    global_data = global_data.sort_values(by="month", axis=0).reset_index(drop=True)
    global_data["growth"] = (
        (global_data["count"] / global_data["count"].shift(1)) - 1
    ) * 100
    global_data["growth"] = global_data["growth"].fillna(0).round(2)
    fig = px.bar(global_data, x="month", y="count", text="growth")
    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="New Customers"),
        legend_title_text="Month",
    )
    fig.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig.update_traces(
        hovertemplate=(
            "<i>Period:</i> %{x} <br><i>New Customers:</i> %{y}"
            " <br><i>Growth:</i>%{text: .2f}%"
        )
    )
    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="Customers"),
        legend_title_text="Month",
        barmode="group",
    )

    x = dcc.Graph(id="new_customer_regional_chart", figure=fig)

    region_data = pd.DataFrame(
        data.groupby([cat_order_col, "region"])["team_name"].nunique()
    ).reset_index()
    region_data.columns = ["month", "region", "count"]
    region_data["month"] = pd.Categorical(region_data["month"], cat_order)
    region_data = region_data.sort_values(by="month", axis=0).reset_index(drop=True)
    shifted = region_data.groupby("region")["count"].shift(1)
    shifted = shifted.reset_index()
    shifted.columns = ["index", "lag"]
    region_data = pd.concat([region_data, shifted], axis=1)
    region_data["growth"] = ((region_data["count"] / region_data["lag"]) - 1) * 100
    region_data["region"] = pd.Categorical(
        region_data["region"],
        ["ANZ", "Europe", "Asia", "MENA", "Americas", "multi-region"],
    )
    region_data = region_data.sort_values("region")

    fig2 = px.bar(
        region_data,
        x="month",
        y="count",
        color="region",
        text="growth",
        barmode="group",
    )
    fig2.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="Customers"),
        legend_title_text="Month",
        barmode="group",
    )
    fig2.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig2.update_traces(
        hovertemplate=(
            "<i>Period:</i> %{x} <br><i>New Customers:</i> %{y}"
            " <br><i>Growth:</i>%{text: .2f}%"
        )
    )

    y = dcc.Graph(id="new_customers_chart_region", figure=fig2)

    ELEMENTS = [
        dcc.Tabs(
            children=[
                dbc.Tab(label="Global", children=[x]),
                dbc.Tab(label="Regional", children=[y]),
            ],
            style={"z-index": "1"},
        ),
        dbc.Row(
            [
                html.P(
                    "A new customer is acquired when a 'team' starts their first"
                    " campaign.",
                    style={
                        "color": "red",
                        "font-weight": "300",
                        "font-style": "italic",
                        "font-size": "9px",
                        "padding": "10px",
                    },
                )
            ]
        ),
    ]
    return ELEMENTS


def new_vs_returning_customers(data, period):
    if period == "quarterly":
        cat_order = [
            str(y) + "-" + x
            for y in range(2017, datetime.datetime.now().year + 2)
            for x in ["quarter-1", "quarter-2", "quarter-3", "quarter-4"]
        ]
        cat_order_col = "year-quarter"
    elif period == "yearly":
        cat_order = [str(y) for y in range(2017, datetime.datetime.now().year + 2)]
        cat_order_col = "financial_year"
    else:
        cat_order = [
            str(y) + "-" + pd.to_datetime(x, format="%m").month_name()
            for y in range(2017, datetime.datetime.now().year + 1)
            for x in range(1, 13)
        ]
        cat_order_col = "year-month"

    cat_order = [i for i in cat_order if i in data[cat_order_col].tolist()]
    global_data = (
        data.groupby([cat_order_col, "first_customer_flag"])["team_name"]
        .nunique()
        .reset_index()
    )

    global_data.columns = ["month", "new_vs_returning", "count"]
    global_data["month"] = pd.Categorical(global_data["month"], cat_order)
    global_data = global_data.sort_values(
        by=["month", "new_vs_returning"], axis=0
    ).reset_index(drop=True)
    global_data["growth"] = (
        (global_data["count"] / global_data["count"].shift(2)) - 1
    ) * 100
    global_data["growth"] = global_data["growth"].fillna(0).round(2)
    fig = px.bar(
        global_data,
        x="month",
        y="count",
        color="new_vs_returning",
        text="count",
        custom_data=["growth"],
    )
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig.update_traces(
        hovertemplate=(
            "<i>Period:</i> %{x} <br><i>Unique Customers:</i> %{y} <br><i>Growth:"
            " </i>%{customdata[0]: .2f}%"
        )
    )
    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="Unique Customers"),
        legend_title_text="Customer",
        barmode="stack",
    )

    x = dcc.Graph(id="new_customer_regional_chart", figure=fig)

    region_data = (
        data.groupby([cat_order_col, "region", "first_customer_flag"])["team_name"]
        .nunique()
        .reset_index()
    )
    region_data.columns = ["month", "region", "first_customer_flag", "count"]

    for month in cat_order:
        for region in [
            "ANZ",
            "Europe",
            "Asia",
            "MENA",
            "Americas",
            "multi-region",
        ]:
            if (
                len(
                    region_data.loc[
                        (region_data["month"] == month)
                        & (region_data["region"] == region)
                    ]
                )
                == 0
            ):
                region_data = region_data.append(
                    {
                        "month": month,
                        "region": region,
                        "first_customer_flag": "new customer",
                        "count": 0,
                    },
                    ignore_index=True,
                )

    region_data["month"] = pd.Categorical(region_data["month"], cat_order, ordered=True)
    region_data = region_data.sort_values("month")
    region_data = region_data.sort_values(
        by=["region", "first_customer_flag"], axis=0
    ).reset_index(drop=True)

    shifted = region_data.groupby(["region", "first_customer_flag"])["count"].shift(1)
    shifted = shifted.reset_index()
    shifted.columns = ["index", "lag"]
    region_data = pd.concat([region_data, shifted], axis=1)
    region_data["growth"] = ((region_data["count"] / region_data["lag"]) - 1) * 100

    region_data["region"] = pd.Categorical(
        region_data["region"],
        ["ANZ", "Europe", "Asia", "MENA", "Americas", "multi-region"],
    )

    combos = [
        (y, z)
        for y in ["new customer", "return customer"]
        for z in ["ANZ", "Europe", "Asia", "MENA", "Americas", "multi-region"]
    ]
    colours = [
        "#636efa",
        "#ef553b",
        "#00cc96",
        "#ab63fa",
        "#ffa15a",
        "#19d3f3",
        "#636efa",
        "#ef553b",
        "#00cc96",
        "#ab63fa",
        "#ffa15a",
        "#19d3f3",
    ]
    # TODO: Tooltips, legend groups
    fig2 = go.Figure()
    fig2.update_layout(
        xaxis=dict(title_text="Period", categoryorder="array", categoryarray=cat_order),
        yaxis=dict(title_text="Unique Customers"),
        barmode="stack",
    )
    region_data["growth"].replace(np.inf, 100, inplace=True)
    region_data["growth"].replace(-np.inf, -100, inplace=True)
    region_data["growth"].fillna(0, inplace=True)

    i = 0
    for customer_type, region in combos:
        opac = 1 if customer_type == "new customer" else 0.5
        leg = True if region == "ANZ" else False
        temp = region_data.loc[
            (region_data["region"] == region)
            & (region_data["first_customer_flag"] == customer_type)
        ]
        fig2.add_trace(
            go.Bar(
                x=[temp["month"], [region] * len(temp["month"])],
                y=temp["count"],
                name=customer_type,
                text=temp["count"],
                marker_color=colours[i],
                opacity=opac,
                legendgroup=customer_type,
                showlegend=leg,
                customdata=temp["growth"],
            ),
        )
        i += 1

    fig2.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig2.update_traces(
        hovertemplate=(
            "%{x} <br><i>Growth: </i>%{customdata:.2f}% <br><i>Unique Customers:</i>"
            " %{y} "
        )
    )

    y = dcc.Graph(id="new_customers_chart_region", figure=fig2)

    ELEMENTS = [
        dcc.Tabs(
            children=[
                dbc.Tab(label="Global", children=[x]),
                dbc.Tab(label="Regional", children=[y]),
            ],
            style={"z-index": "1"},
        ),
        dbc.Row(
            [
                html.P(
                    "A new customer is acquired when a 'team' starts their first"
                    " campaign.",
                    style={
                        "color": "red",
                        "font-weight": "300",
                        "font-style": "italic",
                        "font-size": "9px",
                        "padding": "10px",
                    },
                )
            ]
        ),
    ]
    return ELEMENTS


def new_vs_returning_customer_campaigns(data, period):
    if period == "quarterly":
        cat_order = [
            str(y) + "-" + x
            for y in range(2017, datetime.datetime.now().year + 2)
            for x in ["quarter-1", "quarter-2", "quarter-3", "quarter-4"]
        ]
        cat_order_col = "year-quarter"
    elif period == "yearly":
        cat_order = [str(y) for y in range(2017, datetime.datetime.now().year + 2)]
        cat_order_col = "financial_year"
    else:
        cat_order = [
            str(y) + "-" + pd.to_datetime(x, format="%m").month_name()
            for y in range(2017, datetime.datetime.now().year + 1)
            for x in range(1, 13)
        ]
        cat_order_col = "year-month"

    cat_order = [i for i in cat_order if i in data[cat_order_col].tolist()]
    global_data = pd.DataFrame(
        data.groupby([cat_order_col, "first_customer_flag"]).size()
    ).reset_index()

    global_data.columns = ["month", "new_vs_returning", "count"]
    global_data["month"] = pd.Categorical(global_data["month"], cat_order)
    global_data = global_data.sort_values(
        by=["month", "new_vs_returning"], axis=0
    ).reset_index(drop=True)
    global_data["growth"] = (
        (global_data["count"] / global_data["count"].shift(2)) - 1
    ) * 100
    global_data["growth"] = global_data["growth"].fillna(0).round(2)
    fig = px.bar(
        global_data,
        x="month",
        y="count",
        color="new_vs_returning",
        text="count",
        custom_data=["growth"],
    )
    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="Campaigns"),
        legend_title_text="Month",
    )
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig.update_traces(
        hovertemplate=(
            "<i>Period:</i> %{x} <br><i>Campaigns:</i> %{y} <br><i>Growth:"
            " </i>%{customdata[0]: .2f}%"
        )
    )
    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="Campaigns"),
        legend_title_text="Customer",
        barmode="stack",
    )

    x = dcc.Graph(id="new_customer_regional_chart", figure=fig)

    region_data = pd.DataFrame(
        data.groupby([cat_order_col, "region", "first_customer_flag"]).size()
    ).reset_index()
    region_data.columns = ["month", "region", "first_customer_flag", "count"]

    for month in cat_order:
        for region in [
            "ANZ",
            "Europe",
            "Asia",
            "MENA",
            "Americas",
            "multi-region",
        ]:
            if (
                len(
                    region_data.loc[
                        (region_data["month"] == month)
                        & (region_data["region"] == region)
                    ]
                )
                == 0
            ):
                region_data = region_data.append(
                    {
                        "month": month,
                        "region": region,
                        "first_customer_flag": "new customer",
                        "count": 0,
                    },
                    ignore_index=True,
                )

    region_data["month"] = pd.Categorical(region_data["month"], cat_order, ordered=True)
    region_data = region_data.sort_values("month")
    region_data = region_data.sort_values(
        by=["region", "first_customer_flag"], axis=0
    ).reset_index(drop=True)

    shifted = region_data.groupby(["region", "first_customer_flag"])["count"].shift(1)
    shifted = shifted.reset_index()
    shifted.columns = ["index", "lag"]
    region_data = pd.concat([region_data, shifted], axis=1)
    region_data["growth"] = ((region_data["count"] / region_data["lag"]) - 1) * 100

    region_data["region"] = pd.Categorical(
        region_data["region"],
        ["ANZ", "Europe", "Asia", "MENA", "Americas", "multi-region"],
    )

    combos = [
        (y, z)
        for y in ["new customer", "return customer"]
        for z in ["ANZ", "Europe", "Asia", "MENA", "Americas", "multi-region"]
    ]
    colours = [
        "#636efa",
        "#ef553b",
        "#00cc96",
        "#ab63fa",
        "#ffa15a",
        "#19d3f3",
        "#636efa",
        "#ef553b",
        "#00cc96",
        "#ab63fa",
        "#ffa15a",
        "#19d3f3",
    ]
    # TODO: Tooltips, legend groups
    fig2 = go.Figure()
    fig2.update_layout(
        xaxis=dict(title_text="Period", categoryorder="array", categoryarray=cat_order),
        yaxis=dict(title_text="Campaigns"),
        barmode="stack",
    )
    region_data["growth"].replace(np.inf, 100, inplace=True)
    region_data["growth"].replace(-np.inf, -100, inplace=True)
    region_data["growth"].fillna(0, inplace=True)

    i = 0
    for customer_type, region in combos:
        opac = 1 if customer_type == "new customer" else 0.5
        leg = True if region == "ANZ" else False
        temp = region_data.loc[
            (region_data["region"] == region)
            & (region_data["first_customer_flag"] == customer_type)
        ]
        fig2.add_trace(
            go.Bar(
                x=[temp["month"], [region] * len(temp["month"])],
                y=temp["count"],
                name=customer_type,
                text=temp["count"],
                marker_color=colours[i],
                opacity=opac,
                legendgroup=customer_type,
                showlegend=leg,
                customdata=temp["growth"],
            ),
        )
        i += 1

    fig2.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig2.update_traces(
        hovertemplate=(
            "%{x} <br><i>Growth: </i>%{customdata:.2f}% <br><i>Campaigns:</i> %{y} "
        )
    )

    y = dcc.Graph(id="new_customers_chart_region", figure=fig2)

    ELEMENTS = [
        dcc.Tabs(
            children=[
                dbc.Tab(label="Global", children=[x]),
                dbc.Tab(label="Regional", children=[y]),
            ],
            style={"z-index": "1"},
        ),
        dbc.Row(
            [
                html.P(
                    "A new customer is acquired when a 'team' starts their first"
                    " campaign.",
                    style={
                        "color": "red",
                        "font-weight": "300",
                        "font-style": "italic",
                        "font-size": "9px",
                        "padding": "10px",
                    },
                )
            ]
        ),
    ]
    return ELEMENTS


def cumulative_revenue_bar_chart(data, period):
    if period == "quarterly":
        cat_order = [
            str(y) + "-" + x
            for y in range(2017, datetime.datetime.now().year + 2)
            for x in ["quarter-1", "quarter-2", "quarter-3", "quarter-4"]
        ]
        cat_order_col = "year-quarter"
    elif period == "yearly":
        cat_order = [str(y) for y in range(2017, datetime.datetime.now().year + 2)]
        cat_order_col = "financial_year"
    else:
        cat_order = [
            str(y) + "-" + pd.to_datetime(x, format="%m").month_name()
            for y in range(2017, datetime.datetime.now().year + 1)
            for x in range(1, 13)
        ]
        cat_order_col = "year-month"

    cat_order = [i for i in cat_order if i in data[cat_order_col].tolist()]
    global_data = pd.DataFrame(
        data.groupby(cat_order_col).agg({"adjusted_budget": pd.Series.sum})
    ).reset_index()
    global_data.columns = ["month", "revenue"]
    global_data["month"] = pd.Categorical(global_data["month"], cat_order)
    global_data = global_data.sort_values(by="month", axis=0).reset_index(drop=True)
    global_data["growth"] = (
        (global_data["revenue"] / global_data["revenue"].shift(1)) - 1
    ) * 100
    fig = px.bar(global_data, x="month", y="revenue", text="growth")

    fig.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig.update_traces(
        hovertemplate=(
            "<i>Period:</i> %{x} <br><i>Revenue:</i> $%{y:,.0f}"
            " <br><i>Growth:</i>%{text: .2f}%"
        )
    )

    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="$AUD"),
        legend_title_text="Month",
    )
    x = dcc.Graph(id="cumulative_revenue_chart", figure=fig)

    region_data = pd.DataFrame(
        data.groupby([cat_order_col, "region"]).agg({"adjusted_budget": pd.Series.sum})
    ).reset_index()
    region_data.columns = ["month", "region", "revenue"]
    region_data["month"] = pd.Categorical(region_data["month"], cat_order)
    region_data = region_data.sort_values(by="month", axis=0).reset_index(drop=True)
    shifted = region_data.groupby("region")["revenue"].shift(1)
    shifted = shifted.reset_index()
    shifted.columns = ["index", "lag"]
    region_data = pd.concat([region_data, shifted], axis=1)
    region_data["growth"] = ((region_data["revenue"] / region_data["lag"]) - 1) * 100

    region_data["region"] = pd.Categorical(
        region_data["region"],
        ["ANZ", "Europe", "Asia", "MENA", "Americas", "multi-region"],
    )
    region_data = region_data.sort_values("region")

    fig2 = px.bar(
        region_data,
        x="month",
        y="revenue",
        color="region",
        text="growth",
        barmode="group",
    )
    fig2.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="Revenue"),
        legend_title_text="Region",
        barmode="group",
    )
    fig2.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig2.update_traces(
        hovertemplate=(
            "<i>Period:</i> %{x} <br><i>Revenue:</i> $%{y:,.0f}"
            " <br><i>Growth:</i>%{text: .2f}%"
        )
    )

    y = dcc.Graph(id="cumulative_campaigns_chart_region", figure=fig2)

    ELEMENTS = [
        dcc.Tabs(
            children=[
                dbc.Tab(label="Global", children=[x]),
                dbc.Tab(label="Regional", children=[y]),
            ],
            style={"z-index": "1"},
        ),
        dbc.Row(
            [
                html.P(
                    "The total budget is recognised revenue once the campaign has"
                    " started.",
                    style={
                        "color": "red",
                        "font-weight": "300",
                        "font-style": "italic",
                        "font-size": "9px",
                        "padding": "10px",
                    },
                )
            ]
        ),
    ]
    return ELEMENTS


def cumulative_camp_service_bar_chart(data, period):
    """
    Generate longitudinal graph of campaigns by service level. The graph should
    display the mothly percentage each service makes up, the growth or decline
    of each month based on the previous months as well as the monthly campaign
    counts for each service
    """
    data["service"] = data["has_managed_service"].apply(
        lambda x: "High Touch" if x else "Low Touch"
    )

    if period == "quarterly":
        cat_order = [
            str(y) + "-" + x
            for y in range(2017, datetime.datetime.now().year + 2)
            for x in ["quarter-1", "quarter-2", "quarter-3", "quarter-4"]
        ]
        cat_order_col = "year-quarter"
    elif period == "yearly":
        cat_order = [str(y) for y in range(2017, datetime.datetime.now().year + 2)]
        cat_order_col = "financial_year"
    else:
        cat_order = [
            str(y) + "-" + pd.to_datetime(x, format="%m").month_name()
            for y in range(2017, datetime.datetime.now().year + 1)
            for x in range(1, 13)
        ]
        cat_order_col = "year-month"

    cat_order = [i for i in cat_order if i in data[cat_order_col].tolist()]
    global_idx = [
        (month, service)
        for month in cat_order
        for service in ["High Touch", "Low Touch"]
    ]
    regional_idx = [
        (month, region, service)
        for month in cat_order
        for region in sorted(data["region"].unique())
        for service in ["High Touch", "Low Touch"]
    ]

    regional_data = data.groupby([cat_order_col, "region"]).agg(
        {"service": "value_counts"}
    )
    global_data = data.groupby([cat_order_col]).agg({"service": "value_counts"})
    global_data.columns = ["count"]
    global_data = global_data.reindex(global_idx, fill_value=0)  # ensures shift by 2
    global_data = global_data.reset_index()

    global_data[cat_order_col] = pd.Categorical(global_data[cat_order_col], cat_order)
    global_data = global_data.sort_values(
        by=[cat_order_col, "service"], axis=0
    ).reset_index(drop=True)

    totals = global_data.groupby([cat_order_col]).agg({"count": "sum"})
    global_data["percent"] = global_data.apply(
        lambda row: (row["count"] / totals.loc[row[cat_order_col], "count"]) * 100,
        axis=1,
    )
    global_data["growth"] = (
        (global_data["count"] / global_data["count"].shift(2)) - 1
    ) * 100
    global_data["growth"] = global_data["growth"].fillna(0).round(2)
    global_data["percent"] = global_data["percent"].round(2)

    fig = px.bar(
        global_data,
        x=cat_order_col,
        y="count",
        text="growth",
        color="service",
        barmode="group",
        custom_data=["percent"],
    )

    fig.update_traces(texttemplate="%{customdata[0]:.2f}%", textposition="outside")
    fig.update_traces(
        hovertemplate=(
            "<i>Period:</i> %{x}"
            "<br>"
            "<i>Campaigns:</i> %{y:,.0f}"
            "<br>"
            "<i>Monthly Percent:</i>%{customdata[0]:.2f}%"
            "<br>"
            "<i>Service Growth:</i>%{text: .2f}%"
        )
    )

    fig.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="Number of Campaigns"),
        legend_title_text="Service",
    )

    x = dcc.Graph(id="cumulative_camp_service_chart", figure=fig)

    regional_data.columns = ["count"]
    regional_data = regional_data.reindex(
        regional_idx, fill_value=0
    )  # ensures shift by 12
    regional_data = regional_data.reset_index()
    regional_data[cat_order_col] = pd.Categorical(
        regional_data[cat_order_col], cat_order
    )
    regional_data["region"] = pd.Categorical(
        regional_data["region"],
        ["ANZ", "Europe", "Asia", "MENA", "Americas", "multi-region"],
    )
    regional_data = regional_data.sort_values(
        by=[cat_order_col, "region", "service"], axis=0
    ).reset_index(drop=True)

    totals = regional_data.groupby([cat_order_col, "region"]).agg({"count": "sum"})
    regional_data["percent"] = regional_data.apply(
        lambda row: (
            row["count"] / totals.loc[(row[cat_order_col], row["region"]), "count"]
        )
        * 100,
        axis=1,
    )
    regional_data["growth"] = (
        (regional_data["count"] / regional_data["count"].shift(12)) - 1
    ) * 100
    regional_data["growth"].replace(np.inf, 100, inplace=True)
    regional_data["growth"].replace(-np.inf, -100, inplace=True)
    regional_data["growth"] = regional_data["growth"].fillna(0).round(2)
    regional_data["percent"] = regional_data["percent"].fillna(0).round(2)

    fig2 = go.Figure()
    fig2.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=cat_order, title=""),
        yaxis=dict(title="Number of Campaigns"),
        legend_title_text="Service",
        barmode="stack",
    )

    combos = [
        (y, z)
        for y in ["High Touch", "Low Touch"]
        for z in ["ANZ", "Europe", "Asia", "MENA", "Americas", "multi-region"]
    ]
    colours = [
        "#636efa",
        "#ef553b",
        "#00cc96",
        "#ab63fa",
        "#ffa15a",
        "#19d3f3",
        "#636efa",
        "#ef553b",
        "#00cc96",
        "#ab63fa",
        "#ffa15a",
        "#19d3f3",
    ]

    for i, (service, region) in enumerate(combos):
        opac = 1 if service == "High Touch" else 0.5
        leg = True if region == "ANZ" else False
        temp = regional_data.loc[
            (regional_data["region"] == region) & (regional_data["service"] == service),
            :,
        ].copy()

        print("Growth for Period Campaigns By Service Level")
        print(temp["growth"])

        # Could not get customdata working with percent, shows on first month but none others
        fig2.add_trace(
            go.Bar(
                x=[temp[cat_order_col], temp["region"]],
                y=temp["count"],
                name=service,
                text=temp["percent"],
                marker_color=colours[i],
                opacity=opac,
                legendgroup=service,
                showlegend=leg,
                # this doesnt work for unknown reason
                customdata=temp["growth"],
                hovertemplate=(
                    "<i>Month:</i> %{x}"
                    "<br>"
                    "<i>Regional Campaigns:</i> %{y:,.0f}"
                    "<br>"
                    "<i>Regional Period Percent:</i>%{text: .2f}%"
                    "<br>"
                    "<i>Regional Service Growth:</i>%{customdata}%"
                ),
                texttemplate="%{text:.2s}%",
                textposition="outside",
            ),
        )

    y = dcc.Graph(id="cumulative_camp_region_service_chart_region", figure=fig2)

    ELEMENTS = [
        dcc.Tabs(
            children=[
                dbc.Tab(label="Global", children=[x]),
                dbc.Tab(label="Regional", children=[y]),
            ],
            style={"z-index": "1"},
        )
    ]
    return ELEMENTS


def high_touch_low_touch_revenue_chart(data):

    global_data = pd.DataFrame(
        data.groupby("has_managed_service").agg({"adjusted_budget": pd.Series.sum})
    ).reset_index()

    global_data.columns = ["service_level", "revenue"]
    global_data["Proportion"] = (
        global_data["revenue"] * 100 / sum(global_data["revenue"])
    )
    levels = {True: "High Touch", False: "Low Touch"}
    global_data.replace({"service_level": levels}, inplace=True)

    fig = px.bar(global_data, x="service_level", y="revenue", text="Proportion")
    fig.update_layout(
        xaxis=dict(
            categoryorder="array",
            categoryarray=["High Touch", "Low Touch"],
            title="",
        ),
        yaxis=dict(title="$AUD"),
        legend_title_text="Service Level",
    )
    fig.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig.update_traces(
        hovertemplate=(
            "<br><i>Revenue:</i> $%{y:,.0f} <br><i>Proportion: </i>%{text: .2f}%"
        )
    )

    x = dcc.Graph(id="managed_service_global_revenue_chart", figure=fig)

    region_data = pd.DataFrame(
        data.groupby(["has_managed_service", "region"]).agg(
            {"adjusted_budget": pd.Series.sum}
        )
    ).reset_index()
    region_data.columns = ["service_level", "region", "revenue"]
    region_data.replace({"service_level": levels}, inplace=True)
    global_data["total_revenue"] = global_data["revenue"]
    region_data = region_data.merge(
        global_data.loc[:, ["service_level", "total_revenue"]],
        left_on="service_level",
        right_on="service_level",
    )
    region_data["Proportion"] = (
        region_data["revenue"] * 100 / region_data["total_revenue"]
    )
    region_data["region"] = pd.Categorical(
        region_data["region"],
        ["ANZ", "Europe", "Asia", "MENA", "Americas", "multi-region"],
    )
    region_data = region_data.sort_values("region")

    fig2 = px.bar(
        region_data,
        x="service_level",
        y="revenue",
        color="region",
        text="Proportion",
        barmode="group",
    )
    fig2.update_layout(
        xaxis=dict(
            categoryorder="array",
            categoryarray=["High Touch", "Low Touch"],
            title="",
        ),
        yaxis=dict(title="$AUD"),
        legend_title_text="Region",
        barmode="group",
    )
    fig2.update_traces(texttemplate="%{text:.2s}%", textposition="outside")
    fig2.update_traces(
        hovertemplate=(
            "<i>Service Level:</i> %{x} <br><i>Revenue:</i> $%{y:,.0f}"
            " <br><i>Proportion:</i>%{text: .2f}%"
        )
    )

    y = dcc.Graph(id="managed_service_region_revenue_chart", figure=fig2)

    ELEMENTS = [
        dcc.Tabs(
            children=[
                dbc.Tab(label="Global", children=[x]),
                dbc.Tab(label="Regional", children=[y]),
            ],
            style={"z-index": "1"},
        ),
        dbc.Row(
            [
                html.P(
                    "High Touch campaigns refer to campaigns with 'campaign"
                    " management'. Low touch campaignd refer to campaigns run without"
                    " the campaign management add on. The total budget is recorded"
                    " revenue when the campaign is started.",
                    style={
                        "color": "red",
                        "font-weight": "300",
                        "font-style": "italic",
                        "font-size": "9px",
                        "padding": "10px",
                    },
                )
            ]
        ),
    ]
    return ELEMENTS


"""
--------------------------------------------------------------------------------
                        Pricing Info Charts
--------------------------------------------------------------------------------
"""


def pricing_boxplot(data, currency):
    data = data.loc[data["custom_price"] > 0]
    fig = px.box(data, x="original_token_value", y="custom_price", log_y=True)
    # fig.update_traces(boxpoints=False)
    fig.update_layout(
        xaxis=dict(title="Original Token Value"), yaxis=dict(title=currency)
    )
    x = dcc.Graph(id="pricing_boxplot_chart", figure=fig)

    data = data.loc[data["status"] == "selected"]
    fig2 = px.box(data, x="original_token_value", y="custom_price", log_y=True)
    # fig.update_traces(boxpoints=False)
    fig2.update_layout(
        xaxis=dict(title="Original Token Value"), yaxis=dict(title=currency)
    )
    y = dcc.Graph(id="pricing_selected_boxplot_chart", figure=fig2)

    ELEMENTS = [
        dcc.Tabs(
            children=[
                dbc.Tab(label="Applied", children=[x]),
                dbc.Tab(label="Selected", children=[y]),
            ],
            style={"z-index": "1"},
        )
    ]
    return ELEMENTS


def pricing_barchart(data, currency):
    data["token_value"] = np.where(
        data["current_token_value"] < 2,
        "1 Token",
        np.where(
            data["current_token_value"] < 3,
            "2 Tokens",
            np.where(
                data["current_token_value"] < 4,
                "3 Tokens",
                np.where(
                    data["current_token_value"] < 5,
                    "4 Tokens",
                    np.where(
                        data["current_token_value"] < 6,
                        "5 Tokens",
                        np.where(
                            data["current_token_value"] < 11,
                            "6-10 Tokens",
                            "11+ Tokens",
                        ),
                    ),
                ),
            ),
        ),
    )
    vals = data.loc[
        data["status"] == "selected", ["token_value", "has_managed_service"]
    ].value_counts()
    vals = vals.reset_index()

    vals.columns = ["token_value", "has_managed_service", "count"]
    vals["token_value"] = pd.Categorical(
        vals["token_value"],
        [
            "1 Token",
            "2 Tokens",
            "3 Tokens",
            "4 Tokens",
            "5 Tokens",
            "6-10 Tokens",
            "11+ Tokens",
        ],
    )
    levels = {True: "High Touch", False: "Low Touch"}
    vals.replace({"has_managed_service": levels}, inplace=True)
    vals = vals.sort_values("token_value")

    fig = px.bar(
        vals,
        x="token_value",
        y="count",
        color="has_managed_service",
        barmode="group",
    )
    fig.update_layout(
        xaxis=dict(title="Current Token Value"),
        yaxis=dict(title="Count"),
        legend_title_text="Service Level",
        barmode="group",
    )
    x = dcc.Graph(id="pricing_bar_chart", figure=fig)
    data
    return x

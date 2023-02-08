from dash.dependencies import Input, Output

# import basic libraries
# import App
from components.components import *

# import data functions
from data.functions import *
from data.overview import *

# import graphing functions
from graphs.graphs import *
from main import app


##### OVERVIEW #####
@app.callback(
    [
        Output("self_serve_vb", "children"),
        Output("ave_talent_per_campaign", "children"),
        Output("ave_deliverables_per_campaign", "children"),
        Output("ave_time_in_draft", "children"),
        Output("draft_times_chart", "children"),
        Output("deliverable_type_chart", "children"),
        Output("campaign_locations_map", "children"),
        Output("status_chart", "children"),
    ],
    [
        Input("overview_date_inputs", "start_date"),
        Input("overview_date_inputs", "end_date"),
        Input("overview_customer_type_dropdown", "value"),
    ],
)
def build_overview_charts(start_date, end_date, customer_type):
    data = fetch_deliverables_by_campaign(start_date, end_date, customer_type)
    draft_times = fetch_brief_times_by_campaign(start_date, end_date, customer_type)
    talent_data = fetch_talent_by_campaign(start_date, end_date, customer_type)
    deliverable_types = fetch_deliverable_types_by_campaign(
        start_date, end_date, customer_type
    )
    self_serve = fetch_self_serve_customers(start_date, end_date)
    campaigns = fetch_campaigns(start_date, end_date, customer_type)
    status_data = fetch_campaigns_status(start_date, end_date, customer_type)
    self_serve = value_box("🧑‍💻 ", "Self Serve Customers", self_serve["self_serve"][0])
    ave_talent = value_box(
        "😁 ",
        "Average Talent Used Per Campaign",
        round(talent_data["talent_count"].mean()),
    )
    ave_deliverables = value_box(
        "✉️ ",
        "Average Deliverables Per Campaign",
        round(data["deliverables_count"].mean()),
    )
    ave_time_in_draft = value_box(
        "⏰ ",
        "Average Days in Draft",
        round(draft_times["days_in_draft"].mean()),
    )
    return [
        self_serve,
        ave_talent,
        ave_deliverables,
        ave_time_in_draft,
        build_draft_times_chart(draft_times),
        build_content_type_chart(deliverable_types),
        campaigns_map(campaigns),
        build_campaign_status_chart(status_data),
    ]

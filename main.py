import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State  # noqa

from components.components import LOGIN_PAGE  # NAVBAR,FILTERS, BODY #

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "style.css"],
    suppress_callback_exceptions=True,
)

app.layout = html.Div(
    id="app_page",
    children=[dcc.Store(id="current_loggedin_email"), LOGIN_PAGE],
)

app.title = "Metrics Dashboard"

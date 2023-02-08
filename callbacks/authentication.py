from datetime import datetime as dt

# import basic libraries
import pandas as pd
from dash.dependencies import Input, Output, State

# import App
from components.components import *
from data.authentication import *

# import data functions
from data.functions import *
from main import app


# TODO: ISSUE current-email not found The string ids in the current layout are: [app_page, email_input, password_input, submit-val]
###Authentication####
@app.callback(
    [
        Output("app_page", "children"),
        Output("email_input", "value"),
        Output("password_input", "value"),
        Output("current_loggedin_email", "data"),
    ],
    [Input("submit-val", "n_clicks")],
    [State("email_input", "value"), State("password_input", "value")],
)
def login(n_clicks, email, password):
    print(n_clicks)
    success = [dcc.Store(id="current_loggedin_email"), NAVBAR, BODY]
    fail = [dcc.Store(id="current_loggedin_email"), FAILED_LOGIN_PAGE]
    current_email = pd.DataFrame([{"email": None}])

    # ensuring current date is always updated
    global current_fiscal

    if date.today().month < 7:
        current_fiscal = dt(date.today().year - 1, 7, 1)
    else:
        current_fiscal = dt(date.today().year, 7, 1)

    if n_clicks == 0:
        page = [
            [dcc.Store(id="current_loggedin_email"), LOGIN_PAGE],
            None,
            None,
        ]
    else:
        passcheck = check_password(email, password)
        if passcheck:
            current_email.loc[0, "email"] = email
            page = [success, None, None]
        else:
            page = [fail, email, password]

    return [*page, current_email.to_json(date_format="iso", orient="split")]

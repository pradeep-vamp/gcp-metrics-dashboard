"""
 pricing-insights.py

 @ticket:	https://vampdash.atlassian.net/browse/DAS-11271
 @date:		2022-05-11
 @auth:		Mark Brackenrig < mark@vamp.me >

 @desc:
 This lambda function is triggered via scheduling to collect margin insights
 and send out a newsletter weekly. This email looks at campaigns completed
 in the last week and reports on their profitability and spend.
"""
import logging
import os

import pandas as pd

# import urllib3
from createsend import Transactional
from sqlalchemy import create_engine

# import io
auth = {"api_key": os.getenv("CM_API_KEY")}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

pd.options.display.float_format = "${:,.2f}".format

SMART_EMAIL_ID = os.getenv("SMART_EMAIL_ID")

CAMPAIGNS_SQL = """
SELECT c.id, c.name, t.name as team_name, cur.code as currency, c.budget, c.desired_location, c.spent_coins + c.additional_coins AS spent_tokens,
c.total_coins as total_tokens, CASE WHEN has_managed_service = True THEN 'Yes' ELSE 'No' END as campaign_management,
CASE WHEN CEILING( c.budget/(ctv.token_value*100/c.cogs)) = c.total_coins THEN 'No' ELSE 'Yes' END as campaign_edit,
SUM(d.reward_value) as influencer_spend, 100-SUM(d.reward_value)*100/(c.budget * ((c.spent_coins + c.additional_coins)/c.total_coins )) as margin, round(c.budget * ((c.spent_coins + c.additional_coins)/c.total_coins )) - SUM(d.reward_value) as gross_profit
FROM campaigns as c
JOIN currencies as cur on cur.id = c.currency_id
JOIN campaign_token_values as ctv on ctv.campaign_id = c.id
JOIN teams t on t.id = c.team_id
JOIN briefs b on b.campaign_id = c.id
JOIN deliverables d on d.brief_id = b.id
WHERE
(ctv.social_platform_id IS NULL OR ctv.social_platform_id = 1)
AND d.deliverable_type_id in (SELECT id from deliverable_types where code not in ('product_distribution'))
AND
c.updated_at >=  DATE_TRUNC('week', CURRENT_DATE - INTERVAL '1 week')
AND campaign_status_id = (select id from campaign_statuses WHERE code = 'fulfilled')
AND t.name NOT IN ('Vamp Demo','JoTestProd','Vamp Demo Whitelabel','VampVision', 'Digital4ge', 'Yourcompany')
AND  (
          desired_age_ranges<>'100-999'
        	OR desired_age_ranges IS NULL
        )
GROUP BY 1,2,3,4,5,6,7,8,9,10
"""

# Change campaign edited to tokens edited.
# Change gross profit to gross profit on tokens spent.


def currency_symbol(currency):
    if currency in ["AUD", "USD", "SGD"]:
        symbol = "$"
    elif currency == "GBP":
        symbol = "£"
    elif currency == "EUR":
        symbol = "€"
    elif currency == "JPY":
        symbol = "¥"
    else:
        symbol = "$" + currency + " "
    return symbol


def set_connection_str():
    """Populate DB connection string"""
    host = os.getenv("HOST")
    password = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")
    user = os.getenv("DBUSER")
    port = os.getenv("PORT", "5432")
    result = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
        user=user, password=password, host=host, port=port, database=database
    )

    return result


def fetch_campaign_data():
    """Fetch the deliverables above 5 tokens insights"""
    connect_str = set_connection_str()
    print(connect_str)
    engine = create_engine(connect_str)
    return pd.io.sql.read_sql(CAMPAIGNS_SQL, engine)


def create_email(event, context):
    """
    Create the pricing insight newsletter email. This function is the entry point
    for the AWS lambda, it querys the DB for the insights, formats the HTML email
    and finally sends it off. This lambda should be triggered by a cron job at
    the beginiing of every month for the previous month

    event : aws lambda default arg
            Not used by the function

    context : aws lambda default arg
            Not used by the function
    """
    RECIPIENTS = os.getenv("EMAIL_LIST").split(",")

    campaign_data = fetch_campaign_data()
    campaign_data["currency_symbol"] = campaign_data["currency"].apply(currency_symbol)
    campaign_data["margin"] = campaign_data["margin"].map("{:,.2f}".format)
    campaign_data["gross_profit"] = campaign_data["gross_profit"].map("{:,.2f}".format)
    print(campaign_data.to_dict(orient="records")[0])
    # try:
    tx_mailer = Transactional(auth)
    my_data = {"campaigns": campaign_data.to_dict(orient="records")}
    response = tx_mailer.smart_email_send(
        SMART_EMAIL_ID, RECIPIENTS, "no", data=my_data
    )
    # except Exception as e:
    # 	e
    # 	logger.error(e.response['Error']['Message'])
    # else:
    # 	logger.info(f"Email sent! Message ID: {response['MessageId']}")


if __name__ == "__main__":
    """For testing purposes"""
    create_email(None, None)

# Functions
import json
import os
from datetime import datetime as date

import boto3
import pandas as pd
from botocore.exceptions import ClientError  # used to find NoSuchKey error
from dash.exceptions import PreventUpdate
from google.cloud import bigquery
from psycopg2 import connect, sql

from data.fixer import Fixerio

host = os.getenv("HOST")
database = os.getenv("DATABASE")
req_user = os.getenv("DBUSER")
password = os.getenv("PASSWORD")
sslmode = os.getenv("SSLMODE")
debugmode = os.getenv("DEBUGMODE")
fixer_api_key = os.getenv("FIXER_API_KEY")
aws_key = os.getenv("AWS_ACCESS_KEY")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
bucket = os.getenv("DEFAULT_S3_BUCKET")

WHITELIST_EMAILS = os.getenv("WHITELIST_EMAILS").split(",")

credentials = os.getenv("GOOGLE_CREDENTIALS_RAW")

with open("/tmp/vamp-google-credentials.json", "w") as outfile:
    outfile.write(credentials)


def fetch_from_bigquery(query_string):

    bqclient = bigquery.Client()

    dataframe = (
        bqclient.query(query_string)
        .result()
        .to_dataframe(
            create_bqstorage_client=True,
        )
    )
    return dataframe


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def fetch_from_postgres(
    query,
    host=host,
    database=database,
    req_user=req_user,
    password=password,
    sslmode=sslmode,
):
    conn = connect(
        host=host,
        database=database,
        user=req_user,
        password=password,
        sslmode=sslmode,
    )
    cur = conn.cursor()
    cur.execute(query)
    column_names = [desc[0] for desc in cur.description]
    try:
        # create a cursor
        temp = cur.fetchall()
        temp = pd.DataFrame(temp)
        temp.columns = column_names
    except:
        temp = pd.DataFrame(columns=column_names)
    finally:
        conn.close()
    return temp


def fetch_from_s3(key, aws_key=aws_key, aws_secret=aws_secret, bucket=bucket):
    client = boto3.client(
        "s3", aws_access_key_id=aws_key, aws_secret_access_key=aws_secret
    )
    try:
        csv_object = client.get_object(Bucket=bucket, Key=key)
        body = csv_object["Body"]
        df = pd.read_csv(body)
    except Exception as e:
        print(e)
        df = pd.DataFrame()
    return df


def post_to_s3(key, df, aws_key=aws_key, aws_secret=aws_secret, bucket=bucket):

    client = boto3.client(
        "s3", aws_access_key_id=aws_key, aws_secret_access_key=aws_secret
    )

    df.to_csv("/tmp/temp_csv.csv", index=False)
    client.upload_file("/tmp/temp_csv.csv", bucket, key)

    return "Yes"


def restrict_resource(current_email=pd.DataFrame(), safe_emails=[]):

    current_email = pd.read_json(current_email, orient="split")

    if len(current_email) == 0:
        raise PreventUpdate

    if current_email.loc[0, "email"] not in [*WHITELIST_EMAILS, *safe_emails]:
        raise PreventUpdate


def record_influencer_action(
    employee_email,
    influencer_id,
    action="suspended_influencer",
    reason="",
    notes="",
):
    aw_host = os.getenv("AWH_HOST")
    aw_database = os.getenv("AWH_DATABASE")
    aw_req_user = os.getenv("AWH_DBUSER")
    aw_password = os.getenv("AWH_PASSWORD")
    aw_sslmode = os.getenv("AWH_SSLMODE")

    conn = connect(
        host=aw_host,
        database=aw_database,
        user=aw_req_user,
        password=aw_password,
        sslmode=aw_sslmode,
    )
    cur = conn.cursor()
    query = sql.SQL(
        """
        INSERT INTO warehouse.vamp_influencer_interactions (user_id, influencer_id, action, reason, notes)
            SELECT users.id AS user_id
                , {influencer_id} AS influencer_id
                , '{action}' AS action
                , '{reason}' AS reason
                , '{notes}' AS notes
            FROM raw.users
            inner join raw.memberships on users.id = memberships.user_id
            inner join raw.teams on teams.id = memberships.team_id
            WHERE email = '{email}'
                AND teams.type = 'vamp'
            LIMIT 1;
    """.format(
            email=employee_email,
            influencer_id=influencer_id,
            action=action,
            reason=reason,
            notes=notes,
        )
    )

    try:
        print(query)
        cur.execute(query)
        conn.commit()
    except:
        print("Unable to save interaction")
    finally:
        conn.close()


def suspend_influencer_servalan(
    handle="",
    reason="unknown",
    notes="",
    current_email=pd.DataFrame(),
    aws_key=aws_key,
    aws_secret=aws_secret,
):
    # Add current email to DB
    client = boto3.client(
        "s3", aws_access_key_id=aws_key, aws_secret_access_key=aws_secret
    )
    query = sql.SQL(
        "SELECT DISTINCT influencer_id FROM social_accounts WHERE handle = {handle}"
    ).format(handle=sql.Literal(handle))
    res = fetch_from_postgres(query)

    print(reason, notes)

    if len(res) != 1:
        return f"Error, cannot locate influencer from handle: {handle}"
    else:
        influencer_id = res["influencer_id"][0]
        mutation = (
            "mutation {updateInfluencerStatus(id:"
            + str(influencer_id)
            + ', status:"suspended"){id}}'
        )
        analytics_bucket = os.getenv("ANALYTICS_BUCKET")

        try:
            client.put_object(
                Body=mutation,
                Key="auto-reject/Servalan/" + str(influencer_id) + ".txt",
                Bucket=analytics_bucket,
            )
        except Exception as e:
            print(e)
            return f"Error, an issue occured while trying to suspended {handle}"

        # Send log to AW DB with user suspension
        current_email = pd.read_json(current_email, orient="split")
        record_influencer_action(
            employee_email=current_email.loc[0, "email"],
            influencer_id=influencer_id,
            action="suspended_influencer",
            reason=reason,
            notes=notes,
        )

        return f"Success! influencer {handle}: {str(influencer_id)} has been suspended"

    return f"Error, unknown issue happen while trying to suspended {handle}"


def get_file_list(bucket, prefix):
    """
    Get a dictionary of all the files with lastmodified date from within an S3
    subdirectory

    bucket : str
        The AWS S3 bucket

    prefix : str
        The folder directory within the bucket

    return : dict
        A dictionary of filenames as keys and last modifed date as values
    """
    try:
        client = boto3.client(
            "s3", aws_access_key_id=aws_key, aws_secret_access_key=aws_secret
        )
        paginator = client.get_paginator("list_objects")
        operation_parameters = {"Bucket": bucket, "Prefix": prefix}
        page_iterator = paginator.paginate(**operation_parameters)
        return {
            _["Key"].replace(prefix, ""): _["LastModified"]
            for page in page_iterator
            for _ in page["Contents"]
            if _["Key"] != prefix
        }
    except Exception as e:
        print("Could not retrieve from s3")
        print(e)

    return {}


def log_interaction_s3(dict_msg, aws_key=aws_key, aws_secret=aws_secret, bucket=bucket):
    """
    Creates or updates a log file in s3, specific to an email address. This log
    file stores any interaction made by the logged in user with the fraud
    detection page (pandabot)

    dict_msg : dict
        The only expected field is `email` other than that the message can have
        any structure but I've been using the following keys:
            email: logged in users email
            interaction: some relevant tag to identify the type of interaction
            data: anything you want, ive been putting the data that was altered

    aws_key : str AWS IAM keys
    aws_secret : str AWS IAM keys
    bucket : str AWS S3 bucket
    """
    key = (
        f"metrics-dashboard/logs/{dict_msg.get('email', 'email_key_not_found@vamp.me')}.csv"
    )

    # try to grab logs currently
    try:
        user_logs = fetch_from_s3(
            key=key, aws_key=aws_key, aws_secret=aws_secret, bucket=bucket
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            user_logs = pd.DataFrame()
        else:
            raise

    # append message to body as: [LOGGED] datetime | json_log_message
    logged_at = date.now().strftime("%Y-%m-%dT%H:%M:%S")
    dict_msg["date"] = logged_at
    user_logs = user_logs.append(dict_msg, ignore_index=True)

    print(user_logs)
    col_order = ["date", "email"]
    additional_cols = [col for col in user_logs.columns if col not in col_order]
    user_logs = user_logs.reindex(columns=[*col_order, *additional_cols])
    # upload
    post_to_s3(key, user_logs, aws_key=aws_key, aws_secret=aws_secret, bucket=bucket)


def fetch_active_countries():
    query = """
        SELECT
            id,
            name
        FROM
            countries
        WHERE
            active = TRUE """
    data = fetch_from_postgres(query)
    return data


def fetch_active_categories():
    query = """
        SELECT
            code,
            name
        FROM
            categories
        WHERE
            internal = FALSE """
    data = fetch_from_postgres(query)
    return data


def fetch_countries():
    query = """
        SELECT
            id,
            name,
            code,
            sub_region,
            region
        FROM
            countries """
    data = fetch_from_postgres(query)
    return data


def fetch_self_serve_customers_limited():
    query = """
        SELECT
            id,
            name
        FROM
            teams
        WHERE
            type IN (
                'vamp',
                'selfserve',
                'portal') """
    data = fetch_from_postgres(query)
    return data


self_serve_customers = fetch_self_serve_customers_limited()

try:
    fx = Fixerio(access_key=fixer_api_key)
    currency_conversions = fx.latest()
    print(currency_conversions["success"])
    if currency_conversions["success"] == False:
        raise Exception("Error - Fixer API call failed. reverting to previous rates.")
    with open("/tmp/currency_conversions.json", "w") as writer:
        writer.write(json.dumps(currency_conversions))
except:
    try:
        with open("/tmp/currency_conversions.json") as f:
            currency_conversions = json.load(f)
        if currency_conversions["success"] == False:
            raise Exception(
                "Error - saved rates are incorrect. reverting to static rates."
            )
    except:
        currency_conversions = {
            "rates": {
                "USD": 1,
                "AUD": 1.33,
                "GBP": 0.72,
                "EUR": 0.84,
                "JPY": 110.73,
                "SGD": 1.34,
                "IDR": 14448.15,
            }
        }

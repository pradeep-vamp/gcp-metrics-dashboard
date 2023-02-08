import re

import bcrypt
from psycopg2 import sql

from data.functions import fetch_from_postgres


def fetch_password(email):
    query = sql.SQL(
        """
            SELECT
                encrypted_password
            FROM
                users
                INNER JOIN memberships ON
                    users.id = memberships.user_id
                INNER JOIN teams on
                    teams.id = memberships.team_id
            WHERE
                email = {email}
                AND teams.type = 'vamp'
            LIMIT 1; """
    ).format(email=sql.Literal(email))
    data = fetch_from_postgres(query)
    return data


def check_password(email, password):
    # first check that the email is a vamp email
    if re.search("@vamp.me", email):
        hashedpw = str.encode(fetch_password(email)["encrypted_password"][0])
        result = bcrypt.checkpw(str.encode(password), hashedpw)
    else:
        result = False
    return result

from clickhouse_driver import Client
import requests
import os

PROM_USER = os.environ['PROM_USER']
PROM_PASS = os.environ['PROM_PASS']
API_KEY = os.environ['API_KEY']


# This is for not having to create the authentication every time you fetch
# So you pass the created session around instead
def session_create(data: dict) -> requests.Session:
    session = requests.Session()

    auth = data.get('auth')
    if (auth):
        session.auth = (auth.get('user'), auth.get('pass'))

    headers = data.get('headers')
    if (headers):
        session.headers.update(headers)

    return (session)


# clickhouse
def clickhouse_client_init() -> Client:
    return (Client(
            host=os.environ['CH_HOST'],
            port=os.environ['CH_PORT'],
            user=os.environ['CH_USER'],
            password=os.environ['CH_PASSWORD'],
            database=os.environ['CH_DATABASE'])
    )

from clickhouse_driver import Client
import requests
import os

BLOB_SIDECAR_TABLE = 'beacon_api_eth_v1_events_blob_sidecar'
BLOCK_TABLE = 'beacon_api_eth_v2_beacon_block'
BLOCK_CANON_TABLE = 'canonical_beacon_block'
TXS_TABLE = 'mempool_transaction'


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

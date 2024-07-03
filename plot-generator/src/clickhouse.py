from clickhouse_driver import Client
import os

BLOB_SIDECAR_TABLE = 'beacon_api_eth_v1_events_blob_sidecar'
BLOCK_TABLE = 'beacon_api_eth_v2_beacon_block'
BLOCK_CANON_TABLE = 'canonical_beacon_block'
TXS_TABLE = 'mempool_transaction'


def clickhouse_client_init() -> Client:
    return (Client(
            host=os.environ['CH_HOST'],
            port=os.environ['CH_PORT'],
            user=os.environ['CH_USER'],
            password=os.environ['CH_PASSWORD'],
            database=os.environ['CH_DATABASE'])
    )

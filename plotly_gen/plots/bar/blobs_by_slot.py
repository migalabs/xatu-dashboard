from plots.bar.bar import bar_create_fig
from creates import df_clickhouse_create
from utils import bold
import pandas as pd
import numpy as np


# todo make this into env variable
BLOB_SIDECAR_TABLE = 'default.beacon_api_eth_v1_events_blob_sidecar'


def blobs_per_slot_create(client):
    plotname = 'blobs-by-slot'
    limit = 30

    query = f'''
                select slot, count(distinct blob_index) as blob_count
                from {BLOB_SIDECAR_TABLE}
                where meta_network_name = 'mainnet'
                group by slot
                order by slot desc
                limit {limit}
            '''

    df = df_clickhouse_create(client, query, 'Blobs per slot')

    # The following is mainly for just adding all missing slots as new rows
    # with 0 as their blob count
    # df.iloc[:] = df.iloc[::-1].values
    df.set_index('slot', inplace=True)
    full_index = pd.Index(np.arange(df.index.min(), df.index.max() + 1), name='slot')
    df = df.reindex(full_index, fill_value=0)
    df.reset_index(inplace=True)
    df = df.tail(limit)

    fig = bar_create_fig(
        df,
        x='slot', y='blob_count',
        title='Blob count per slot',
        color_discrete_sequence='#d9f45d', thickness=0.3,
        hovertemplate=f'{bold("slot")}: %{{x:,}}<br>{bold("blobs")}: %{{y:,}}',
        ytitle='Blob count', xtitle='Slot',
        xskips=5, yskips=1
    )

    fig.update_traces(marker_line_color='#d9f45d', marker_line_width=10)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

from os import times
from plots.area.area import area_fig_create, area_customize, fraction_clamp
from utils import date_since, to_unix_date_tuple
from creates import df_clickhouse_create
from utils import bold
from typing import List
import pandas as pd
import numpy as np

# todo make this into env variable
BLOB_SIDECAR_TABLE = 'default.beacon_api_eth_v1_events_blob_sidecar'


def ticktext_labels_truncate(skips, column) -> List[str]:
    ticktext = []
    for a, val in enumerate(column):
        if (a % skips) == 0:
            ticktext.append(str(val)[:10] + '...')
    return (ticktext)


def blob_hash_repetitions_create(client):
    plotname = 'blob-hash-repetitions'
    title = 'Blob hash repetitions'
    start_time = date_since(days=1)
    limit = 100
    # dates = to_unix_date_tuple(start_time, end_time)

    query = f'''
                select
                    versioned_hash,
                    count(*) as repeat_times
                from {BLOB_SIDECAR_TABLE}
                where meta_network_name = 'mainnet'
                group by versioned_hash
                order by repeat_times desc
                limit {limit}
            '''

    df = df_clickhouse_create(client, query, title)
    df['full_hashes'] = df['versioned_hash']

    fig = area_fig_create(
        df, x='versioned_hash', y='repeat_times', name='versioned_hash',
        color_discrete_map=None, markers=True, customdata='full_hashes',
        color_lines='rgb(255, 181, 120)'
    )

    hovertemplate = f'{bold("Repetitions")}: %{{y}}<br>{bold("Hash")}: %{{customdata[0]}}<extra></extra>'

    tickvals = df['versioned_hash'].tolist()
    xskips = 10

    area_customize(
        fig, df, title=title,
        xtitle='Hash', ytitle='Repetitions', hovertemplate=hovertemplate,
        legend=False, percent=False, markers=True, start_time=start_time,
        inv=False, filling=True, name='repeat_times', rate='L0.5',
        yskips=fraction_clamp(df['repeat_times'].max() / 5),
        tickvals=[i for i in range(0, len(df), xskips)],
        xrange=None, xticktext=ticktext_labels_truncate(xskips, df['versioned_hash'])
    )

    fig.update_layout(xaxis_tickangle=45)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

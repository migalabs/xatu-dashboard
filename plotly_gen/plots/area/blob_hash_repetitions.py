from plots.area.area import area_create_fig, area_customize, fraction_clamp
from creates import df_clickhouse_create
from utils import date_since
from typing import List
from sessions import BLOB_SIDECAR_TABLE
from utils import bold, title_format


def ticktext_labels_truncate(skips, column) -> List[str]:
    ticktext = []
    for a, val in enumerate(column):
        if (a % skips) == 0:
            ticktext.append(str(val)[:10] + '...')
    return (ticktext)


def blob_hash_repetitions_create(client):
    plotname = 'area_blob-hash-repetitions'
    title = 'Blob hash repetitions'
    start_time = date_since(days=1)
    limit = 150

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

    fig = area_create_fig(
        df, x='versioned_hash', y='repeat_times', name='versioned_hash',
        color_discrete_map=None, markers=False, customdata='full_hashes',
        color_lines='rgb(255, 181, 120)', log_y=True
    )

    hovertemplate = f'{bold("Repetitions")}: %{{y}}<br>{bold("Hash")}: %{{customdata[0]}}<extra></extra>'

    xskips = 10

    area_customize(
        fig, df, title=title,
        xtitle='Hash', ytitle='Repetitions', hovertemplate=hovertemplate,
        legend=False, percent=False, markers=False, start_time=start_time,
        inv=False, filling=True, name='repeat_times', rate='L0.5',
        yskips=fraction_clamp(df['repeat_times'].max() / 5),
        tickvals=[i for i in range(0, len(df), xskips)], xrange=None,
        xticktext=ticktext_labels_truncate(xskips, df['versioned_hash']),
        title_annotation=f'{limit} hashes (all time)'
    )

    fig.update_layout(xaxis_tickangle=45)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

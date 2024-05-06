from plots.bar.bar import bar_create_fig
from creates import df_clickhouse_create
from utils import bold
import pandas as pd
import numpy as np


# todo make this into env variable
BLOB_SIDECAR_TABLE = 'default.beacon_api_eth_v1_events_blob_sidecar'


def first_last_difference_create(client):
    plotname = 'first-last-timediff'
    title = 'Time difference between first and last blob'
    slot_limit = 30

    query = f'''
                select
                    slot,
                    min(propagation_slot_start_diff) min_delay_ms,
                    max(propagation_slot_start_diff) max_delay_ms
                from {BLOB_SIDECAR_TABLE}
                where meta_network_name = 'mainnet'
                group by slot
                having count(distinct blob_index) >= 2
                order by slot desc
                limit {slot_limit}
            '''

    df = df_clickhouse_create(
        client, query, title
    )

    df['time_diff_ms'] = df['max_delay_ms'] - df['min_delay_ms']

    fig = bar_create_fig(
        df,
        x='slot', y='time_diff_ms',
        title=title,
        color_discrete_sequence='#d5c3fc', thickness=0.5,
        hovertemplate=f'{bold("time difference")}: %{{y:.0f}}ms<br>{bold("slot")}: %{{x:,}}',
        ytitle='Time difference', xtitle='Slots',
        xskips=20, yskips=(df['time_diff_ms'].max() / 5),
        title_annotation=f' Latest {(225 * slot_limit)} epochs ({slot_limit} days)'
    )

    tickvals = fig['layout']['yaxis']['tickvals']

    fig.update_yaxes(
        tickvals=tickvals,
        ticktext=[f"<b>{'{:.0f}ms'.format(x)}     </b>" for x in tickvals]
    )
    fig.update_traces(marker_line_color='#d5c3fc', marker_line_width=5)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

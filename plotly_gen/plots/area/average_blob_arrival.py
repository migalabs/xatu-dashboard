from plots.area.area import area_create_fig, area_customize, fraction_clamp, end_time
from creates import df_clickhouse_create
from utils import date_since, bold, get_epoch_readable_unit
from sessions import BLOB_SIDECAR_TABLE
from units import format_seconds
import pandas as pd
import numpy as np


def average_blob_arrival_create(client):
    plotname = 'area_avg-blob-arrival'
    title = 'Average blob arrival time'
    start_time = date_since(days=1)
    day_limit = 30

    query = f'''
                select
                    toDate(slot_start_date_time) AS day,
                    AVG(propagation_slot_start_diff) AS avg_delay_ms
                from (
                    select *,
                           ROW_NUMBER() OVER (PARTITION BY block_root, versioned_hash, blob_index, slot ORDER BY slot_start_date_time ASC) AS rn
                    from {BLOB_SIDECAR_TABLE}
                    where meta_network_name = 'mainnet'
                    and propagation_slot_start_diff < 100000
                )
                where rn = 1
                group BY day
                order BY day desc
                limit {day_limit}
            '''

    df = df_clickhouse_create(client, query, title)

    df['avg_delay_s'] = df['avg_delay_ms'] / 1000

    fig = area_create_fig(
        df, x='day', y='avg_delay_s', name='day',
        color_discrete_map=None, markers=True, customdata='avg_delay_s',
        color_lines='rgb(125, 149, 255)'
    )

    hovertemplate = f'{bold("Average delay")}: %{{customdata[0]:,.2f}}s<br>{bold("Date")}: %{{x}}<extra></extra>'

    epochs = (day_limit * 225)
    readable_timeframe = get_epoch_readable_unit(epochs)

    area_customize(
        fig, df, title=title, xtitle='', ytitle='Delay',
        hovertemplate=hovertemplate, legend=False, percent=False, markers=True,
        start_time=start_time, inv=False, filling=True, name='avg_delay_s',
        rate='604800000', tick_text_formatter=format_seconds,
        yskips=fraction_clamp(df['avg_delay_s'].max() / 5, 10),
        xrange=[df['day'].min(), df['day'].max()],
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})'
    )

    fig.update_layout(xaxis_tickangle=45)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

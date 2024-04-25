from plots.area.area import area_fig_create, area_customize, fraction_clamp, end_time
from utils import date_since, to_unix_date_tuple
from creates import df_clickhouse_create
from utils import bold
import pandas as pd
import numpy as np

# todo make this into env variable
BLOB_SIDECAR_TABLE = 'default.beacon_api_eth_v1_events_blob_sidecar'


def average_blob_arrival_create(client):
    plotname = 'avg-blob-arrival'
    title = 'Average blob arrival time'
    limit = 100
    start_time = date_since(days=1)
    dates = to_unix_date_tuple(start_time, end_time)

    query = f'''
                select
                    toDate(slot_start_date_time) as day,
                    avg(propagation_slot_start_diff) as avg_delay_ms
                from {BLOB_SIDECAR_TABLE}
                group by toDate(slot_start_date_time)
                order by day desc
            '''

    df = df_clickhouse_create(client, query, title)

    fig = area_fig_create(
        df, x='day', y='avg_delay_ms', name='day',
        color_discrete_map=None, markers=True, customdata=None,
        color_lines='rgb(125, 149, 255)'
    )

    hovertemplate = f'{bold("Average delay")}: %{{y:,.0f}}ms<br>{bold("Date")}: %{{x}}<extra></extra>'
    area_customize(
        fig, df, title=title, xtitle='', ytitle='Delay',
        hovertemplate=hovertemplate, legend=False, percent=False, markers=True,
        start_time=start_time, inv=False, filling=True, name='avg_delay_ms',
        rate='432000000', tick_text_formatter=lambda x: f'{bold(f"{x:,.0f}ms")}',
        yskips=fraction_clamp(df['avg_delay_ms'].max() / 5),
        xrange=[df['day'].min(), df['day'].max()]
    )

    fig.update_layout(xaxis_tickangle=45)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

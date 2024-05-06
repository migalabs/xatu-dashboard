from plots.area.area import area_create_fig, area_customize, fraction_clamp, end_time
from utils import date_since, to_unix_date_tuple, title_format
from creates import df_clickhouse_create
from utils import bold
import pandas as pd
import numpy as np

# todo make this into env variable
BLOB_SIDECAR_TABLE = 'default.beacon_api_eth_v1_events_blob_sidecar'


def average_blob_arrival_create(client):
    plotname = 'avg-blob-arrival'
    title = 'Average blob arrival time'
    start_time = date_since(days=1)
    day_limit = 25

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

    print(df)

    df['avg_delay_s'] = df['avg_delay_ms'] / 1000

    fig = area_create_fig(
        df, x='day', y='avg_delay_s', name='day',
        color_discrete_map=None, markers=True, customdata='avg_delay_s',
        color_lines='rgb(125, 149, 255)'
    )

    hovertemplate = f'{bold("Average delay")}: %{{customdata[0]:,.2f}}s<br>{bold("Date")}: %{{x}}<extra></extra>'

    area_customize(
        fig, df, title=title, xtitle='', ytitle='Delay',
        hovertemplate=hovertemplate, legend=False, percent=False, markers=True,
        start_time=start_time, inv=False, filling=True, name='avg_delay_s',
        rate='432000000', tick_text_formatter=lambda x: f'{bold(f"{x/10:,.0f}ms")}' if (x < 1) else f'{bold(f"{(x):,.0f}s")}',
        yskips=fraction_clamp(df['avg_delay_s'].max() / 5, 10),
        xrange=[df['day'].min(), df['day'].max()], title_annotation=f' Latest {(225 * day_limit)} epochs ({day_limit} days)'
    )

    fig.update_layout(xaxis_tickangle=45)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

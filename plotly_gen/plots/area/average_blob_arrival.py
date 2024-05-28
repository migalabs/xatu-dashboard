from plots.area.area import (
    area_create_fig, area_customize, fraction_clamp,
    DEFAULT_DATE_FORMAT, FIVE_DAYS_RATE)
from utils import date_since, bold, get_epoch_readable_unit
from creates import df_clickhouse_create
from sessions import BLOB_SIDECAR_TABLE
from units import format_seconds


def average_blob_arrival_create(client):
    plotname = 'area_avg-blob-arrival'
    title = 'Average blob arrival time'
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

    x, y = 'day', 'avg_delay_s'
    fig = area_create_fig(
        df, x=x, y=y, name=x,
        color_discrete_map=None, markers=True, customdata=y,
        color_lines='rgb(125, 149, 255)'
    )

    hovertemplate = (
        f'{bold("Average delay")}: %{{y:,.2f}}s<br>'
        f'{bold("Date")}: %{{x}}<extra></extra>'
    )

    epochs = (day_limit * 225)
    readable_timeframe = get_epoch_readable_unit(epochs)
    area_customize(
        df, fig, title=title,
        x_col_title=(x, ''),
        y_col_title=(y, 'Delay'),
        yrange=[0, df[y].max() + 0.2],
        hovertemplate=hovertemplate,
        yskips=1, xskips=FIVE_DAYS_RATE,
        xtickformat=DEFAULT_DATE_FORMAT,
        ytickformat=format_seconds,
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})'
    )
    fig.update_layout(xaxis_tickangle=45)
    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

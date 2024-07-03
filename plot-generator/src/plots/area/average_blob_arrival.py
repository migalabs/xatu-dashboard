from plots.area.area import (
    area_create_fig, area_customize)
from axis_tools import DEFAULT_DATE_FORMAT, FIVE_DAYS_RATE
from utils import bold, get_epoch_readable_unit
from df_manip import df_clickhouse_create
from clickhouse import BLOB_SIDECAR_TABLE
from units import format_seconds


def average_blob_arrival_create(client):
    plotname = 'area_avg-blob-arrival'
    title = 'Average blob arrival time'
    day_limit = 30

    query = f'''
                SELECT
                    toDate(slot_start_date_time) AS day,
                    AVG(propagation_slot_start_diff) AS avg_delay_ms
                FROM (
                    SELECT *,
                            ROW_NUMBER() OVER (
                                PARTITION BY
                                    block_root, versioned_hash, blob_index, slot
                                ORDER BY
                                    slot_start_date_time ASC
                            ) AS rn
                    FROM {BLOB_SIDECAR_TABLE}
                    WHERE meta_network_name = 'mainnet'
                    and propagation_slot_start_diff < 100000
                )
                WHERE rn = 1
                GROUP BY day
                ORDER BY day DESC
                LIMIT {day_limit}
            '''

    df = df_clickhouse_create(client, query, title)

    # Convert delay to seconds
    df['avg_delay_s'] = df['avg_delay_ms'] / 1000

    hovertemplate = (
        f'{bold("Average delay")}: %{{y:,.2f}}s<br>'
        f'{bold("Date")}: %{{x}}<extra></extra>'
    )
    epochs = (day_limit * 225)
    readable_timeframe = get_epoch_readable_unit(epochs)
    x, y = 'day', 'avg_delay_s'

    fig = area_create_fig(
        df, x=x, y=y, color=x,
        color_discrete_map=None, markers=True, customdata=y,
        line_color='rgb(125, 149, 255)'
    )
    area_customize(
        df, fig, title=title,
        x_axis_info=(x, ''),
        y_axis_info=(y, 'Delay'),
        yrange=[0, df[y].max() + 0.2],
        hovertemplate=hovertemplate,
        yskips=1, xskips=FIVE_DAYS_RATE,
        xtickformat=DEFAULT_DATE_FORMAT,
        ytickformat=format_seconds,
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})'
    )
    # Tilt ticks slightly
    fig.update_layout(xaxis_tickangle=45)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

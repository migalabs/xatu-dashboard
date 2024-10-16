from utils import bold, get_epoch_readable_unit
from df_manip import df_clickhouse_create
from plots.box.box import box_create_fig
from clickhouse import BLOB_SIDECAR_TABLE
from units import format_seconds

color_map = {
    2: '#c4fffd',
    3: '#a6d1ff',
    4: '#b6a9ff',
    5: '#edb5ff',
    6: '#ffb8d3'
}


def first_last_difference_create(client):
    plotname = 'box_first-last-timediff'
    title = 'Time difference between first and last blob'
    slot_limit = 216000

    query = f'''
                SELECT
                    slot,
                    COUNT(distinct blob_index) AS blob_count,
                    MIN(propagation_slot_start_diff)/1000 min,
                    MAX(propagation_slot_start_diff)/1000 max,
                    AVG(propagation_slot_start_diff)/1000 AS avg
                FROM (
                    SELECT *,
                            ROW_NUMBER() over (
                                partition BY
                                    block_root, versioned_hash, blob_index, slot
                                ORDER BY
                                    slot_start_date_time asc
                            ) AS rn
                    FROM {BLOB_SIDECAR_TABLE}
                    WHERE meta_network_name = 'mainnet'
                    AND propagation_slot_start_diff < 100000
                )
                WHERE rn = 1
                GROUP BY slot
                HAVING count(distinct blob_index) >= 2
                ORDER BY slot DESC
                LIMIT {slot_limit}
            '''

    df = df_clickhouse_create(client, query, title)
    df['time_diff_s'] = df['max'] - df['min']

    hovertemplate = (
        f'{bold("Time difference")}: %{{y:,.1f}}s<br>'
        f'{bold("Number of blobs")}: %{{x:,.0f}}<extra></extra>'
    )
    epochs = (slot_limit / 32)
    readable_timeframe = get_epoch_readable_unit(epochs)
    x, y = 'blob_count', 'time_diff_s'

    fig = box_create_fig(
        df,
        x_axis_info=(x, 'Blob count'),
        y_axis_info=(y, 'Time difference'),
        color=x,
        title=title, points='outliers', quartilemethod='exclusive',
        color_discrete_map=color_map, thickness=0.5,
        hovertemplate=hovertemplate, notched=True,
        xskips=1, yskips=2,
        title_annotation=f'Last {epochs:,.0f} epochs ({readable_timeframe})',
        ytickformat=format_seconds, xtickformat=','
    )

    fig.update_yaxes(range=[0, 12])

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

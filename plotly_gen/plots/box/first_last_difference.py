from utils import bold, get_epoch_readable_unit
from creates import df_clickhouse_create
from plots.box.box import box_create_fig
from sessions import BLOB_SIDECAR_TABLE
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
                select
                    slot,
                    count(distinct blob_index) as blob_count,
                    min(propagation_slot_start_diff)/1000 min,
                    max(propagation_slot_start_diff)/1000 max,
                    AVG(propagation_slot_start_diff)/1000 AS avg
                from (
                    select *,
                           ROW_NUMBER() over (partition by block_root, versioned_hash, blob_index, slot ORDER by slot_start_date_time asc) as rn
                    from {BLOB_SIDECAR_TABLE}
                    where meta_network_name = 'mainnet'
                    and propagation_slot_start_diff < 100000
                )
                where rn = 1
                group by slot
                having count(distinct blob_index) >= 2
                order by slot desc
                limit {slot_limit}
            '''

    df = df_clickhouse_create(client, query, title)
    df['time_diff_s'] = df['max'] - df['min']

    epochs = (slot_limit / 32)
    readable_timeframe = get_epoch_readable_unit(epochs)

    fig = box_create_fig(
        df,
        x='blob_count', y='time_diff_s', color='blob_count',
        title=title, points='outliers', quartilemethod='exclusive',
        color_discrete_map=color_map, thickness=0.5,
        hovertemplate=f'{bold("time difference")}: %{{y:.1f}}s<br>{bold("number of blobs")}: %{{x:,}}<extra></extra>', notched=True,
        ytitle='Time difference', xtitle='Blobs',
        xskips=1, yskips=2,
        title_annotation=f'Last {epochs:,.0f} epochs ({readable_timeframe})',
        ytick_text_formatter=format_seconds
    )

    fig.update_yaxes(range=[0, 12])

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

from clickhouse import BLOB_SIDECAR_TABLE, BLOCK_TABLE
from utils import bold, get_epoch_readable_unit
from plots.box.box import box_create_fig
from df_manip import df_clickhouse_create
from units import format_kilobytes

color_map = {
    1: '#c0ff8c',
    2: '#c4fffd',
    3: '#a6d1ff',
    4: '#b6a9ff',
    5: '#edb5ff',
    6: '#ffb8d3'
}


def block_size_vs_blobs_create(client):
    plotname = 'box_block-size-vs-blobs'
    title = 'Block size and blob count'
    slot_limit = 216000

    query = f'''
                select
                    blob_sidecars.slot as slot,
                    (max(block_total_bytes) / 1024) as kb_block_size,
                    count(distinct blob_index) as blob_count
                from (
                    select *
                    from {BLOB_SIDECAR_TABLE}
                ) as blob_sidecars
                inner join {BLOCK_TABLE} as blobs
                on blob_sidecars.slot = blobs.slot
                group by blob_sidecars.slot
                order by blob_sidecars.slot desc
                limit {slot_limit}
            '''

    df = df_clickhouse_create(client, query, title)

    hovertemplate = (
        f'{bold("Block size")}: %{{y:,.0f}}kb<br>'
        f'{bold("Number of blobs")}: %{{x:,.0f}}<extra></extra>'
    )
    epochs = (slot_limit / 32)
    readable_timeframe = get_epoch_readable_unit(epochs)
    x, y = 'blob_count', 'kb_block_size'

    fig = box_create_fig(
        df,
        x_axis_info=(x, 'Blob count'),
        y_axis_info=(y, 'Block size'),
        title=title, points='outliers', color='blob_count',
        color_discrete_map=color_map, thickness=0.5,
        hovertemplate=hovertemplate,
        xskips=1, yskips=500,
        ytickformat=format_kilobytes, xtickformat=',',
        title_annotation=f'Last {epochs:,.0f} epochs ({readable_timeframe})'
    )

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

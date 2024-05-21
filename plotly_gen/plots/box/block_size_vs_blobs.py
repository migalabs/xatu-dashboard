from plots.box.box import box_create_fig
from creates import df_clickhouse_create
from utils import bold, get_epoch_readable_unit
from units import format_kilobytes
from sessions import BLOB_SIDECAR_TABLE, BLOCK_TABLE

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
    title = 'Block size and number of blobs'
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

    epochs = (slot_limit / 32)
    readable_timeframe = get_epoch_readable_unit(epochs)

    # h_start = f'{bold("Block size")}: '
    # h_end = f'<br>{bold("number of blobs")}: %{{x:,}}<extra></extra>'
    # hovertemplate = np.select(
    #         [df['kb_block_size'] >= 1024], [f'%{{y:.0f}}mb'], f'%{{y:.0f}}kb'
    # )

    fig = box_create_fig(
        df,
        x='blob_count', y='kb_block_size',
        title=title, points='outliers', color='blob_count',
        color_discrete_map=color_map, thickness=0.5,
        hovertemplate=f'{bold("Block size")}: %{{y:,.0f}}kb<br>{bold("number of blobs")}: %{{x:,}}<extra></extra>',
        ytitle='Block Size', xtitle='Blobs',
        xskips=1, yskips=(df['kb_block_size'].max() / 5),
        ytick_text_formatter=format_kilobytes,
        title_annotation=f'Last {epochs:,.0f} epochs ({readable_timeframe})'
    )

    tickvals = fig['layout']['yaxis']['tickvals']

    fig.update_yaxes(
        tickvals=tickvals,
        ticktext=[format_kilobytes(x) + '     ' for x in tickvals],
        autorange=True
    )

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

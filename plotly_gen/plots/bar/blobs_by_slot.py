from plots.bar.bar import bar_create_fig
from creates import df_clickhouse_create
from sessions import BLOB_SIDECAR_TABLE
from utils import bold, fill_in_gaps, get_epoch_readable_unit


def bar_blobs_per_slot_create(client):
    plotname = 'bar_blobs-by-slot'
    title = 'Blob count per slot'
    slot_limit = 500

    query = f'''
                select slot, count(distinct blob_index) as blob_count
                from {BLOB_SIDECAR_TABLE}
                where meta_network_name = 'mainnet'
                group by slot
                order by slot desc
                limit {slot_limit}
            '''

    df = df_clickhouse_create(client, query, title)

    # adding all missing slots as new rows with 0 as blob count
    df = fill_in_gaps(df, column='slot', fill_value=0, limit=slot_limit)

    epochs = (slot_limit / 32)
    readable_timeframe = get_epoch_readable_unit(epochs)

    fig = bar_create_fig(
        df,
        x='slot', y='blob_count',
        title=title, color_discrete_sequence='#d9f45d', thickness=0.2,
        hovertemplate=f'{bold("slot")}: %{{x:,}}<br>{bold("blobs")}: %{{y:,}}',
        ytitle='Blob count', xtitle='Slot',
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})',
        xskips=len(df)/5, yskips=1
    )

    fig.update_traces(marker_line_color='#d9f45d', marker_line_width=1)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

from plots.bar.bar import bar_create_fig
from creates import df_clickhouse_create
from sessions import BLOB_SIDECAR_TABLE
from utils import bold, fill_in_gaps, title_format, get_epoch_readable_unit


def bar_slots_by_blob_count_create(client):
    plotname = 'bar_slots-by-blob-count'
    title = 'Slots by blob count'
    slot_limit = 216000

    query = f'''
                select slot, count(distinct blob_index) as blob_count
                from {BLOB_SIDECAR_TABLE}
                where meta_network_name = 'mainnet'
                group by slot
                order by slot desc
                limit {slot_limit}
            '''

    df = df_clickhouse_create(client, query, title)

    df = fill_in_gaps(df, column='slot', fill_value=0, limit=slot_limit)
    df = df.groupby('blob_count')['slot'].nunique().reset_index()
    df.columns = ['blob_count', 'slot_count']

    epochs = (slot_limit / 32)
    readable_timeframe = get_epoch_readable_unit(epochs)

    fig = bar_create_fig(
        df,
        x='blob_count', y='slot_count', title=title,
        color_discrete_sequence='#ff989f', thickness=0.5,
        hovertemplate=f'{bold("slots")}: %{{y:,}}<br>{bold("blobs")}: %{{x:,}}',
        ytitle='Slots', xtitle='Blob count',
        xskips=1, yskips=(df['slot_count'].max() / 5),
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})',
    )

    tickvals = fig['layout']['yaxis']['tickvals']

    fig.update_yaxes(
        tickvals=tickvals,
        ticktext=[bold(f"{'{:,.0f}'.format(x)}     ") for x in tickvals]
    )

    fig.update_traces(marker_line_color='#ff989f', marker_line_width=2)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

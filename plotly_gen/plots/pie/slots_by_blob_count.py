from plots.pie.pie import pie_fig_create
from creates import df_clickhouse_create, legend_labels_percent_parse
from utils import bold, get_epoch_readable_unit, legend_update, title_format
from sessions import BLOB_SIDECAR_TABLE

color_map = {
    1: '#c0ff8c',
    2: '#c4fffd',
    3: '#a6d1ff',
    4: '#b6a9ff',
    5: '#edb5ff',
    6: '#ffb8d3'
}


def pie_slots_by_blob_count_create(client):
    plotname = 'pie_slots-by-blob-count'
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

    df_grouped = df.groupby('blob_count')['slot'].count().reset_index()
    df_grouped.columns = ['blob_count', 'slots']
    legend_labels_percent_parse(
        df_grouped, percent_names=['blob_count', 'slots'], no_perc_labels=False
    )
    df_grouped['legend_labels'] = df_grouped.apply(
        lambda row: bold(f'{row['blob_count']:.0f} ({row['percentage']:.2f}%)'), axis=1)

    df = df_grouped

    epochs = (slot_limit / 32)
    readable_timeframe = get_epoch_readable_unit(epochs)

    fig = pie_fig_create(
        df, values='slots', names='legend_labels', slices_data='blob_count',
        colors={'color_discrete_map': color_map}, title=title,
        hoverplate=(f'{bold("%{value}")} slots with {bold("%{customdata[0]}")} blobs'),
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})',
        custom_data=['blob_count'], hole_text='SLOTS'
    )

    title_format(fig, title_dict=dict(title_y=0.97))

    legend_update(
        fig, show_legend=True,
        legend_dict=dict(x=0.5, y=-0.088, title=bold('Blob count'))
    )

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}
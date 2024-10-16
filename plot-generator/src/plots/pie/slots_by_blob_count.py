from utils import (
    bold, get_epoch_readable_unit, legend_update, title_format)
from df_manip import df_clickhouse_create, legend_labels_percent_parse
from plots.pie.pie import pie_fig_create
from clickhouse import BLOB_SIDECAR_TABLE, BLOCK_TABLE, BLOCK_CANON_TABLE

color_map = {
    0: '#fff566',
    1: '#c0ff8c',
    2: '#c4fffd',
    3: '#a6d1ff',
    4: '#b6a9ff',
    5: '#edb5ff',
    6: '#ffb8d3'
}


def slots_by_blob_count_create(client):
    plotname = 'pie_slots-by-blob-count'
    title = 'Slots by blob count'
    day_limit = 30

    query = f'''
                WITH
                    slots AS (
                        SELECT slot
                        FROM {BLOCK_TABLE}
                        WHERE toDate(slot_start_date_time) > now() - INTERVAL {day_limit} day
                        AND meta_network_name == 'mainnet'
                    ),
                    blobs AS (
                        SELECT slot, COUNT(DISTINCT blob_index) AS blob_count
                        FROM {BLOB_SIDECAR_TABLE}
                        WHERE toDate(slot_start_date_time) > now() - INTERVAL {day_limit} day
                        AND meta_network_name == 'mainnet'
                        GROUP BY slot
                    ),
                    canonical AS (
                        SELECT slot
                        FROM {BLOCK_CANON_TABLE}
                        WHERE toDate(slot_start_date_time) > now() - INTERVAL {day_limit} day
                        AND meta_network_name == 'mainnet'
                    )
                SELECT s.slot AS slot, IFNULL(b.blob_count, 0) AS blob_count
                FROM slots s
                LEFT JOIN blobs b ON slot = b.slot
                LEFT JOIN canonical c ON slot = c.slot
            '''

    df = df_clickhouse_create(client, query, title)
    df = df.groupby('blob_count')['slot'].count().reset_index()
    df.columns = ['blob_count', 'slots']
    legend_labels_percent_parse(df, percent_names=['blob_count', 'slots'])
    df['legend_labels'] = df.apply(
        lambda row: bold(f'{row["blob_count"]:.0f} ({row["percentage"]:.2f}%)'), axis=1)

    hovertemplate = (
        f'{bold("%{value}")} slots with {bold("%{customdata[0]}")} blobs'
    )

    epochs = (day_limit * 225)
    readable_timeframe = get_epoch_readable_unit(epochs)

    fig = pie_fig_create(
        df, values='slots', names='legend_labels', slices_data='blob_count',
        colors={'color_discrete_map': color_map}, title=title,
        hoverplate=hovertemplate,
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

from plots.bar.bar import bar_create_fig
from creates import df_clickhouse_create
from utils import bold, fill_in_gaps, title_format

# todo make this into env variable
BLOB_SIDECAR_TABLE = 'default.beacon_api_eth_v1_events_blob_sidecar'


def blobs_per_slot_create(client):
    plotname = 'blobs-by-slot'
    title = 'Blob count per slot'
    limit = 50

    query = f'''
                select slot, count(distinct blob_index) as blob_count
                from {BLOB_SIDECAR_TABLE}
                where meta_network_name = 'mainnet'
                group by slot
                order by slot desc
                limit {limit}
            '''

    df = df_clickhouse_create(client, query, title)

    # adding all missing slots as new rows with 0 as blob count
    df = fill_in_gaps(df, column='slot', fill_value=0, limit=limit)

    fig = bar_create_fig(
        df,
        x='slot', y='blob_count',
        title=title, color_discrete_sequence='#d9f45d', thickness=0.3,
        hovertemplate=f'{bold("slot")}: %{{x:,}}<br>{bold("blobs")}: %{{y:,}}',
        ytitle='Blob count', xtitle='Slot',
        xskips=5, yskips=1
    )

    fig.update_traces(marker_line_color='#d9f45d', marker_line_width=6)

    # For some reason annotations break everything so its added it into the
    # title instead. Reason MIGHT be annotations_delete()...?
    title_format(fig, dict(
        title_text=bold(title + "    -   ") + f' Latest {limit} slots'))

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

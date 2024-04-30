from plots.bar.bar import bar_create_fig
from creates import df_clickhouse_create
from utils import bold, fill_in_gaps

# todo make this into env variable
BLOB_SIDECAR_TABLE = 'default.beacon_api_eth_v1_events_blob_sidecar'


def slots_by_blob_count_create(client):
    plotname = 'slots-by-blob-count'
    title = 'Slots by blob count'
    limit = 7200

    query = f'''
                select slot, count(distinct blob_index) as blob_count
                from {BLOB_SIDECAR_TABLE}
                where meta_network_name = 'mainnet'
                group by slot
                order by slot desc
                limit {limit}
            '''

    df = df_clickhouse_create(client, query, title)

    df = fill_in_gaps(df, column='slot', fill_value=0, limit=limit)
    df = df.groupby('blob_count')['slot'].nunique().reset_index()
    df.columns = ['blob_count', 'slot_count']

    print(df)

    fig = bar_create_fig(
        df,
        x='blob_count', y='slot_count', title=title,
        color_discrete_sequence='#ff989f', thickness=0.5,
        hovertemplate=f'{bold("slots")}: %{{y:,}}<br>{bold("blobs")}: %{{x:,}}',
        ytitle='Slots', xtitle='Blob count',
        xskips=1, yskips=(df['slot_count'].max() / 5)
    )

    tickvals = fig['layout']['yaxis']['tickvals']

    fig.update_yaxes(
        tickvals=tickvals,
        ticktext=[f"<b>{'{:.0f}'.format(x)}     </b>" for x in tickvals]
    )

    fig.update_traces(marker_line_color='#ff989f', marker_line_width=2)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

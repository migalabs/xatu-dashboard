import contextlib
from plots.scatter.scatter import scatter_create_fig
from df_manip import df_clickhouse_create
from clickhouse import BLOB_SIDECAR_TABLE
from utils import bold, fill_in_gaps, get_epoch_readable_unit


def blobs_per_slot_create(client):
    plotname = 'scatter_blobs-by-slot'
    title = 'Blob count per slot'
    slot_limit = 7200

    query = f'''
                select slot, count(distinct blob_index) as blob_count
                from {BLOB_SIDECAR_TABLE}
                where meta_network_name = 'mainnet'
                group by slot
                order by slot desc
                limit {slot_limit}
            '''

    df = df_clickhouse_create(client, query, title)
    hovertemplate = (
        f'{bold("Slot")}: %{{x:,.0f}}<br>'
        f'{bold("Blob count")}: %{{y:,.0f}}<extra></extra>'
    )
    # adding all missing slots as new rows with 0 as blob count
    df = fill_in_gaps(df, column='slot', fill_value=0, limit=slot_limit)
    x, y = 'slot', 'blob_count'
    df[x] = df[x].apply(lambda x: f'<b>{x:,.0f}</b>')
    epochs = (slot_limit / 32)
    readable_timeframe = get_epoch_readable_unit(epochs)
    fig = scatter_create_fig(
        df, title=title,
        x_axis_info=(x, 'Slot'),
        y_axis_info=(y, 'Blob count'),
        xskips=700, yskips=1,
        xtickformat=',', symbol=y,
        color_discrete_sequence=['#344C6C'],
        hovertemplate=f'{bold("slot")}: %{{x}}<br>{bold("blobs")}: %{{y:,}}',
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})'
    )
    fig.update_traces(showlegend=False)
    fig.update_traces(marker_line_color='#ffffff', marker_line_width=0.3)
    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

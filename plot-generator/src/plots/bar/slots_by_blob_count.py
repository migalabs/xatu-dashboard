from utils import (
    bold, fill_in_gaps, get_epoch_readable_unit,
    fraction_clamp)
from plots.bar.bar import bar_create_fig
from df_manip import df_clickhouse_create
from clickhouse import BLOB_SIDECAR_TABLE


def slots_by_blob_count_create(client):
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

    hovertemplate = (
        f'{bold("Slots")}: %{{y:,.0f}}<br>'
        f'{bold("Blob count")}: %{{x:,.0f}}<extra></extra>'
    )
    epochs = (slot_limit / 32)
    readable_timeframe = get_epoch_readable_unit(epochs)
    x, y = 'blob_count', 'slot_count'

    fig = bar_create_fig(
        df, title=title,
        x_axis_info=(x, 'Blob count'),
        y_axis_info=(y, 'Slots'),
        color_discrete_sequence=['#ff989f'], thickness=0.5,
        hovertemplate=hovertemplate,
        xskips=1, yskips=fraction_clamp(df[y].max()/len(df), 1000),
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})',
    )
    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

from plots.area.area import area_create_fig, area_customize
from creates import df_clickhouse_create
from utils import date_since
from typing import List
from utils import bold, title_format


def ticktext_labels_truncate(skips, column) -> List[str]:
    ticktext = []
    for a, val in enumerate(column):
        if (a % skips) == 0:
            ticktext.append(str(val)[:10] + '...')
    return (ticktext)


def blob_size_used_per_blob_create(client):
    plotname = 'blob-size-used'
    title = 'Average used blob size per blob'
    start_time = date_since(days=1)
    day_limit = 15

    query = f'''
                select
                    toDate(event_date_time) as day,
                    avg((blob_sidecars_size-blob_sidecars_empty_size) / blob_sidecars_size * 100)  as used_blob_size
                from file('txs.parquet', Parquet)
                where meta_network_name = 'mainnet' and event_date_time > now() - interval {day_limit} day
                group by day
            '''

    df = df_clickhouse_create(client, query, title)

    fig = area_create_fig(
        df, x='day', y='used_blob_size', name='day',
        color_discrete_map=None, markers=False, customdata=None,
        color_lines='rgb(201, 255, 205)'
    )

    hovertemplate = f'{bold("Used size")}: %{{y:.3}}%<br>{bold("Date")}: %{{x}}<extra></extra>'

    area_customize(
        fig, df, title=title,
        xtitle='', ytitle='Used blob size', hovertemplate=hovertemplate,
        legend=False, percent=True, markers=False, start_time=start_time,
        inv=False, filling=True, name='used_blob_size', rate='200000000',
        yskips=10, xrange=[df['day'].min(), df['day'].max()],
        title_annotation=f' Latest {(225 * day_limit)} epochs ({day_limit} days)'
    )

    fig.update_layout(xaxis_tickangle=45)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

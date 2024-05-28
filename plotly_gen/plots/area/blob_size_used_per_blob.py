from plots.area.area import (
    area_create_fig, area_customize,
    FIVE_DAYS_RATE, DEFAULT_DATE_FORMAT)
from utils import date_since, get_epoch_readable_unit
from creates import df_clickhouse_create
from sessions import TXS_TABLE
from typing import List
from utils import bold


def ticktext_labels_truncate(skips, column) -> List[str]:
    ticktext = []
    for a, val in enumerate(column):
        if (a % skips) == 0:
            ticktext.append(str(val)[:10] + '...')
    return (ticktext)


def blob_size_used_per_blob_create(client):
    plotname = 'area_blob-size-used'
    title = 'Average used blob size per blob'
    day_limit = 30

    query = f'''
               select
                    toDate(event_date_time) as day,
                    avg((blob_sidecars_size-blob_sidecars_empty_size) / blob_sidecars_size * 100)  as used_blob_size
                from {TXS_TABLE}
                where meta_network_name = 'mainnet' and event_date_time > now() - interval {day_limit} day
                group by day
            '''

    df = df_clickhouse_create(client, query, title)
    x, y = 'day', 'used_blob_size'
    fig = area_create_fig(
        df, x=x, y=y, name=x,
        color_discrete_map=None, markers=False, customdata=None,
        color_lines='rgb(152, 207, 169)'
    )

    hovertemplate = f'{bold("Used size")}: %{{y:.3}}%<br>{bold("Date")}: %{{x}}<extra></extra>'

    epochs = (day_limit * 225)
    readable_timeframe = get_epoch_readable_unit(epochs)
    area_customize(
        df, fig, title=title,
        x_col_title=(x, ''),
        y_col_title=(y, 'Used blob size'),
        yrange=[0, df[y].max() + 5],
        hovertemplate=hovertemplate,
        yskips=10, xskips=FIVE_DAYS_RATE,
        xtickformat=DEFAULT_DATE_FORMAT,
        ytickformat=lambda y: bold(f'{y}%'),
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})'
    )
    # area_customize(
    #     fig, df, title=title,
    #     xtitle='', ytitle='Used blob size', hovertemplate=hovertemplate,
    #     legend=False, percent=True, markers=False, start_time=start_time,
    #     inv=False, filling=True, name=y, x=x, rate='604800000',
    #     yskips=10, xrange=[df[x].min(), df[x].max()],
    #     title_annotation=f' Latest {epochs:,.0f} epochs ({readable_timeframe})'
    # )

    fig.update_layout(xaxis_tickangle=45)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

from plots.area.area import area_create_fig, area_customize
from df_manip import df_clickhouse_create
from clickhouse import BLOB_SIDECAR_TABLE
from utils import fraction_clamp
from utils import bold


def format_truncate(x: str) -> str:
    '''
    Get the string's first 10 characters plus a trailing '...'
    '''
    return (f'{str(x)[:10]}...')


def blob_hash_repetitions_create(client):
    plotname = 'area_blob-hash-repetitions'
    title = 'Blob hash repetitions'
    limit = 150

    query = f'''
                select
                    versioned_hash,
                    COUNT(*) AS repeat_times
                FROM {BLOB_SIDECAR_TABLE}
                WHERE meta_network_name = 'mainnet'
                GROUP BY versioned_hash
                ORDER BY repeat_times DESC
                LIMIT {limit}
            '''

    df = df_clickhouse_create(client, query, title)
    df['full_hashes'] = df['versioned_hash']

    hovertemplate = (
        f'{bold("Repetitions")}: %{{y:,.0f}}<br>'
        f'{bold("Hash")}: %{{customdata[0]}}<extra></extra>'
    )
    xskips = 10
    x, y = 'versioned_hash', 'repeat_times'

    fig = area_create_fig(
        df, x=x, y=y, color=x,
        color_discrete_map=None, markers=False, customdata='full_hashes',
        line_color='rgb(255, 181, 120)', log_y=True
    )
    area_customize(
        df, fig, title=title,
        x_axis_info=(x, 'Hash'),
        y_axis_info=(y, 'Repetitions'),
        hovertemplate=hovertemplate,
        yskips=fraction_clamp(df[y].max() / 5),
        xskips=xskips,
        xtickformat=format_truncate,
        title_annotation=f'{limit} hashes (all time)'
    )
    # Tilt ticks slightly
    fig.update_layout(xaxis_tickangle=45)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

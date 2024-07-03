from utils import bold, get_epoch_readable_unit, fraction_clamp
from plots.bar.bar import bar_create_fig
from df_manip import df_clickhouse_create
from clickhouse import BLOB_SIDECAR_TABLE, BLOCK_TABLE, BLOCK_CANON_TABLE


def slots_by_blob_count_create(client):
    plotname = 'bar_slots-by-blob-count'
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
    df = df.groupby('blob_count')['slot'].nunique().reset_index()
    df.columns = ['blob_count', 'slot_count']

    hovertemplate = (
        f'{bold("Slots")}: %{{y:,.0f}}<br>'
        f'{bold("Blob count")}: %{{x:,.0f}}<extra></extra>'
    )
    epochs = (day_limit * 225)
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

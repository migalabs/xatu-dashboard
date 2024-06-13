from plots.area.area import (
    area_create_fig, area_customize,
    DEFAULT_DATE_FORMAT, FIVE_DAYS_RATE)
from utils import (
    date_since, bold, fraction_clamp, get_epoch_readable_unit)
from clickhouse import BLOB_SIDECAR_TABLE, TXS_TABLE
from df_manip import df_clickhouse_create


def type_3_transactions_per_block_create(client):
    plotname = 'area_type-3-transactions'
    title = 'Type 3 Transactions per block'
    day_limit = 30

    query = f'''
                WITH ranked_entries AS (
                        SELECT *,
                        ROW_NUMBER() OVER (PARTITION BY block_root, versioned_hash, blob_index ORDER BY slot_start_date_time ASC) AS rn
                        FROM {BLOB_SIDECAR_TABLE}
                        where propagation_slot_start_diff < 100000
                        and meta_network_name = 'mainnet'
                    )
                select
                    slot,
                    type,
                    count() as tx_count
                from (
                    select *
                    from {TXS_TABLE}
                    array join blob_hashes
                    where meta_network_name = 'mainnet'
                     ) as mainnet_txs
                inner join ranked_entries
                on mainnet_txs.blob_hashes = ranked_entries.versioned_hash
                where rn = 1
                and toDate(slot_start_date_time) > now() - interval {day_limit} day
                group by slot, type
                limit {day_limit}
            '''

    client.execute('SET max_memory_usage = 16106127360')
    df = df_clickhouse_create(client, query, title)

    hovertemplate = (
        f'{bold("Type 3 transactions")}: %{{y:,.0f}}<br>'
        f'{bold("Slot number")}: %{{customdata[0]:,.0f}}<extra></extra>'
    )
    epochs = (day_limit * 225)
    readable_timeframe = get_epoch_readable_unit(epochs)
    x, y = 'slot', 'tx_count'

    fig = area_create_fig(
        df, x=x, y=y, color='type',
        color_discrete_map=None, markers=True, customdata='slot',
        line_color='rgb(92, 255, 92)'
    )
    area_customize(
        df, fig, title=title,
        x_axis_info=(x, 'Slot number'),
        y_axis_info=(y, 'Type 3 transactions'),
        yrange=[0, df[y].max() + 5],
        hovertemplate=hovertemplate,
        yskips=fraction_clamp(df[y].max() / 7, 10),
        xskips=None, xtickformat=',',
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})'
    )
    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

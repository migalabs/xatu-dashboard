from plots.area.area import (
    area_create_fig, area_customize, fraction_clamp,
    DEFAULT_DATE_FORMAT, FIVE_DAYS_RATE)
from utils import date_since, bold, get_epoch_readable_unit
from sessions import BLOB_SIDECAR_TABLE, TXS_TABLE
from creates import df_clickhouse_create


def type_3_transactions_per_block_create(client):
    plotname = 'area_type-3-transactions'
    title = 'Type 3 Transactions per block'
    day_limit = 30

    query = f'''
                WITH ranked_entries AS (
                        SELECT *,
                        ROW_NUMBER() OVER (PARTITION BY block_root, versioned_hash, blob_index ORDER BY slot_start_date_time ASC) AS rn
                        FROM {BLOB_SIDECAR_TABLE}
                        WHERE propagation_slot_start_diff < 100000
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
                where rn = 1 and toDate(slot_start_date_time) > now() - interval {day_limit} day
                group by slot, type
                limit {day_limit}
            '''

    client.execute('SET max_memory_usage = 16106127360')
    df = df_clickhouse_create(client, query, title)
    x, y = 'slot', 'tx_count'
    fig = area_create_fig(
        df, x=x, y=y, name='type',
        color_discrete_map=None, markers=True, customdata='slot',
        color_lines='rgb(92, 255, 92)'
    )

    hovertemplate = (
        f'{bold("Type 3 transactions")}: %{{y:,.0f}}<br>'
        f'{bold("Slot number")}: %{{customdata[0]:,.0f}}<extra></extra>'
    )
    epochs = (day_limit * 225)
    readable_timeframe = get_epoch_readable_unit(epochs)
    area_customize(
        df, fig, title=title,
        x_col_title=(x, 'Slot number'), y_col_title=(y, 'Type 3 transactions'),
        yrange=[0, df[y].max() + 5],
        hovertemplate=hovertemplate,
        yskips=fraction_clamp(df[y].max() / 7, 10),
        xskips=None, xtickformat=',',
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})'
    )

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}
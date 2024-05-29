from plots.area.area import (
    area_create_fig, area_customize, fraction_clamp,
    DEFAULT_DATE_FORMAT, FIVE_DAYS_RATE)
from utils import bold, get_epoch_readable_unit
from sessions import BLOB_SIDECAR_TABLE, TXS_TABLE
from creates import df_clickhouse_create


def day_type_3_transactions_per_block_create(client):
    plotname = 'area_day-type-3-transactions'
    title = 'Type 3 Transactions per block, grouped by day'
    day_limit = 30

    query = f'''
                WITH ranked_entries AS (
                        select *,
                        ROW_NUMBER() OVER (PARTITION BY block_root, versioned_hash, blob_index ORDER BY slot_start_date_time ASC) AS rn
                        from {BLOB_SIDECAR_TABLE}
                        where propagation_slot_start_diff < 100000
                        and meta_network_name = 'mainnet'
                )
                select
                    slot,
                    type,
                    toDate(slot_start_date_time) as day,
                    count() as tx_count
                from (
                    select *
                    from {TXS_TABLE}
                    array join blob_hashes
                    where meta_network_name = 'mainnet'
                ) as mainnet_txs
                inner join ranked_entries
                on mainnet_txs.blob_hashes = ranked_entries.versioned_hash
                where rn = 1 and day > now() - interval {day_limit} day
                group by slot, type, day
            '''

    client.execute('SET max_memory_usage = 16106127360')
    df = df_clickhouse_create(client, query, title)
    x, y = 'day', 'tx_count'
    print(df)
    fig = area_create_fig(
        df, x=x, y=y, name='type',
        color_discrete_map=None, markers=True, customdata='slot',
        color_lines='rgb(165, 255, 97)'
    )

    hovertemplate = (
        f'{bold("Type 3 transactions")}: %{{y:,.0f}}<br>'
        f'{bold("Slot number")}: %{{customdata[0]:,.0f}}<br>'
        f'{bold("Date")}: %{{x}}<extra></extra>'
    )
    epochs = (day_limit * 225)
    readable_timeframe = get_epoch_readable_unit(epochs)
    area_customize(
        df, fig, title=title,
        x_col_title=(x, ''), y_col_title=(y, 'Type 3 transactions'),
        xrange=[df[x].min(), df[x].max()],
        yrange=[0, df[y].max() + 5],
        hovertemplate=hovertemplate,
        yskips=fraction_clamp(df[y].max() / 5, 10),
        xskips=FIVE_DAYS_RATE, xtickformat=DEFAULT_DATE_FORMAT,
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})'
    )

    fig.update_layout(xaxis_tickangle=45)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

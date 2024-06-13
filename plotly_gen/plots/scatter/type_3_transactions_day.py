from plots.scatter.scatter import (scatter_create_fig)
from plots.area.area import FIVE_DAYS_RATE, DEFAULT_DATE_FORMAT
from utils import bold, get_epoch_readable_unit, fraction_clamp
from clickhouse import BLOB_SIDECAR_TABLE, TXS_TABLE
from df_manip import df_clickhouse_create


def day_type_3_transactions_per_block_create(client):
    plotname = 'scatter_day-type-3-transactions'
    title = 'Type 3 Transactions per day'
    day_limit = 30

    query = f'''
                 WITH ranked_entries AS (
                        select *,
                        ROW_NUMBER() OVER (PARTITION BY
                            block_root, versioned_hash, blob_index
                            ORDER BY slot_start_date_time ASC) AS rn
                        from beacon_api_eth_v1_events_blob_sidecar
                        where propagation_slot_start_diff < 100000
                        and meta_network_name = 'mainnet'
                )
                select
                    slot,
                    type,
                    count() as tx_count,
                    toDate(slot_start_date_time) as day
                from (
                    select *
                    from mempool_transaction
                    array join blob_hashes
                    where meta_network_name = 'mainnet'
                ) as mainnet_txs
                inner join ranked_entries
                on mainnet_txs.blob_hashes = ranked_entries.versioned_hash
                where rn = 1 and abs(date_diff('seconds', mainnet_txs.event_date_time, ranked_entries.event_date_time)) < 12
                group by slot, type, day
                order by tx_count desc
            '''

    client.execute('SET max_memory_usage = 16106127360')
    df = df_clickhouse_create(client, query, title)

    hovertemplate = (
        f'{bold("Type 3 transactions")}: %{{y:,.0f}}<br>'
        f'{bold("Slot number")}: %{{customdata[0]:,.0f}}<br>'
        f'{bold("Date")}: %{{x}}<extra></extra>'
    )
    epochs = (day_limit * 225)
    readable_timeframe = get_epoch_readable_unit(epochs)
    x, y, color = 'day', 'tx_count', 'type'

    fig = scatter_create_fig(
        df, title=title, show_legend=False,
        x_axis_info=(x, 'Date'),
        y_axis_info=(y, 'Type 3 Transactions'),
        yskips=fraction_clamp(df[y].max() / 5, 10),
        xskips=FIVE_DAYS_RATE, xtickformat=DEFAULT_DATE_FORMAT,
        color_discrete_sequence=None, customdata=['slot'],
        hovertemplate=hovertemplate,
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})'
    )
    fig.update_traces(marker_line_color='#ffffff', marker_line_width=0.5)
    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

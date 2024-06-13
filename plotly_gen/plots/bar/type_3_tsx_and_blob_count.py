from plots.bar.bar import (bar_create_fig)
from axis_tools import FIVE_DAYS_RATE, DEFAULT_DATE_FORMAT
from utils import (
    annotations_add, bold, get_epoch_readable_unit, fraction_clamp,
    fill_in_gaps)
from clickhouse import BLOB_SIDECAR_TABLE, TXS_TABLE
from df_manip import df_clickhouse_create
import plotly.graph_objects as go


def day_type_3_transactions_and_blob_count_create(client):
    plotname = 'bar_day-type-3-transactions-blob-count'
    title = 'Type 3 Transactions and blob count per block'
    slot_limit = 150

    query = f'''
                 WITH ranked_entries AS (
                        select *,
                        ROW_NUMBER() OVER (PARTITION BY block_root, versioned_hash, blob_index ORDER BY slot_start_date_time ASC) AS rn
                        from beacon_api_eth_v1_events_blob_sidecar
                        where propagation_slot_start_diff < 100000
                        and meta_network_name = 'mainnet'
                )
                select
                    slot,
                    type,
                    count() as tx_count,
                    count(distinct blob_index) as blob_count
                from (
                    select *
                    from mempool_transaction
                    array join blob_hashes
                    where meta_network_name = 'mainnet'
                ) as mainnet_txs
                inner join ranked_entries
                on mainnet_txs.blob_hashes = ranked_entries.versioned_hash
                where rn = 1 and abs(date_diff('seconds', mainnet_txs.event_date_time, ranked_entries.event_date_time)) < 12
                group by slot, type
                order by tx_count desc
                limit {slot_limit}
            '''

    client.execute('SET max_memory_usage = 16106127360')
    df = df_clickhouse_create(client, query, title)
    df = df.melt(
        id_vars='slot', value_vars=['tx_count', 'blob_count'],
        var_name='info', value_name='count')

    hovertemplate = (
        f'<b>%{{customdata[0]}}</b><br>'
        f'{bold("Count")}: %{{y:,.0f}}<br>'
        f'{bold("Slot")}: %{{x}}<extra></extra>'
    )
    epochs = (slot_limit / 32)
    readable_timeframe = get_epoch_readable_unit(epochs)
    x, y, color = 'slot', 'count', 'info'
    df[x] = df[x].apply(lambda x: f'<b>{x:,.0f}</b>')

    fig = bar_create_fig(
        df, title=title,
        color=color, show_legend=True,
        x_axis_info=(x, 'Slot'),
        y_axis_info=(y, 'Count'),
        color_discrete_sequence=['#E68D8D', '#618AE4'], thickness=0.2,
        hovertemplate=hovertemplate,
        xskips=50, yskips=1,
        customdata=['info'], barmode='group',
        title_annotation=f'{slot_limit} blocks',
    )
    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)
    return {plotname: plot_div}

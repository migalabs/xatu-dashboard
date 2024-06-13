from plots.histogram.histogram import (histogram_create_fig)
from axis_tools import FIVE_DAYS_RATE, DEFAULT_DATE_FORMAT
from utils import (
    annotations_add, bold, get_epoch_readable_unit, fraction_clamp)
from clickhouse import BLOB_SIDECAR_TABLE, TXS_TABLE
from df_manip import df_clickhouse_create
import plotly.graph_objects as go


def day_type_3_transactions_and_blob_count_create(client):
    plotname = 'histogram_day-type-3-transactions-blob-count'
    title = 'Type 3 Transactions per block, grouped by day with blob count'
    slot_limit = 10

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
                    count() as tx_count,
                    count(distinct blob_index) as blob_count
                from (
                    select *
                    from {TXS_TABLE}
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
    x, y = 'slot', 'tx_count'
    color = 'blob_count'

    hovertemplate = (
        f'{bold("Type 3 transactions")}: %{{y:,.0f}}<br>'
        f'{bold("Blob count")}: %{{labels:,.0f}}<br>'
        f'{bold("Slot number")}: %{{customdata[0]:,.0f}}<br>'
        f'{bold("Date")}: %{{x}}<extra></extra>'
    )
    epochs = (slot_limit / 32)
    readable_timeframe = get_epoch_readable_unit(epochs)
    fig = histogram_create_fig(
        df, title=title, color=None, color_sequence=["#000000", "#aeae00"],
        show_legend=True,
        x_axis_info=(x, 'Date'),
        y_axis_info=(y, 'Type 3 Transactions'),
        yskips=1,
        customdata=['slot', y[1]], nbins=10,
        hovertemplate=hovertemplate
    )

    # Create a bar for tx_count
    fig.add_trace(go.Bar(
        x=df['slot'],
        y=df['tx_count'],
        name='tx_count',
        marker_color='blue',  # tx_count bars are blue
        hovertemplate=(
            f'{bold("Type 3 transactions")}: %{{y:,.0f}}<br>'
            f'{bold("Slot number")}: %{{x:,.0f}}<extra></extra>'
        )
    ))

    # Create a bar for blob_count
    fig.add_trace(go.Bar(
        x=df['slot'],
        y=df['blob_count'],
        name='blob_count',
        marker_color='green',  # blob_count bars are green
        hovertemplate=(
            f'{bold("Blob count")}: %{{y:,.0f}}<br>'
            f'{bold("Slot number")}: %{{x:,.0f}}<extra></extra>'
        )
    ))

    fig.update_layout(barmode='group')  # Bars are grouped by slot
    fig.update_layout(title_text=title)
    fig.update_traces(marker_line_color='#ffffff', marker_line_width=0.5)
    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

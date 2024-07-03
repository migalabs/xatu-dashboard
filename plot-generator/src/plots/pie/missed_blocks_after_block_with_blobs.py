from plots.pie.pie import pie_fig_create
from df_manip import df_clickhouse_create, legend_labels_percent_parse
from utils import bold, get_epoch_readable_unit, legend_update, title_format
from creates import NOW
import pandas as pd
from clickhouse import BLOB_SIDECAR_TABLE, BLOCK_CANON_TABLE

color_map = {
    0: '#fff566',
    1: '#c0ff8c',
    2: '#c4fffd',
    3: '#a6d1ff',
    4: '#b6a9ff',
    5: '#edb5ff',
    6: '#ffb8d3'
}


def get_blob_count_before_miss(client, day_limit, title) -> tuple:
    '''
    Get a tuple of dataframes: (missed blocks, all blocks)
    '''
    query_canonical = (f'''
        SELECT
                slot,
                toInt64(ROW_NUMBER() OVER (ORDER BY slot DESC)) AS row_num
            FROM
                {BLOCK_CANON_TABLE}
            WHERE meta_network_name = 'mainnet'
            AND toDate(slot_start_date_time) > toDate('{NOW}') - INTERVAL {day_limit} day
        ''')
    df_canonical_blocks = client.query_dataframe(query_canonical)

    query_canon_diff = (f'''
            WITH ordered_blocks AS (
                SELECT
                    slot,
                    toInt64(ROW_NUMBER() OVER (ORDER BY slot DESC)) AS row_num
                FROM
                    {BLOCK_CANON_TABLE}
                WHERE meta_network_name = 'mainnet'
                AND toDate(slot_start_date_time) > toDate('{NOW}') - INTERVAL {day_limit} day
            )
            SELECT
                current.slot AS current_slot,
                previous.slot AS previous_slot,
                current.slot - previous.slot AS slot_difference
            FROM
                ordered_blocks AS current
            LEFT JOIN
                ordered_blocks AS previous
            ON
                current.row_num = previous.row_num - 1
            ORDER BY
                current.slot DESC
    ''')

    df_canonical_blocks_diff = client.query_dataframe(query_canon_diff)
    query_blobs = (f'''
        WITH RankedEntries AS (
            SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY
                            block_root, versioned_hash, blob_index
                        ORDER BY
                            slot_start_date_time ASC, event_date_time ASC
                        ) AS rn
            FROM {BLOB_SIDECAR_TABLE}
            WHERE meta_network_name = 'mainnet'
            AND propagation_slot_start_diff <= 100000
            AND toDate(slot_start_date_time) > toDate('{NOW}') - INTERVAL {day_limit} day
        )
        SELECT slot, block_root, COUNT(DISTINCT(blob_index)) as blob_count
        FROM RankedEntries
        WHERE rn = 1
        GROUP BY slot, block_root
        ORDER BY slot DESC
    ''')

    df_blobs = df_clickhouse_create(client, query_blobs, title)

    # Filter by slot difference > 1
    df_filtered = df_canonical_blocks_diff[df_canonical_blocks_diff['slot_difference'] > 1]
    # Ensure unique slots by grabbing first ocurrence
    blobs_found_unique = df_blobs.groupby('slot').agg({'blob_count': 'first'}).reset_index()

    # Get missed blocks from df_filtered and all blocks from canonical
    missed_blocks = pd.DataFrame({'slot': df_filtered['previous_slot']})
    all_blocks = pd.DataFrame({'slot': df_canonical_blocks['slot']})

    # Map to slot's blob count, if there is no match, set blob_count as 0
    missed_blocks['blob_count'] = missed_blocks['slot'].map(blobs_found_unique.set_index('slot')['blob_count']).fillna(0).astype(int)
    all_blocks['blob_count'] = all_blocks['slot'].map(blobs_found_unique.set_index('slot')['blob_count']).fillna(0).astype(int)

    # Sort by blob count
    all_blocks.sort_values('blob_count', inplace=True)
    missed_blocks.sort_values('blob_count', inplace=True)

    return (missed_blocks, all_blocks)


def missed_blocks_after_block_with_blobs_create(client):
    plotname = 'pie_missed-after-blob-count'
    title = 'Blob count before missed block'
    day_limit = 30

    # Get missed blocks, ignore all blocks from return
    (df, _) = get_blob_count_before_miss(client, day_limit, title)

    # Group by blob count and rename 'slot' to 'slot_count'
    df = df.groupby('blob_count')['slot'].count().reset_index()
    df.columns = ['blob_count', 'slot_count']

    # Set legend labels (format to percentage)
    legend_labels_percent_parse(df, percent_names=['blob_count', 'slot_count'])
    df['legend_labels'] = df.apply(
        lambda row: bold(
            f'{row["blob_count"]:.0f} ({row["percentage"]:.2f}%)'), axis=1)

    hovertemplate = (
        f'{bold("%{value}")} slot_count with {bold("%{customdata[0]}")} blobs '
        f'before a missed block<extra></extra>'
    )
    epochs = (day_limit * 225)
    readable_timeframe = get_epoch_readable_unit(epochs)

    fig = pie_fig_create(
        df, values='slot_count', names='legend_labels', slices_data='blob_count',
        colors={'color_discrete_map': color_map}, title=title,
        hoverplate=hovertemplate,
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})',
        custom_data=['blob_count'], hole_text='BLOCKS MISSED'
    )
    title_format(fig, title_dict=dict(title_y=0.97))
    legend_update(
        fig, show_legend=True,
        legend_dict=dict(x=0.5, y=-0.088, title=bold('Blob count'))
    )
    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

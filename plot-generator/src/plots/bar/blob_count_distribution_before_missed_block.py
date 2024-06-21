from utils import (
    bold, fill_in_gaps, get_epoch_readable_unit,
    fraction_clamp)
from plots.bar.bar import bar_create_fig
from df_manip import df_clickhouse_create
import pandas as pd
import numpy as np
from clickhouse import BLOB_SIDECAR_TABLE, BLOCK_TABLE


def blob_count_distribution_before_missed_block_create(client):
    plotname = 'bar_distribution-before-missed-block'
    title = 'Slots by blob count'
    day_limit = 30

    df_blob_count = client.query_dataframe(f'''
                WITH
                    slots AS (
                        SELECT slot
                        FROM {BLOCK_TABLE}
                        WHERE toDate(slot_start_date_time) > now() - INTERVAL {day_limit} day
                        and meta_network_name = 'mainnet'
                    ),
                    blobs AS (
                        SELECT slot, COUNT(DISTINCT blob_index) as blob_count
                        FROM {BLOB_SIDECAR_TABLE}
                        WHERE toDate(slot_start_date_time) > now() - INTERVAL {day_limit} day
                        and meta_network_name = 'mainnet'
                        GROUP BY slot
                    )
                SELECT s.slot as slot, IFNULL(b.blob_count, 0) as blob_count
                FROM slots s
                LEFT JOIN blobs b ON slot = b.slot
        ''')
    df_blob_count = df_blob_count.groupby('blob_count')['slot'].nunique().reset_index()
    df_blob_count.columns = ['blob_count', 'slot_count']

    query = f'''
                WITH prev_missed_slots as(
                    select
                        slot_list.slot,
                        epoch
                    from (
                        select
                            distinct(slot),
                            epoch
                        from beacon_api_eth_v1_beacon_committee
                        where slot < (select max(slot) from beacon_api_eth_v1_events_head)
                        and toDate(slot_start_date_time) > now() - interval {day_limit} day
                        and meta_network_name = 'mainnet'
                    ) as slot_list
                    left join beacon_api_eth_v1_events_block
                        on slot_list.slot + 1 = beacon_api_eth_v1_events_block.slot
                    where beacon_api_eth_v1_events_block.slot = 0
                    order by slot_list.slot desc
                )

                SELECT
                    slt.slot,
                    ubm.block_root,
                    count(DISTINCT ubm.blob_index) AS blob_count
                FROM
                    prev_missed_slots AS slt
                LEFT JOIN
                    (select distinct *
                    from beacon_api_eth_v1_events_blob_sidecar) AS ubm
                ON
                    slt.slot = ubm.slot
                    AND ubm.meta_network_name = 'mainnet'
                WHERE
                    block_root != ''
                GROUP BY
                    slt.slot,
                    ubm.block_root
                ORDER BY
                    blob_count DESC;
            '''

    df = df_clickhouse_create(client, query, title)

    df = df.groupby('blob_count')['slot'].nunique().reset_index()
    df.columns = ['blob_count', 'slot_count']
    df = df.sort_values(by='blob_count', ascending=True)
    df_blob_count = df_blob_count[df_blob_count['blob_count'] > 0]
    df_blob_count = df_blob_count.sort_values(by='blob_count', ascending=True)
    df_merged = pd.merge(df, df_blob_count, on='blob_count', suffixes=('_df', '_df_blob_count'))
    df_merged['percentage'] = df_merged['slot_count_df'] / df_merged['slot_count_df_blob_count'] * 100
    df['percentage'] = df_merged['percentage']
    print(f'Percentage: {df_merged}')
    hovertemplate = (
        f'{bold("Percentage")}: %{{y:,.3f}}%<br>'
        f'{bold("Blob count")}: %{{x:,.0f}}<extra></extra>'
    )
    epochs = (day_limit * 225)
    readable_timeframe = get_epoch_readable_unit(epochs)
    x, y = 'blob_count', 'percentage'

    fig = bar_create_fig(
        df_merged, title=title,
        x_axis_info=(x, 'Blob count'),
        y_axis_info=(y, 'Percentage'),
        color_discrete_sequence=['#69cde4'], thickness=0.3,
        hovertemplate=hovertemplate,
        xskips=1, yskips=0.1,
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})',
        y_formatter=lambda y: f'{bold(f"{y:.3f}")}%',
        x_formatter=',.0f'
    )
    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

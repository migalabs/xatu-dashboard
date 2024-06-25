from utils import (
    bold, fill_in_gaps, get_epoch_readable_unit,
    fraction_clamp)
from plots.bar.bar import bar_create_fig
from df_manip import df_clickhouse_create
import pandas as pd
import numpy as np
from clickhouse import BLOB_SIDECAR_TABLE, BLOCK_TABLE
from plots.pie.missed_blocks_after_block_with_blobs import get_blob_count_before_miss


def blob_count_distribution_before_missed_block_create(client):
    plotname = 'bar_distribution-before-missed-block'
    title = 'Blob distribution before missed block'
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

    df = get_blob_count_before_miss(client, day_limit, title)
    df = df.groupby('blob_count')['slot'].nunique().reset_index()
    df.columns = ['blob_count', 'slot_count']
    df = df.sort_values(by='blob_count', ascending=True)
    df_blob_count = df_blob_count.sort_values(by='blob_count', ascending=True)
    df_merged = pd.merge(df, df_blob_count, on='blob_count', suffixes=('_df', '_df_blob_count'))
    df_merged['percentage'] = df_merged['slot_count_df'] / df_merged['slot_count_df_blob_count'] * 100

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

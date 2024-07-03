from utils import bold, get_epoch_readable_unit
from plots.bar.bar import bar_create_fig
import pandas as pd
from plots.pie.missed_blocks_after_block_with_blobs import (
    get_blob_count_before_miss)


def blob_count_distribution_before_missed_block_create(client):
    plotname = 'bar_distribution-before-missed-block'
    title = 'Blob distribution before missed block'
    day_limit = 30

    # Get missed blocks and all blocks
    (df, df_all) = get_blob_count_before_miss(client, day_limit, title)

    # Group by blob count and rename 'slot' to 'slot_count' on both dataframes
    df = df.groupby('blob_count')['slot'].nunique().reset_index()
    df.columns = ['blob_count', 'slot_count']
    df_all = df_all.groupby('blob_count')['slot'].nunique().reset_index()
    df_all.columns = ['blob_count', 'slot_count']

    # Sort both dataframes by blob count (ascending)
    df = df.sort_values(by='blob_count', ascending=True)
    df_all = df_all.sort_values(by='blob_count', ascending=True)

    # Merge both dataframes
    df_merged = pd.merge(df, df_all, on='blob_count', suffixes=('_missed', '_all'))
    # Calculate ratio percentage from missed to all slot counts
    df_merged['percentage'] = df_merged['slot_count_missed'] / df_merged['slot_count_all'] * 100

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

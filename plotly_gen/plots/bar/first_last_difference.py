from utils import bold, get_epoch_readable_unit
from plots.bar.bar import bar_create_fig
from creates import df_clickhouse_create
from sessions import BLOB_SIDECAR_TABLE
from units import format_seconds


def first_last_difference_create(client):
    plotname = 'bar_first-last-timediff'
    title = 'Time difference between first and last blob'
    slot_limit = 500

    query = f'''
                select
                    slot,
                    count(distinct blob_index) as blob_count,
                    min(propagation_slot_start_diff)/1000 min,
                    max(propagation_slot_start_diff)/1000 max,
                    AVG(propagation_slot_start_diff)/1000 AS avg
                from (
                    select *,
                           ROW_NUMBER() over (partition by block_root, versioned_hash, blob_index, slot ORDER by slot_start_date_time asc) as rn
                    from {BLOB_SIDECAR_TABLE}
                    where meta_network_name = 'mainnet'
                    and propagation_slot_start_diff < 100000
                )
                where rn = 1
                group by slot
                having count(distinct blob_index) >= 2
                order by slot desc
                limit {slot_limit}
            '''

    df = df_clickhouse_create(
        client, query, title
    )

    df['time_diff_ms'] = df['max'] - df['min']
    epochs = (slot_limit / 32)
    readable_timeframe = get_epoch_readable_unit(epochs)

    fig = bar_create_fig(
        df,
        x='slot', y='time_diff_ms',
        title=title,
        color_discrete_sequence='#d5c3fc', thickness=0.5,
        hovertemplate=f'{bold("time difference")}: %{{y:.0f}}ms<br>{bold("slot")}: %{{x:,}}',
        ytitle='Time difference', xtitle='Slots',
        xskips=len(df)/5, yskips=(df['time_diff_ms'].max() / 5),
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})'
    )

    # @todo add ticktext formatting to bar_create_fig
    tickvals = fig['layout']['yaxis']['tickvals']

    fig.update_yaxes(
        tickvals=tickvals,
        ticktext=[format_seconds(x) for x in tickvals]
    )
    fig.update_traces(marker_line_color='#d5c3fc', marker_line_width=2)

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

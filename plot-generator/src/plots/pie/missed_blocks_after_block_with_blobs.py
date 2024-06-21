from plots.pie.pie import pie_fig_create
from df_manip import df_clickhouse_create, legend_labels_percent_parse
from utils import bold, fill_in_gaps, get_epoch_readable_unit, legend_update, title_format
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


def missed_blocks_after_block_with_blobs_create(client):
    plotname = 'pie_missed-after-blob-count'
    title = 'Blob count before missed block'
    day_limit = 30

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
    df = df.groupby('blob_count')['slot'].count().reset_index()
    df.columns = ['blob_count', 'slots']
    legend_labels_percent_parse(
        df, percent_names=['blob_count', 'slots'], no_perc_labels=False
    )
    df['legend_labels'] = df.apply(
        lambda row: bold(
            f'{row["blob_count"]:.0f} ({row["percentage"]:.2f}%)'), axis=1)

    hovertemplate = (
        f'{bold("%{value}")} slots with {bold("%{customdata[0]}")} blobs '
        f'before a missed block<extra></extra>'
    )
    epochs = (day_limit * 225)
    readable_timeframe = get_epoch_readable_unit(epochs)

    fig = pie_fig_create(
        df, values='slots', names='legend_labels', slices_data='blob_count',
        colors={'color_discrete_map': color_map}, title=title,
        hoverplate=hovertemplate,
        title_annotation=f'Latest {epochs:,.0f} epochs ({readable_timeframe})',
        custom_data=['blob_count'], hole_text='SLOTS'
    )
    title_format(fig, title_dict=dict(title_y=0.97))
    legend_update(
        fig, show_legend=True,
        legend_dict=dict(x=0.5, y=-0.088, title=bold('Blob count'))
    )
    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

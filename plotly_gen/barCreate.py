from utils import updateHoverplate, formatTitle, legendUpdate, addWatermark, boldText
from creates import prefix, createdfApi, createdfCSV, createdfClickhouse
import plotly.express as px
import numpy as np


def barCreate(df, x, y, title, colorsch, thickness, hovertemp, ytitle, xtitle, xskips, yskips):
    fig = px.bar(
        df,
        x = x,
        y = y,
        title = title,
        color_discrete_sequence = [colorsch]
    )

    updateHoverplate(fig, hovertemp)

    fig.update_traces(
        marker_line_width=0,
        width=thickness,
    )

    formatTitle(fig, dict(
            title_text=boldText(title)
        )
    )

    font_info = dict(
        family='Lato',
        color='#4c5773',
        size=12
    )

    tickvals = [x for x in np.arange(0, df[y].max() + 1, yskips)]

    fig.update_yaxes(
        showgrid=True,
        gridcolor='#f9f9f9',
        title_text='<b>' + ytitle + '</b>',
        title_font_color='#4c5773',
        title_font_family='Lato',
        title_font_size=15,
        tickfont=font_info,
        tickvals=tickvals,
        ticktext=[f"<b>{'{:,}'.format(x)}     </b>" for x in tickvals]
    )

    tickvals = df[x] if (not xskips) else [x for x in np.arange(0, df[x].max() + 1, xskips)]

    fig.update_xaxes(
        title_text='<b>' + xtitle + '</b>',
        title_font_color='#4c5773',
        title_font_family='Lato',
        title_font_size=15,
        tickfont=font_info,
        tickvals=tickvals,
        ticktext=[f"<b>{x}</b>" for x in tickvals]
    )

    legendUpdate(fig, False)

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    addWatermark(fig, '/templates/img/migalabsLogo.png', 0.5, 0.5)

    return (fig)


def rttDistCreate(session):
    df = createdfApi(session, prefix + '/all/rtt')

    plotname = 'rtt'

    fig = barCreate(
        df, 'rtt', 'node_count', 'Latency Distribution', '#509ee3', 0.8,
        '<b>RTT:</b> %{x}<br><b>count:</b> %{y}', 'Node count', 'Round Trip Time (RTT)',
        None, 1000
    )

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}


def adAttSnSbsCreate(session):
    df = createdfApi(session, prefix + '/all/att_subnets')

    plotname = 'adver-attest'

    fig = barCreate(
        df, 'att_subnets', 'node_count', 'Advertised Attestation Subnets Subscription', '#88bf4d', 0.7,
        '<b>attnets:</b> %{x}<br><b>count</b>: %{y}', 'Node count', 'Subscribed to Attestation Subnets',
        5, 500
    )

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}


def beaconPerIPCreate(session):
    df = createdfApi(session, prefix + '/all/per_ip')

    plotname = 'node-ip'

    fig = barCreate(
        df, 'nodes', 'ip_count', 'Number of Nodes Per IP', '#f9d45c', 0.7,
        '<b>ips:</b> %{x}<br><b>count</b>: %{y}', 'Node count', 'IPs', 2, 1000
    )

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}


def BlobsBySlotCreate(client):
    plotname = 'blobs-per-slot'

    query = '''
                select slot, count(distinct blob_index) as blob_count
                from default.beacon_api_eth_v1_events_blob_sidecar
                where meta_network_name = 'mainnet'
                group by slot
                order by slot asc
                limit 10
            '''

    df = createdfClickhouse(client, query, 'BlobsBySlot')

    print(df)

    fig = barCreate(
        df, 'slot', 'blob_count', 'Blob count per Slot', '#d9f45d', 0.3,
        '<b>slot:</b> %{x}<br><b>blobs</b>: %{y}', 'Blob count', 'Slot', None, 1
    )

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

from creates import prefix, setBoldLabels, createdfApi, safeFetchEndpoint, createdfPromHTTP, createdfClickhouse, SERVER
from datetime import datetime, timedelta
from utils import addWatermark, updateHoverplate, formatTitle, legendUpdate, getDateSince, getUnixDates, dfFormatUnixTo8601, formatAvg
import plotly.express as px
import numpy as np
import pandas as pd
import plotly.graph_objects as go

end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')


def clampFraction(fraction, clamp=200):
    smaller = int(fraction / clamp) * clamp

    bigger = smaller + clamp

    if ((fraction - smaller) > (bigger - fraction)):
        return (bigger)
    else:
        return (smaller)


def deleteAnnotations(fig):
    for annotation in fig['layout']['annotations']:
        annotation['text'] = ''

# This is what all "line graphs" use at the moment
# However, you might need plotly graph objects to do multi variable graphs
# That are not stacked
# In that case making a lineCreate function is better
def areaCreate(df, x, y, name, color_discrete_map, markers: bool, customdata, color_lines, facet_row = None):
    fig = px.area(
        df,
        x=x,
        y=y,
        color=name if (not color_lines) else None,
        color_discrete_map=color_discrete_map if (not color_lines) else None,
        markers=markers,
        custom_data=[customdata],
        hover_data=[name],
        facet_row=facet_row
    )

    if (color_lines):
        fig.update_traces(
            line=dict(color=color_lines,)
        )

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return (fig)


# Percent formatting
# inv inverses y axis values
def yaxisFormatPercent(fig, inv):
    tickvals = [x for x in np.arange(0, 110, 10)]
    tickvals = tickvals[::-1] if inv else tickvals
    ticktext = [f"<b>{x:.0f}</b>%   " for x in tickvals]

    fig.update_yaxes(
        tickvals=tickvals,
        ticktext=ticktext
    )


def formatWh(x):
    if (x < 1):
        x *= 1000
        return (f'<b>{x:,.2f} mWh</b>   ')

    return (f'<b>{x:,.2f} Wh</b>   ')


def formatWatts(x):
    if (x < 1):
        x *= 1000
        return (f'<b>{x:,.2f} mW</b>   ')

    return (f'<b>{x:,.2f} W</b>   ')


def formatPercent(x):
    return f'<b>{x}%</b>   '


def formatMbps(x):
    if (x < 1000):
        return f'<b>{x:,.0f} Kb/s</b>   '
    return f'<b>{x/1000:,.2f} Mb/s</b>   '


def formatGb(x):
    if (x < 1000):
        return f'<b>{x:,.0f} Mb</b>   '
    return f'<b>{x/1000:,.2f} Gb</b>   '


def formatDefault(x):
    return (f'<b>{x:,.0f}</b>   ')


# Choose text format for y axis
def yaxisFormatAmounts(fig, df, counts, ticktextFormatter, yskips):
    tickvals = [x for x in np.arange(0, df[counts].max(), yskips)]
    ticktext = [ticktextFormatter(x) + '   ' for x in tickvals]

    fig.update_yaxes(
        tickvals=tickvals,
        ticktext=ticktext,
    )


def yaxisCustomize(fig, distance, title, size, inv: bool):
    fig.update_yaxes(
        showgrid=True,
        gridcolor='#f9f9f9',
        title_standoff=distance,
        title_text='<b>' + title + '</b>',
        title_font_color='#4c5773',
        title_font_family='Lato',
        title_font_size=size,
        autorange='reversed' if (inv) else None,
    )


def xaxisCustomize(fig, df, title, start, rate, tickvals = None):
    fig.update_xaxes(
        title_text=title,
        range=[df['timestamp'].min(), df['timestamp'].max()],
        dtick=rate,
        tickvals=tickvals,
        tickformat='<b>%B %d, %Y, %I:%M %p</b>'
    )


# this function was made to reduce boilerplate, that's why it's huge
def areaCustomize(
    fig, df, title, ytitle, hovertemp, legend: bool, percent: bool,
    markers: bool, start_time, inv: bool, filling: bool, name,
    rate='M1', ticktextFormatter=formatDefault, yskips=2000, tickvals=None,
    averages=None
):
    if (legend):
        setBoldLabels(fig)

        legendUpdate(fig, True, dict(
                orientation='v',
                yanchor='top',
                xanchor='left',
                x=1,
                y=1,
                title_text=''
            )
        )
    else:
        legendUpdate(fig, False)

    if (percent):
        yaxisFormatPercent(fig, inv)
    else:
        yaxisFormatAmounts(fig, df, name, ticktextFormatter, yskips)

    yaxisCustomize(fig, 10, ytitle, 15, inv)

    xaxisCustomize(fig, df, '', start_time, rate, tickvals)

    formatTitle(fig, dict(
            title_text='<b>' + title + (''
                if not averages
                else formatAvg(ticktextFormatter, averages)) + '</b>'
        )
    )

    updateHoverplate(fig, hovertemp, dict(namelength=0))

    opacity = ', 0.3)' if (filling) else ', 0)'

    fig.for_each_trace(
        lambda t: t.update(  # setting transparent fillcolor
            fillcolor=t['line']['color'].replace('rgb', 'rgba').replace(')', opacity),
            line=dict(
                width=2
            ),
            marker=(dict(
                line=dict(
                    width=1.5,
                    color=t['line']['color']
                ),
                color='white'
            )) if (markers) else None
        )
    )

    addWatermark(fig, '/templates/img/migalabsLogo.png', 0.5, 0.5)

    deleteAnnotations(fig)

    return (fig)


def getColorKeys():
    return {
        'lighthouse': 'rgb(113, 114, 173)',
        'prysm': 'rgb(136, 191, 77)',
        'teku': 'rgb(239, 140, 140)',
        'nimbus': 'rgb(169, 137, 197)',
        'lodestar': 'rgb(113, 114, 173)',
        'grandine': 'rgb(249, 212, 92)',
        'erigon': 'rgb(80, 158, 227)',
        'unknown': 'rgb(242, 168, 111)'
    }


def clientDiversityEvolutionCreate(session):
    start_time = getDateSince(90)

    markers = False
    # markers = (endpoint == 'validators')

    plotname = 'ev-cli-dist'

    hovertemplate = (
                        '<b>%{fullData.name} (%{y}%)</b>:'
                        '%{customdata[0]}<br>%{x}<extra></extra>'
                    )

    color_keys = getColorKeys()

    df = createdfApi(
        session,
        prefix +
        (
            f'/all/client_diversity/historic?'
            f'start_time={start_time}&end_time={end_time}'
        ),
        ['client_name', 'node_count']
    )

    fig = areaCreate(
        df, 'timestamp', 'percentage', 'client_name', color_keys, markers,
        'node_count', None
    )

    areaCustomize(
        fig, df, 'Client Diversity Evolution', 'Percentage of Nodes',
        hovertemplate, True, True, markers, start_time, True, True, ''
    )

    formatTitle(fig, dict(title_y=0.98))

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}


def activeNodesCreate(session):
    start_time = getDateSince(90)

    markers = False

    hovertemplate = '<b>node count</b>: %{y:,.0f}<br>%{x}<extra></extra>'

    plotname = 'act-nodes'

    df = createdfApi(
        session,
        prefix +
        f'/all/count/historic?start_time={start_time}&end_time={end_time}'
    )

    df = df.sort_values(by='timestamp')

    fig = areaCreate(
        df, 'timestamp', 'node_count', 'node_count', None, markers,
        'node_count', 'rgb(136, 191, 77)'
    )

    areaCustomize(
        fig, df, 'Active Nodes Evolution', 'Active Nodes', hovertemplate,
        False, False, markers, start_time, False, True, 'node_count'
    )

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}


def CpuUsageCreate(session):
    start_time = getDateSince(1)
    dates = getUnixDates(start_time, end_time)
    plotname = 'cpu-usage'

    df = createdfPromHTTP(
        session,
        'query_range?',
        'values',
        {
            'query': (
                f'100 - (avg by (server)(irate(node_cpu_seconds_total'
                f'{{mode="idle",server="{SERVER}"}}[6m])) * 100)'
            ),
            'start': dates[0],
            'end': dates[1],
            'step': 3600
        },
        '%',
        'CPU usage',
        'formatted_values'
    )

    dfFormatUnixTo8601(df)
    df['legend_labels'] = 'CPU'

    hovertemplate = '<b>CPU usage</b>: %{customdata[0]}<br>%{x}<extra></extra>'

    fig = areaCreate(
        df, 'timestamp', 'values', 'legend_labels',
        {'CPU': '#88bf4d'}, True, 'formatted_values',
        'rgb(239, 140, 140)', 'legend_labels'
    )

    areaCustomize(
        fig, df, 'CPU Usage', 'Percentage', hovertemplate, False, True, True,
        start_time, False, True, 'values', '20000000', formatPercent,
        clampFraction(df['values'].max() / 5), None,
        [df['values'].mean().round(3)]
    )

    # Sets the y range from smallest value to largest + 5 (so it looks better)
    # fig.update_yaxes(range=[df['values'].min(), df['values'].max() + 10])

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}


def memoryUsageCreate(session):
    start_time = getDateSince(1)
    dates = getUnixDates(start_time, end_time)
    plotname = 'memory-usage'

    df = createdfPromHTTP(
        session,
        'query_range?',
        'values',
        {
            'query': (
                f'(node_memory_MemTotal_bytes{{server="{SERVER}"}}'
                f' - irate(node_memory_MemAvailable_bytes'
                f'{{server="{SERVER}"}}[6m])) / 1024 / 1024'
            ),
            'start': dates[0],
            'end': dates[1],
            'step': 3600
        },
        'Gb',
        'Memory usage',
        'formatted_values'
    )

    dfFormatUnixTo8601(df)
    df['legend_labels'] = 'Memory'

    hovertemplate = '<b>Memory usage</b>: %{customdata[0]}<br>%{x}<extra></extra>'

    fig = areaCreate(
        df, 'timestamp', 'values', 'legend_labels',
        {'Memory': '#88bf4d'}, False, 'formatted_values', 'rgb(169, 137, 197)',
        'legend_labels'
    )
    areaCustomize(
        fig, df, 'Memory Usage', 'Memory', hovertemplate, False, False, False,
        start_time, False, True, 'values', '20000000', formatGb,
        10000, None, [df['values'].mean().round(3)]
    )

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}


def networkBandwidthInOutCreate(session):
    start_time = getDateSince(1)
    dates = getUnixDates(start_time, end_time)
    plotname = 'network-in-out'

    df_in = createdfPromHTTP(
        session,
        'query_range?',
        'values',
        {
            'query': (
                f'irate(node_network_receive_bytes_total'
                f'{{server="{SERVER}", device="enp89s0"}}[6m]) / 1024'
            ),
            'start': dates[0],
            'end': dates[1],
            'step': 3600
        },
        'Mbps',
        'Network In',
        'formatted_values'
    )

    df_out = createdfPromHTTP(
        session,
        'query_range?',
        'values',
        {
            'query': (
                f'irate(node_network_transmit_bytes_total'
                f'{{server="{SERVER}", device="enp89s0"}}[6m]) / 1024'
            ),
            'start': dates[0],
            'end': dates[1],
            'step': 3600
        },
        'Mbps',
        'Network Out',
        'formatted_values'
    )

    dfFormatUnixTo8601(df_in)
    dfFormatUnixTo8601(df_out)
    df_in['legend_labels'] = '<b>Bandwidth In</b>'
    df_out['legend_labels'] = '<b>Bandwidth Out</b>'

    averages = [df_in['values'].mean().round(3), df_out['values'].mean().round(3)]

    df = pd.concat([df_in, df_out])

    hovertemplate = '<b>Rate</b>: %{customdata[0]}<br><b>%{x}</b><extra></extra>'

    fig = areaCreate(df, 'timestamp', 'values', 'legend_labels',
        {
            '<b>Bandwidth In</b>': 'rgb(113, 114, 173)',
            '<b>Bandwidth Out</b>': 'rgb(80, 158, 227)'
        },
        True, 'formatted_values', None, 'legend_labels')

    areaCustomize(
        fig, df, 'Network Bandwidth In/Out', 'Rate', hovertemplate, True,
        False, True, start_time, False, True, 'values', '20000000',
        formatMbps, clampFraction(df['values'].max() / 5), None, averages
    )

    fig.update_yaxes(range=[df['values'].min(), df['values'].max()])

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}


def nearest(min, max, value):
    if ((value - min) > (max - value)):
        return (max)
    return (min)


def FilesystemReadWriteCreate(session):
    start_time = getDateSince(1)
    dates = getUnixDates(start_time, end_time)
    plotname = 'file-rw'

    df_read = createdfPromHTTP(
        session,
        'query_range?',
        'values',
        {
            'query': (
                f'(irate(node_disk_read_bytes_total{{server="{SERVER}"'
                f', device="nvme0n1"}}[6m]) / 1024)'
            ),
            'start': dates[0],
            'end': dates[1],
            'step': 3600
        },
        'Mbps',
        'Filesystem Read Ratio',
        'formatted_values'
    )

    df_write = createdfPromHTTP(
        session,
        'query_range?',
        'values',
        {
            'query': (
                f'(irate(node_disk_written_bytes_total{{server="{SERVER}"'
                f', device="nvme0n1"}}[6m]) / 1024)'
            ),
            'start': dates[0],
            'end': dates[1],
            'step': 3600
        },
        'Mbps',
        'Filesystem Write Ratio',
        'formatted_values'
    )

    dfFormatUnixTo8601(df_read)
    dfFormatUnixTo8601(df_write)
    df_read['legend_labels'] = '<b>Read</b>'
    df_write['legend_labels'] = '<b>Write</b>'

    averages = [df_read['values'].mean().round(3), df_write['values'].mean().round(3)]

    df = pd.concat([df_read, df_write])

    hovertemplate = '<b>Rate</b>: %{customdata[0]}<br><b>%{x}</b><extra></extra>'

    fig = areaCreate(df, 'timestamp', 'values', 'legend_labels',
        {
            '<b>Read</b>': 'rgb(242, 168, 111)',
            '<b>Write</b>': 'rgb(136, 191, 77)'
        },
        True, 'formatted_values', None, 'legend_labels')

    areaCustomize(
        fig, df, 'File System Read/Write Ratio', 'Rate', hovertemplate, True,
        False, True, start_time, False, True, 'values', '20000000',
        formatMbps, clampFraction(df['values'].max() / 5), None, averages
    )

    fig.update_yaxes(range=[df['values'].min(), df['values'].max()])

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}


def PowerConsumptionCreate(session):
    start_time = getDateSince(1)
    dates = getUnixDates(start_time, end_time)
    plotname = 'power-usage'

    df = createdfPromHTTP(
        session,
        'query_range?',
        'values',
        {
            'query': f'(rate(mystrom_power{{server="{SERVER}"}}[6m]))',
            'start': dates[0],
            'end': dates[1],
            'step': 3600
        },
        'W',
        'Power Consumption',
        'formatted_values'
    )

    dfFormatUnixTo8601(df)
    df['legend_labels'] = 'Power'

    averages = [df['values'].mean().round(3)]

    hovertemplate = '<b>Consumption</b>: %{customdata[0]}<br>%{x}<extra></extra>'

    fig = areaCreate(
        df, 'timestamp', 'values', 'legend_labels',
        {'Power Consumption': '#88bf4d'}, False, 'formatted_values',
        'rgb(249, 212, 92)', 'legend_labels'
    )

    areaCustomize(
        fig, df, 'Power Consumption', 'Power', hovertemplate, False, False,
        True, start_time, False, True, 'values', '20000000', formatWatts,
        clampFraction(df['values'].max() / 5, 5), None, averages
    )

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}


def EnergyConsumptionCreate(session):
    start_time = getDateSince(1)
    dates = getUnixDates(start_time, end_time)
    plotname = 'energy-usage'

    df = createdfPromHTTP(
        session,
        'query_range?',
        'values',
        {
            'query': f'avg_over_time(mystrom_power{{server="{SERVER}"}}[1h])',
            'start': dates[0],
            'end': dates[1],
            'step': 3600
        },
        'Wh',
        'Energy Consumption',
        'formatted_values'
    )

    dfFormatUnixTo8601(df)
    df['legend_labels'] = 'Energy'

    averages = [df['values'].mean().round(3)]

    hovertemplate = '<b>Consumption</b>: %{customdata[0]}<br>%{x}<extra></extra>'

    fig = areaCreate(
        df, 'timestamp', 'values', 'legend_labels',
        {'Energy Consumption': '#88bf4d'}, False, 'formatted_values',
        'rgb(80, 158, 227)', 'legend_labels'
    )

    areaCustomize(
        fig, df, 'Energy Consumption', 'Watts per hour', hovertemplate,
        False, False, True, start_time, False, True, 'values', '20000000',
        formatWh, clampFraction(df['values'].max() / 5, 5), None, averages
    )

    plot_div = fig.to_html(full_html=False, include_plotlyjs=False)

    return {plotname: plot_div}

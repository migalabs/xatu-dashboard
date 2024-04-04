from   creates        import prefix, setBoldLabels, createdfApi, createdfPromHTTP, SERVER
from   datetime       import datetime, timedelta
from   utils          import addWatermark, updateHoverplate, formatTitle, legendUpdate, getUnixDates, getDateSince, dfFormatUnixTo8601, formatAvg
from   areaCreate       import yaxisCustomize, xaxisCustomize, yaxisFormatAmounts, formatMbps
import plotly.express       as px
import plotly.graph_objects as go
import numpy                as np
import pandas               as pd

end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

def formatWh(x):
    if (x < 1):
        x *= 1000
        return(f'<b>{x:,.2f} mWh</b>   ')

    return (f'<b>{x:,.2f} Wh</b>   ')

def formatWatts(x):
    if (x < 1):
        x *= 1000
        return(f'<b>{x:,.2f} mW</b>   ')

    return (f'<b>{x:,.2f} W</b>   ')

def histogramCreate(df, x, y, title, ytitle, name, color_sequence, customdata, hovertemplate, nbins, yFormatter, yskips, legend = False, opacity = 0.45):
    fig = px.histogram(
        df,
        x = x,
        y = y,
        title = title,
        color = name,
        color_discrete_sequence = color_sequence,
        nbins = nbins,
        histfunc = 'avg'
    )

    if (legend == True):
        setBoldLabels(fig)

        legendUpdate(fig, True,
            dict(
                orientation = 'v',
                yanchor = 'top',
                xanchor = 'left',
                x = 1,
                y = 1,
                title_text = '',
            )
        )
    else:
        legendUpdate(fig, False)

    fig.update_layout(
        bargap = 0.1
    )

    yaxisFormatAmounts(fig, df, y, yFormatter, yskips)

    yaxisCustomize(fig, 10, ytitle, 15, False)

    xaxisCustomize(fig, df, '', getDateSince(1), 6000000)

    formatTitle(fig,
        dict(
            title_text = '<b>' + title + '</b>   (   Avg. ' + yFormatter(df['values'].mean().round(3)) + ')',
        )
    )

    fig.update_layout(
        plot_bgcolor = 'white',
        paper_bgcolor = 'white',
        barmode = 'overlay'
    )

    fig.update_traces(
        customdata = [customdata],
        selector = dict(type = 'histogram'),
        opacity = opacity
    )

    updateHoverplate(fig, hovertemplate,
        dict(
            namelength = 0
        )
    )

    addWatermark(fig, '/templates/img/migalabsLogo.png', 0.5, 0.5)

    return (fig)

color_sequence = {
    '#f9d45c', '#88bf4d'
}

def PowerConsumptionCreate(session):
    plotname = 'power-usage'
    start_time = getDateSince(1)
    dates = getUnixDates(start_time, end_time)

    df = createdfPromHTTP(
        session,
        'query_range?',
        'values',
        {
            'query': f'(irate(mystrom_power{{server="{SERVER}"}}[6m]))',
            'start': dates[0],
            'end': dates[1],
            'step': 3600
        },
        'W',
        'Power Consumption',
        'formatted_values'
    )

    dfFormatUnixTo8601(df)
    df['legend_labels'] = '<b>Power</b>'

    hovertemplate = '<b>Consumption</b>: %{y} W<br>%{x}<extra></extra>'

    fig = histogramCreate(df, 'timestamp', 'values', 'Power Consumption',
        'Usage', 'legend_labels', ['rgb(239, 140, 140)'],
        'formatted_values', hovertemplate, 48, formatWatts, 5, False, 0.6)

    plot_div = fig.to_html(full_html = False, include_plotlyjs = False)

    return { plotname: plot_div }


def EnergyConsumptionCreate(session):
    plotname = 'energy-usage'
    start_time = getDateSince(1)
    dates = getUnixDates(start_time, end_time)

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
        'W',
        'Energy Consumption',
        'formatted_values'
    )

    dfFormatUnixTo8601(df)
    df['legend_labels'] = '<b>Energy</b>'

    hovertemplate = '<b>Consumption</b>: %{y} Wh<br>%{x}<extra></extra>'

    fig = histogramCreate(df, 'timestamp', 'values', 'Energy Consumption',
        'Usage', 'legend_labels', ['rgb(80, 158, 227)'],
        'formatted_values', hovertemplate, 48, formatWh, 5, False, 0.6)

    plot_div = fig.to_html(full_html = False, include_plotlyjs = False)

    return { plotname: plot_div }

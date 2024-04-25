import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from creates import bold_labels_set
from datetime import datetime
from export import ABS_PATH
from utils import (
    watermark_add, title_format, legend_update, get_avg_str,
    hoverplate_update, bold
)

end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')


def fraction_clamp(fraction, clamp=200):
    smaller = int(fraction / clamp) * clamp

    bigger = smaller + clamp

    if ((fraction - smaller) > (bigger - fraction)):
        return (bigger)
    else:
        return (smaller)


def annotations_delete(fig):
    for annotation in fig['layout']['annotations']:
        annotation['text'] = ''


# Used for most "line graphs" but is actually an area graph
def area_fig_create(
    df, x, y, name, color_discrete_map, markers: bool, customdata, color_lines,
    facet_row=None  # column that separates the data for stacked plots
):
    fig = px.area(
        df,
        x=x,
        y=y,
        color=name if (not color_lines) else None,
        color_discrete_map=color_discrete_map if (not color_lines) else None,
        markers=markers,
        custom_data=[customdata] if (customdata) else None,
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
def yaxis_format_percent(fig, inv):
    tickvals = [x for x in np.arange(0, 110, 10)]
    tickvals = tickvals[::-1] if inv else tickvals
    ticktext = [f"<b>{x:.0f}</b>%   " for x in tickvals]

    fig.update_yaxes(
        tickvals=tickvals,
        ticktext=ticktext
    )


# Choose text format for y axis
def yaxis_format_amounts(fig, df, counts, tick_text_formatter, yskips):
    tickvals = [x for x in np.arange(0, df[counts].max(), yskips)]
    ticktext = [tick_text_formatter(x) + '   ' for x in tickvals]

    fig.update_yaxes(
        tickvals=tickvals,
        ticktext=ticktext,
    )


# this function was made to reduce boilerplate, that's why it's huge
def area_customize(
    fig, df, title, ytitle, xtitle, hovertemplate, legend: bool, percent: bool,
    markers: bool, start_time: str, inv: bool, filling: bool, xrange,
    name, rate='M1',
    tick_text_formatter=lambda x: bold(f'{x:,.0f}'),
    yskips=2000,
    tickvals=None, xtickformat=bold('%B %d, %Y, %I:%M %p'),
    xticktext=None, averages=None, tickdiv=None
):
    if (legend):
        bold_labels_set(fig)

        legend_update(fig, True, dict(
                orientation='v',
                yanchor='top',
                xanchor='left',
                x=1,
                y=1,
                title_text=''
            )
        )
    else:
        legend_update(fig, False)

    if (percent):
        yaxis_format_percent(fig, inv)
    else:
        yaxis_format_amounts(fig, df, name, tick_text_formatter, yskips)

    fig.update_yaxes(
        showgrid=True,
        gridcolor='#f9f9f9',
        title_standoff=10,
        title_text=bold(ytitle),
        title_font_color='#4c5773',
        title_font_family='Lato',
        title_font_size=15,
        autorange='reversed' if (inv) else None,
    )

    fig.update_xaxes(
        title_text=bold(xtitle),
        title_standoff=10,
        title_font_size=15,
        range=xrange,
        dtick=rate,
        tick0=0.1,
        tickvals=tickvals,
        tickformat=xtickformat,
        ticktext=xticktext if (xticktext) else None
    )

    title_format(
        fig, dict(
            title_text=bold(title + (
                    '' if not averages
                    else get_avg_str(tick_text_formatter, averages)
                )
            )
        )
    )

    hoverplate_update(fig, hovertemplate, dict(namelength=0))

    opacity = ', 0.3)' if (filling) else ', 0)'

    fig.for_each_trace(
        lambda t: t.update(  # setting transparent fillcolor
            fillcolor=t['line']['color'].replace('rgb', 'rgba').replace(')', opacity),
            line=dict(width=2),
            marker=(dict(
                line=dict(
                    width=1.5,
                    color=t['line']['color']
                ),
                color='white'
            )) if (markers) else None
        )
    )

    watermark_add(
        fig, file=(f'{ABS_PATH}/assets/migalabsLogo.png'), x=0.5, y=0.5
    )

    annotations_delete(fig)

    return (fig)

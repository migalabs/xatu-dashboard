from typing import Callable, Union, Any, Optional
from utils import (
    watermark_add, title_format, legend_update, get_avg_str,
    hoverplate_update, bold, fraction_clamp, annotations_delete
)
from creates import bold_labels_set
from datetime import datetime
from export import ABS_PATH
import plotly.express as px
import pandas as pd
import numpy as np

end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
DEFAULT_DATE_FORMAT = bold('%B %d, %Y, %I:%M %p')
ONE_DAY_RATE = '86400000'
FIVE_DAYS_RATE = '432000000'
TEN_DAYS_RATE = '864000000'
MONTH_RATE = 'M1'


def set_area_filling(fig, markers: bool, filled: bool):
    opac = ', 0.3)' if (filled) else ', 0)'
    fig.for_each_trace(lambda t: t.update(  # setting transparent fillcolor
        fillcolor=t['line']['color'].replace('rgb', 'rgba').replace(')', opac),
        line=dict(width=2),
        marker=(
            dict(line=dict(
                width=1.5, color=t['line']['color']), color='white')
            ) if (markers) else None
        )
    )


# Used for most "line graphs" but is actually an area graph
def area_create_fig(
    df, x, y, name, color_discrete_map, markers: bool, customdata, color_lines,
    facet_row=None, log_y: bool = False, filled: bool = True
    # facet_row: column that separates the data for stacked plots
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
        facet_row=facet_row,
        log_y=log_y
    )
    if (color_lines):
        fig.update_traces(line=dict(color=color_lines))
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    fig.update_yaxes(gridcolor='#f3f3f3', linewidth=5)
    set_area_filling(fig, markers, filled)
    return (fig)


def format_y_axis(
    df, fig, y_col_title: tuple, yskips: Optional[float],
    ytickformat: Union[Callable, str],
    yrange: Optional[list[int]] = None,
):
    tickvals = []
    if (isinstance(yskips, int)):
        tickvals = [y for y in np.arange(0, df[y_col_title[0]].max() + yskips, yskips)]
        fig.update_yaxes(tickvals=tickvals)
    if (callable(ytickformat)):
        ticktext = [ytickformat(y) for y in tickvals]
        fig.update_yaxes(
            tickmode='array', tickvals=tickvals, ticktext=ticktext)
    else:
        fig.update_yaxes(tickformat=ytickformat)

    fig.update_yaxes(
        showgrid=True,
        title_standoff=10,
        title_text=bold(y_col_title[1]),
        title_font_color='#4c5773',
        title_font_family='Lato',
        title_font_size=15,
        range=yrange
    )


def format_x_axis(
    df, fig, x_col_title: tuple, xskips: Optional[Union[float, str]],
    xtickformat: Union[Callable, str],
    xrange: Optional[list[int]] = None
):
    tickvals = []
    if (isinstance(xskips, int)):
        tickvals = [x for x in np.arange(0, len(df[x_col_title[0]]), xskips)]
        fig.update_xaxes(tickvals=tickvals)
    if (callable(xtickformat)):
        ticktext = [xtickformat(df[x_col_title[0]].iloc[x]) for x in tickvals]
        fig.update_xaxes(tickmode='array', ticktext=ticktext)
    else:
        fig.update_xaxes(tickformat=xtickformat)

    fig.update_xaxes(
        showgrid=True,
        title_standoff=10,
        title_text=bold(x_col_title[1]),
        title_font_color='#4c5773',
        title_font_family='Lato',
        title_font_size=15,
        range=xrange,
        dtick=xskips if (isinstance(xskips, str)) else None
    )


def set_default_legend_style(fig):
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


# Add more (important) attributes to the plot
# If any of the tickformat parameters is a function,
# It will apply it to all ticks with [skips] spacing.
# Otherwise, will apply the string tickformat for plotly
# and will use rate for the spacing/rate instead of xskips
def area_customize(
    df, fig, title, x_col_title: tuple, y_col_title: tuple,
    hovertemplate: str, xskips: Union[float, str], yskips: float,
    show_legend: bool = False,
    xtickformat: Union[Callable, str] = lambda x: bold(f'{x:,.0f}'),
    xrange: Optional[list[int]] = None,
    ytickformat: Union[Callable, str] = lambda y: bold(f'{y:,.0f}'),
    yrange: Optional[list[int]] = None,
    title_annotation: str = ''
):
    if (show_legend):
        set_default_legend_style(fig)
    else:
        legend_update(fig, False)
    format_y_axis(df, fig, y_col_title, yskips, ytickformat, yrange)
    format_x_axis(df, fig, x_col_title, xskips, xtickformat, xrange)

    if (title_annotation):
        title = bold(title) + "    -   " + title_annotation
    title_format(fig, dict(title_text=title))
    hoverplate_update(fig, hovertemplate, dict(namelength=0))
    watermark_add(
        fig, file=(f'{ABS_PATH}/assets/migalabsLogo.png'), x=0.5, y=0.5)
    annotations_delete(fig)
    return (fig)

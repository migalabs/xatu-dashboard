from typing import Callable, Union, Any, Optional
from utils import (
    watermark_add, title_format, legend_update,
    hoverplate_update, bold, annotations_delete,
    set_default_legend_style
)
from axis_tools import (
    format_y_axis, format_x_axis,
    DEFAULT_DATE_FORMAT, FIVE_DAYS_RATE
)
from datetime import datetime
from export import ABS_PATH
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')


# Set area filling with custom opacity. If not filled, opacity is changed to 0.
def set_area_filling(fig: go.Figure, markers: bool, fill: bool):
    opac = ', 0.3)' if (fill) else ', 0)'

    fig.for_each_trace(lambda t: t.update(  # For each line,
        fillcolor=t['line']['color'].replace('rgb', 'rgba').replace(')', opac),
        line=dict(width=2),  # Set thickness of the line
        marker=(  # Customizing the markers
            dict(line=dict(
                width=1.5, color=t['line']['color']), color='white')
            ) if (markers) else None
        )
    )


# Used as a "line graph" but it's actually a stacked area plot
# Creates barebones area fig
# facet_row: column that separates the data for stacked plots
def area_create_fig(
    df: pd.DataFrame,
    x: str, y: str, color: str,
    color_discrete_map: dict, markers: bool, customdata: str,
    line_color: str, facet_row: str = '', log_y: bool = False,
    fill: bool = True, margin: int = 15
) -> go.Figure:
    fig = px.area(
        df,
        x=x,
        y=y,
        color=color if (not line_color) else None,
        color_discrete_map=color_discrete_map if (not line_color) else None,
        markers=markers,
        custom_data=[customdata] if (customdata) else None,
        hover_data=[color],
        # something
        facet_row=facet_row if (facet_row) else None,
        log_y=log_y
    )
    if (line_color):
        fig.update_traces(line=dict(color=line_color))
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    fig.update_yaxes(gridcolor='#f3f3f3', linewidth=5)
    set_area_filling(fig, markers, fill)
    fig.update_layout(margin_pad=margin)
    return (fig)


# Add more (important) attributes to the plot
# If any of the tickformat parameters is a function,
# It will apply it to all ticks with [skips] spacing.
# Otherwise, will apply the string tickformat for plotly
# and will use rate for the spacing/rate instead of xskips
def area_customize(
    df: pd.DataFrame, fig: go.Figure, title: str,
    x_axis_info: tuple, y_axis_info: tuple,
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
    format_y_axis(df, fig, y_axis_info, yskips, ytickformat, yrange)
    format_x_axis(df, fig, x_axis_info, xskips, xtickformat, xrange)

    if (title_annotation):
        title = bold(title) + "    -   " + title_annotation
    title_format(fig, dict(title_text=title))
    hoverplate_update(fig, hovertemplate, dict(namelength=0))
    watermark_add(
        fig, file=(f'{ABS_PATH}/assets/migalabsLogo.png'), x=0.5, y=0.5)
    annotations_delete(fig)
    return (fig)

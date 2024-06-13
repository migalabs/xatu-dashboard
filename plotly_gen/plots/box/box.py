import plotly.express as px
import numpy as np
from export import ABS_PATH
from axis_tools import format_y_axis, format_x_axis
from utils import (
    hoverplate_update, title_format,
    legend_update, watermark_add, bold
)


def box_create_fig(
    df,  title,
    x_axis_info: tuple,
    y_axis_info: tuple, color_discrete_map: list[str],
    thickness: float, hovertemplate: str,
    xskips: float, yskips: float, color=None, quartilemethod=None,
    points: str = '', notched: bool = False, boxmode: str = 'group',
    xtickformat=lambda x: bold(f'{x:,.0f}'),
    ytickformat=lambda y: bold(f'{y:,.0f}'),
    yrange: list[float] = None, xrange: list[float] = None,
    #  quartilemethod = "exclusive", "inclusive" or "linear",
    title_annotation=None, ytick_text_formatter=lambda y: bold(f'{y:,.0f}'),
    margin: int = 15
):
    fig = px.box(
        df,
        x=x_axis_info[0],
        y=y_axis_info[0],
        points=points,
        title=title,
        color=color,
        notched=notched,
        # color_discrete_sequence=color_discrete_sequence,
        color_discrete_map=color_discrete_map,
        boxmode=boxmode
    )

    hoverplate_update(fig, hovertemplate)

    fig.update_traces(marker_line_width=0, width=thickness)

    if (title_annotation):
        title = bold(title) + "    -   " + title_annotation

    title_format(fig, dict(title_text=title))

    font_info = dict(
        family='Lato',
        color='#4c5773',
        size=12
    )
    format_y_axis(df, fig, y_axis_info, yskips, ytickformat, yrange)
    format_x_axis(df, fig, x_axis_info, xskips, xtickformat, xrange)

    legend_update(fig, False)

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    fig.update_traces(quartilemethod=quartilemethod)
    fig.update_yaxes(gridcolor='#f3f3f3', linewidth=2)
    # for trace in fig.data:
    #     trace.marker = dict(outliercolor=trace.marker.line.color)
    watermark_add(fig, file=(f'{ABS_PATH}/assets/migalabsLogo.png'), x=0.5, y=0.5)
    fig.update_layout(margin_pad=margin)
    return (fig)

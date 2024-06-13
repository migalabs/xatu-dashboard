import plotly.express as px
from export import ABS_PATH
import plotly.graph_objects as go
from typing import Callable, Union, Optional
from utils import (
    hoverplate_update, title_format,
    legend_update, watermark_add, bold,
    set_default_legend_style
)
from plots.area.area import (format_y_axis, format_x_axis)


def scatter_create_fig(
    df, title,
    x_axis_info: tuple, y_axis_info: tuple,
    color_discrete_sequence, hovertemplate,
    xskips, yskips, color=None,
    size: str = '', symbol: str = '', trendline: str = '',
    marginal_x: str = '', marginal_y: str = '',
    show_legend: bool = True, title_annotation=None,
    xtickformat: Union[Callable, str] = lambda x: bold(f'{x:,.0f}'),
    xrange: Optional[list[int]] = None,
    ytickformat: Union[Callable, str] = lambda y: bold(f'{y:,.0f}'),
    yrange: Optional[list[int]] = None,
    customdata=[], margin: int = 15
):
    fig = px.scatter(
        df,
        x=x_axis_info[0],
        y=y_axis_info[0],
        size=size if (size) else None,
        title=title,
        color=color,
        color_discrete_sequence=color_discrete_sequence,
        marginal_x=marginal_x,
        marginal_y=marginal_y,
        trendline=trendline if (trendline) else None,
        custom_data=customdata
    )
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
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    fig.update_yaxes(gridcolor='#f3f3f3', linewidth=2)

    watermark_add(
        fig,
        file=(f'{ABS_PATH}/assets/migalabsLogo.png'),
        x=0.5, y=0.5
    )
    fig.update_layout(margin_pad=margin)
    return (fig)

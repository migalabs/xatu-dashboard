import plotly.express as px
from utils import set_default_legend_style
from export import ABS_PATH
from utils import (
    hoverplate_update, title_format,
    legend_update, watermark_add, bold
)
from axis_tools import format_y_axis, format_x_axis


def bar_create_fig(
    df, title,
    x_axis_info: tuple, y_axis_info: tuple,
    color_discrete_sequence: list[str], thickness, hovertemplate,
    xskips: float, yskips: float, title_annotation=None, color=None,
    show_legend: bool = False, customdata: list[str] = [],
    barmode: str = 'overlay', margin: int = 15,
    y_formatter=lambda y: bold(f"{y:,.0f}"),
    x_formatter=lambda x: bold(f"{x}")
):
    x, y = x_axis_info[0], y_axis_info[0]
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
        color_discrete_sequence=color_discrete_sequence,
        custom_data=customdata,
        barmode=barmode
    )

    hoverplate_update(fig, hovertemplate)

    fig.update_traces(
        marker_line_width=0,
        width=thickness,
    )

    if (title_annotation):
        title = bold(title) + "    -   " + title_annotation

    title_format(fig, dict(title_text=title))

    font_info = dict(
        family='Lato',
        color='#4c5773',
        size=12
    )

    format_y_axis(df, fig, y_axis_info, yskips, y_formatter)
    format_x_axis(df, fig, x_axis_info, xskips, x_formatter)

    if (show_legend):
        set_default_legend_style(fig)
    else:
        legend_update(fig, False)

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    watermark_add(
        fig, file=(f'{ABS_PATH}/assets/migalabsLogo.png'), x=0.5, y=0.5
    )
    fig.update_layout(margin_pad=margin)
    return (fig)

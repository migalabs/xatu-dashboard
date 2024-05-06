import plotly.express as px
import numpy as np
from export import ABS_PATH
from utils import (
    hoverplate_update, title_format,
    legend_update, watermark_add, bold
)


def bar_create_fig(
    df, x, y, title, color_discrete_sequence, thickness, hovertemplate,
    ytitle, xtitle, xskips, yskips, title_annotation=None
):
    fig = px.bar(
        df,
        x=x,
        y=y,
        title=title,
        color_discrete_sequence=[color_discrete_sequence]
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

    tickvals = [x for x in np.arange(0, df[y].max() + 1, yskips)]

    fig.update_yaxes(
        title_text=bold(ytitle),
        title_font_color='#4c5773',
        title_font_family='Lato',
        gridcolor='#f9f9f9',
        showgrid=True,
        title_font_size=15,
        tickfont=font_info,
        tickvals=tickvals,
        ticktext=[f"<b>{'{:,}'.format(x)}     </b>" for x in tickvals]
    )

    tickvals = df[x] if (not xskips) else [x for x in np.arange(df[x].min(), df[x].max() + 1, xskips)]

    fig.update_xaxes(
        title_text=bold(xtitle),
        title_font_color='#4c5773',
        title_font_family='Lato',
        title_font_size=15,
        tickfont=font_info,
        tickvals=tickvals,
        ticktext=[f'{bold(f"{x}")}' for x in tickvals]
    )

    legend_update(fig, False)

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    watermark_add(
        fig, file=(f'{ABS_PATH}/assets/migalabsLogo.png'), x=0.5, y=0.5
    )

    return (fig)

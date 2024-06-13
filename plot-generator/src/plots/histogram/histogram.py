import pandas as pd
import plotly.express as px
from typing import (Optional, Callable, Union)
from utils import bold_labels_set
from datetime import datetime
from export import ABS_PATH
from axis_tools import format_y_axis, format_x_axis
from utils import (
    date_since, watermark_add, hoverplate_update, title_format,
    legend_update, bold
)

end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')


def histogram_create_fig(
    df: pd.DataFrame, title: str,
    x_axis_info: tuple, y_axis_info: tuple,
    color: str, color_sequence: list[str], customdata: list[str],
    hovertemplate, nbins,
    yskips: float, xskips: Union[float, str] = 1,
    show_legend: bool = False, barmode='group',
    xtickformat: Union[Callable, str] = lambda x: bold(f'{x:,.0f}'),
    xrange: Optional[list[int]] = None,
    ytickformat: Union[Callable, str] = lambda y: bold(f'{y:,.0f}'),
    yrange: Optional[list[int]] = None,
    opacity: float = 0.45
):
    fig = px.histogram(
        df,
        x=x_axis_info[0],
        y=y_axis_info[0],
        title=title,
        color=color,
        color_discrete_sequence=color_sequence,
        nbins=nbins,
        histfunc='avg',
        barmode=barmode,
    )

    if (show_legend):
        bold_labels_set(fig)

        legend_update(
            fig, True, dict(
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

    fig.update_layout(bargap=0.1)

    format_y_axis(df, fig, y_axis_info, yskips, ytickformat, yrange)
    format_x_axis(df, fig, x_axis_info, xskips, xtickformat, xrange)

    title_format(fig, dict(title_text=bold(title)))

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        barmode='overlay'
    )

    fig.update_traces(
        customdata=[customdata],
        selector=dict(type='histogram'),
        opacity=opacity
    )

    hoverplate_update(fig, hovertemplate, dict(namelength=0))

    watermark_add(fig, f'{ABS_PATH}/assets/migalabsLogo.png', 0.5, 0.5)

    return (fig)

from typing import Callable, Union, Optional
from utils import bold
import numpy as np

DEFAULT_DATE_FORMAT = bold('%B %d, %Y, %I:%M %p')
ONE_DAY_RATE = '86400000'
FIVE_DAYS_RATE = '432000000'
TEN_DAYS_RATE = '864000000'
MONTH_RATE = 'M1'


# At the moment, this only works with y axis that only contain numbers
def format_y_axis(
    df, fig, y_axis_info: tuple, yskips: Optional[float],
    ytickformat: Union[Callable, str],
    yrange: Optional[list[int]] = None,
):
    tickvals = []
    # if the y skips are present, use them to create the tickvals
    if (isinstance(yskips, float) or isinstance(yskips, int)):
        tickvals = [y for y in np.arange(0, df[y_axis_info[0]].max() + yskips, yskips)]
        fig.update_yaxes(tickvals=tickvals)
    if (callable(ytickformat)):  # if ytickformat is a formatter function...
        ticktext = [ytickformat(y) for y in tickvals]
        fig.update_yaxes(
            tickmode='array', tickvals=tickvals, ticktext=ticktext)
    else:  # if ytickformat is a string, use plotly's tickformatting
        fig.update_yaxes(tickformat=ytickformat)

    fig.update_yaxes(
        showgrid=True,
        title_standoff=35,
        title_text=bold(y_axis_info[1]),
        title_font_color='#4c5773',
        title_font_family='Lato',
        title_font_size=15,
        tickfont=dict(color='#4c5773'),
        range=yrange
    )


# For formatting numbers e.g. ",.0f", use plotly's formatting.
# Custom ticktext formatting fails in this case.
def format_x_axis(
    df, fig, x_axis_info: tuple, xskips: Optional[Union[float, str]],
    xtickformat: Union[Callable, str],
    xrange: Optional[list[int]] = None
):
    tickvals = []
    # if the x skips are present, use them to create the tickvals
    if (isinstance(xskips, float) or isinstance(xskips, int)):
        tickvals = [x for x in np.arange(0, len(df[x_axis_info[0]]), int(xskips))]
        fig.update_xaxes(tickvals=tickvals)
    if (callable(xtickformat)):  # if xtickformat is a formatter function...
        ticktext = [xtickformat(df[x_axis_info[0]].iloc[x]) for x in tickvals]
        fig.update_xaxes(tickmode='array', ticktext=ticktext)
    else:  # if xtickformat is a string, use plotly's tickformatting
        fig.update_xaxes(tickformat=xtickformat)

    fig.update_xaxes(
        showgrid=True,
        title_standoff=35,
        title_text=bold(x_axis_info[1]),
        title_font_color='#4c5773',
        title_font_family='Lato',
        title_font_size=15,
        tickfont=dict(color='#4c5773'),
        automargin=True,
        range=xrange,
        # ticks="outside",
        # tickcolor='white',
        # ticklen=10,
        # In case xskips is not a number, use Plotly's string dtick
        # For example, if the values are dates, you can use the
        # FIVE_DAYS_RATE Constant.
        dtick=xskips if (isinstance(xskips, str)) else None
    )

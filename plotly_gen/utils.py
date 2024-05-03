import sys
import time
import pandas as pd
import numpy as np
from PIL import Image
from datetime import datetime, timedelta

annotation_format_default = {
    'font_family': 'Lato',
    'showarrow': False,
    'font_color': '#4c5773',
    'font_size': 25,
    'x': 0.5,
    'y': 0.5
}

title_format_default = {
    'font_family': 'Lato',
    'font_color': '#4c5773',

    'title_font_family': 'Lato',
    'title_font_color': '#4c5773',
    'title_font_size': 25,
    'title_x': 0.04999,
    'title_y': 0.95
}

legend_font_format_default = {
    'bgcolor': 'rgba(0, 0, 0, 0)',
    'font': {
        'size': 16,
        'family': 'Lato',
        'color': '#4c5773'
    }
}

hoverlabel_default = {
    'bgcolor': 'rgba(255, 255, 255, 0.7)',
    'font_color': 'rgba(72, 72, 72, 0.7)'
}


# This and the group of functions related to plots in this file just
# grab a default value (from above) as starting point unless you overwrite
# by specifying in the parameters (dict)
# This is just to make a default style and will help making new plots
# fit with others visually
def annotations_add(
    fig, annotations: list[dict], format: dict = annotation_format_default
):
    formats = [format.copy() for _ in annotations]

    for annotation, formatItem in zip(annotations, formats):
        formatItem.update(annotation)

    fig.update_layout(
        annotations=formats
    )


def hoverplate_update(fig, hovertemplate, hoverlabel: dict = hoverlabel_default):
    hoverlabel_def = hoverlabel_default.copy()
    hoverlabel_def.update(hoverlabel)

    fig.update_traces(
        hoverlabel=hoverlabel_def,
        hovertemplate=hovertemplate
    )


def title_format(fig, title_dict: dict, format: dict = title_format_default):
    format = format.copy()
    format.update(title_dict)

    fig.update_layout(format)


def legend_update(
    fig, show_legend: bool, legend_dict: dict = {},
    font_format: dict = legend_font_format_default
):
    if (not show_legend):
        fig.update_traces(showlegend=show_legend)
        return

    legend_dict = legend_dict.copy()
    legend_dict.update(font_format)

    fig.update_layout(
        autosize=True,
        legend=legend_dict
    )


def watermark_add(fig, file: str, x, y, opacity: float = 0.25):
    img = Image.open(file)

    fig.add_layout_image(
        dict(
            source=img,
            opacity=opacity,
            xref='paper',
            yref='paper',
            xanchor='center',
            yanchor='middle',
            x=x,
            y=y,
            sizex=0.18,
            sizey=0.18,
            layer='above'
        )
    )


def date_since(days: int):
    return (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')


# Get 2 unix dates from date strings formatted '%Y-%m-%dT%H:%M:%SZ'
def to_unix_date_tuple(date1, date2, rounding=1440):
    date1_obj = datetime.strptime(date1, "%Y-%m-%dT%H:%M:%SZ")
    date2_obj = datetime.strptime(date2, "%Y-%m-%dT%H:%M:%SZ")

    unix_date1 = int(time.mktime(date1_obj.timetuple()))
    unix_date2 = int(time.mktime(date2_obj.timetuple()))

    # Rounded to the minute
    return [int(unix_date1 / rounding) * rounding, int(unix_date2 / rounding) * rounding]


def df_unix_to_8601_format(df, column: str = 'timestamp'):
    df[column] = pd.to_datetime(df[column], unit='s')
    df[column] = df[column].dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def fill_in_gaps(df, column, fill_value, limit=None):
    df.set_index(column, inplace=True)
    full_index = pd.Index(np.arange(df.index.min(), df.index.max() + 1), name=column)
    df = df.reindex(full_index, fill_value=0)
    df.reset_index(inplace=True)

    if (limit):
        df = df.tail(limit)
        df.reset_index(inplace=True)

    return (df)


def get_avg_str(ticktextFormatter, averages):
    dec_string = f'   (   {bold("Avg.  ")} '
    avg_string = ''
    sep = False

    for avg in averages:
        dec_string += '</b>and  <b>' if sep else ''
        if (ticktextFormatter):
            avg_string = ticktextFormatter(avg)
        else:
            avg_string = str(avg) + '%   '
        dec_string += avg_string
        sep = True
    return (dec_string + ')')


def bold(text):
    return (f'<b>{text}</b>')

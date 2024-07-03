from datetime import datetime, timedelta
from PIL import Image
import pandas as pd
import time

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
    'title_font_size': 15,
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


def bold_labels_set(fig):
    fig.for_each_trace(lambda t: t.update(name=bold(t.name)))


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


# This and the group of functions related to plots in this file
# use the `[attribute]_default` dicts. You may overwrite
# the attributes as you wish by passing in a new dict with the fields you
# want to replace.
def annotations_add(
    fig, annotations: list[dict], format: dict = annotation_format_default
):
    formats = [format.copy() for _ in annotations]

    for annotation, formatItem in zip(annotations, formats):
        formatItem.update(annotation)

    fig.update_layout(annotations=formats)


def annotations_delete(fig):
    for annotation in fig['layout']['annotations']:
        annotation['text'] = ''


def hoverplate_update(
    fig, hovertemplate, hoverlabel: dict = hoverlabel_default
):
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


def date_since(days: int, format: str = '%Y-%m-%dT%H:%M:%SZ'):
    date = datetime.now() - timedelta(days=days)
    return (date.strftime(format))


def to_unix_date_tuple(
    date1, date2, rounding=1440, format: str = '%Y-%m-%dT%H:%M:%SZ'
) -> tuple:
    '''
    Get a tuple of unix dates from date strings
    '''
    date1_obj = datetime.strptime(date1, format)
    date2_obj = datetime.strptime(date2, format)

    unix_date1 = int(time.mktime(date1_obj.timetuple()))
    unix_date2 = int(time.mktime(date2_obj.timetuple()))

    # Rounded to the minute
    return (
        int(unix_date1 / rounding) * rounding,
        int(unix_date2 / rounding) * rounding
    )


def df_unix_to_8601_format(df, column: str = 'timestamp'):
    df[column] = pd.to_datetime(df[column], unit='s')
    df[column] = df[column].dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def bold(text):
    return (f'<b>{text}</b>')


time_string_map = {
    'month': {'amount': 6750},
    'day': {'amount': 225},
    'hour': {'amount': 9.375}
}


def get_epoch_readable_unit(epochs: float) -> str:
    '''
    Convert epochs into a readable string according to `time_string_map`.

    Example: with 225 epochs, returned string is '1 day'
    '''
    for unit, value in time_string_map.items():
        threshold = value['amount']
        if (epochs >= threshold):
            converted = epochs/threshold
            return (
                f'{converted:,.0f} '
                f'{unit if ((converted) == 1) else unit + "s"}'
            )

    return ('')


def fraction_clamp(fraction: float, clamp=200):
    '''
    Round a float to the closest multiple of `clamp`.
    '''
    smaller = int(fraction / clamp) * clamp
    bigger = smaller + clamp
    if ((fraction - smaller) > (bigger - fraction)):
        return (bigger)
    else:
        return (1 if (smaller == 0) else smaller)

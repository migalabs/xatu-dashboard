import numpy as np
import pandas as pd
import plotly.express as px
from export import ABS_PATH
from creates import prefix, bold_labels_set
from utils import (
    hoverplate_update, title_format, legend_update, watermark_add, bold
)
from pycountry_convert import (
    country_alpha2_to_country_name, country_name_to_country_alpha3
)


def safeCountry_alpha2_to_country_name(country_code):
    try:
        return (country_alpha2_to_country_name(country_code))

    except (KeyError):
        return (np.nan)


def alpha2_to_alpha3(alpha2_code):
    country_name = safeCountry_alpha2_to_country_name(alpha2_code)

    if (country_name == np.nan):
        return (np.nan)

    alpha3_code = country_name_to_country_alpha3(country_name)

    return (alpha3_code)


def roundCategorical(x):
    left, right = x.left, x.right

    left, right = round(left, 0), round(right, 0)

    left, right = left.astype(int), right.astype(int)

    return (pd.Interval(left, right, closed=x.closed))


def formatBins(df):
    return (df.str.replace('(', '').str.replace(']', '').str.replace(',', ' - ').str.replace('.0', ''))


def createBins(df, df_nodup, n):
    _, bin_edges = np.histogram(df_nodup['node_count'], bins=n)

    bins = np.sort(bin_edges.flatten())

    bins[0] = df_nodup['node_count'].min() - 0.1

    df['node_count_bins'] = pd.cut(df['node_count'], bins=bins)


def geoCreate(df, tint, locations, loc_names, color, title):
    fig = px.choropleth(
        df,
        locations=locations,
        color='node_count_bins',
        hover_name=loc_names,
        custom_data=[color, 'node_count_bins'],
        color_discrete_sequence=tint,
        projection='patterson',
        fitbounds='locations'
    )

    fig.update_geos(
        showland=True,
        landcolor='lightgray',
        showframe=False,
        showcoastlines=False
    )

    title_format(fig, dict(title_text=bold(title)))

    watermark_add(fig, f'{ABS_PATH}/assets/migalabsLogo.png', 0.5, 0.5)

    bold_labels_set(fig)

    legend_update(fig, True, dict(
            title_text='',
            orientation='v',
            yanchor='middle',
            xanchor='left',
            x=0,
            y=0.5
        )
    )

    hoverplate_update(fig, "<b>%{hovertext}</b><br><b>Node count:</b> %{customdata[0]:.0f}<br><b>Range:</b> %{customdata[1]}<extra></extra>")

    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color='white'
    )

    return (fig)

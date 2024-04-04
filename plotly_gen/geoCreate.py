from   utils             import updateHoverplate, formatTitle, legendUpdate, addWatermark
from   creates           import prefix, setBoldLabels, createdfApi
from   pycountry_convert import country_alpha2_to_country_name, country_name_to_country_alpha3
import plotly.express    as px
import pandas            as pd
import numpy             as np

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

    return (pd.Interval(left, right, closed = x.closed))

def formatBins(df):
    return (df.str.replace('(', '').str.replace(']', '').str.replace(',', ' - ').str.replace('.0', ''))

def binsCreate(df, df_nodup, n):
    _, bin_edges = np.histogram(df_nodup['node_count'], bins = n)

    bins = np.sort(bin_edges.flatten())

    bins[0] = df_nodup['node_count'].min() - 0.1

    df['node_count_bins'] = pd.cut(df['node_count'], bins = bins)

def geoCreate(df, tint, locations, loc_names, color, title):
    fig = px.choropleth(
        df,
        locations = locations,
        color = 'node_count_bins',
        hover_name = loc_names,
        custom_data = [color, 'node_count_bins'],
        color_discrete_sequence = tint,
        projection = 'patterson',
        fitbounds = 'locations'
    )

    fig.update_geos(
        showland = True,
        landcolor = 'lightgray',
        showframe = False,
        showcoastlines = False
    )

    formatTitle(fig,
        dict(
            title_text = '<b>' + title + '</b>'
        )
    )

    addWatermark(fig, '/templates/img/migalabsLogo.png', 0.5, 0.5)

    setBoldLabels(fig)

    legendUpdate(fig, True,
        dict(
            title_text = '',
            orientation = 'v',
            yanchor = 'middle',
            xanchor = 'left',
            x = 0,
            y = 0.5
        )
    )

    updateHoverplate(fig, "<b>%{hovertext}</b><br><b>Node count:</b> %{customdata[0]:.0f}<br><b>Range:</b> %{customdata[1]}<extra></extra>")

    fig.update_traces(
        marker_line_width = 0.5,
        marker_line_color = 'white'
    )

    return (fig)

def GeoDistCreate(session):
    df = createdfApi(session, prefix + '/all/geographical_distribution')

    plotname = 'geo-dist'

    tint = px.colors.sequential.Blues[::-1]

    df['country_names'] = df['country_code'].apply(safeCountry_alpha2_to_country_name)
    df = df.dropna(subset = ['country_names'])
    df['country_code'] = df['country_code'].apply(alpha2_to_alpha3)
    df = df.dropna(subset = ['country_code'])
    df_nodup = df[['node_count']].drop_duplicates()
    df_nodup = df_nodup.dropna(subset = ['node_count'])

    binsCreate(df, df_nodup, 20)

    df['node_count_bins'] = df['node_count_bins'].apply(roundCategorical)
    df['node_count_bins'] = df['node_count_bins'].astype(str)
    df['node_count_bins'] = formatBins(df['node_count_bins'])

    fig = geoCreate(
        df, tint, 'country_code', 'country_names', 'node_count', 'Geographical Distribution of Validators'
    )

    plot_div = fig.to_html(full_html = False, include_plotlyjs = False)

    return { plotname: plot_div }

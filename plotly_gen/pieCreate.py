from   creates        import prefix, createdfApi, createdfCSV, sortByPercentage
from   utils          import addAnnotations, updateHoverplate, formatTitle, legendUpdate, addWatermark, boldText
import plotly.express as px
import colorsys

def pieCreate(df, values, slices_data, colors: dict, title):
    fig = px.pie(
        df,
        values = values,
        names = 'legend_labels',
        category_orders = dict(legend_labels = sortByPercentage(df, slices_data)),
        hole = 0.635,
        color = slices_data,
        color_discrete_map = colors.get('color_discrete_map'),
        color_discrete_sequence = colors.get('color_discrete_sequence')
    )

    updateHoverplate(fig, "%{label}: %{value}")

    fig.update_traces(
        marker = dict(
            line = dict(
                color = 'white',
                width = 0.5
            )
        ),
        textinfo = 'percent',
        textposition = 'none'
    )

    # This adds the 'TOTAL' thing inside of the donut
    addAnnotations(fig,
        [
            dict(
                text = 'TOTAL',
                font_color = 'gray',
                x = 0.5,
                y = 0.45,
                font_size = 22
            ),
            dict(
                text = '<b>' + str('{:,}'.format(df.sum()[values])) + '</b>',
                x = 0.5,
                y = 0.5333,
                font_size = 35
            )
        ]
    )

    legendUpdate(fig, True,
        dict(
            orientation = 'h',
            yanchor = 'auto',
            xanchor = 'auto',
            x = 0.5,
            y = -0.2
        )
    )

    formatTitle(fig,
        dict(
            title_text = boldText(title)
        )
    )

    addWatermark(fig, '/templates/img/migalabsLogo.png', 0.5, 0.33)

    return (fig)

def clientDiversityCreate(session):
    plotname = 'cli-div'

    df = createdfApi(session, prefix + '/all/client_diversity', ['client_name', 'node_count'])

    fig = pieCreate(df, 'node_count', 'client_name',
            { 'color_discrete_map' : {
                    'lighthouse': '#7172ad',
                    'prysm': '#88bf4d',
                    'teku': '#ef8c8c',
                    'nimbus': '#a989c5',
                    'lodestar': '#509ee3',
                    'grandine': '#f9d45c',
                    'erigon': '#98d9d9',
                    'unknown': '#f2a86f',
                }
            },
            'Client Type Distribution'
    )

    plot_div = fig.to_html(full_html = False, include_plotlyjs = False)

    return { plotname: plot_div }

def hostingDistributionCreate(session):
    plotname = 'hosting-dist'

    df = createdfApi(session, prefix + '/all/hosting_type', ['hosting_type', 'node_count'])

    fig = pieCreate(df, 'node_count', 'hosting_type',
            { 'color_discrete_map' : {
                    'Cloud': '#f2a86f',
                    'Residential': '#f9d45c',
                    'Unknown': '#a989c5',
                    'Finance & IT': '#98d9d9',
                    'Academia': '#509ee3'
                }
            },
            'Node Hosting Distribution'
    )

    plot_div = fig.to_html(full_html = False, include_plotlyjs = False)

    return { plotname: plot_div }

def architectureDistributionCreate(session):
    plotname = 'arch-dist'

    df = createdfApi(session, prefix + '/all/architecture', ['client_arch', 'node_count'])

    fig = pieCreate(df, 'node_count', 'client_arch',
            { 'color_discrete_map' : {
                    'unknown': '#f2a86f',
                    'arm': '#f9d45c',
                    'x86_64': '#88bf4d'
                }
            },
            'Architecture Distribution'
    )

    plot_div = fig.to_html(full_html = False, include_plotlyjs = False)

    return { plotname: plot_div }

def OsDistributionCreate(session):
    plotname = 'os-dist'

    df = createdfApi(session, prefix + '/all/os', ['client_os', 'node_count'])

    fig = pieCreate(df, 'node_count', 'client_os',
            { 'color_discrete_map' : {
                    'unknown': '#f2a86f',
                    'linux': '#f9d45c',
                    'windows': '#ef8c8c',
                    'mac': '#7172ad'
                }
            },
            'Client OS Distribution'
    )

    plot_div = fig.to_html(full_html = False, include_plotlyjs = False)

    return { plotname: plot_div }

def ISPcreate(session):
    df = createdfApi(session, prefix + '/all/internet_providers', ['isp', 'total_nodes'])

    plotname = 'isp'

    fig = pieCreate(df, 'total_nodes', 'isp',
            { 'color_discrete_sequence' : [
                    '#9A7DAC', '#C778A6', '#E46A98', '#E6666E', '#EB8568', '#EFA36A', '#F3BF62',
                    '#EED154', '#E2DC59', '#C9D469', '#9ABF5B', '#A7CA9F', '#AED1C3', '#99CBC6',
                    '#8BB2C5'
                ]
            },
            'Number of Nodes Per ISP'
    )

    legendUpdate(fig, True,
        dict(
            x = 0.5,
            y = -0.26
        )
    )

    plot_div = fig.to_html(full_html = False, include_plotlyjs = False)

    return { plotname: plot_div }

# The higher 'start' is, the color where it starts will shift forward
# The higher 'end' is, the earlier the pattern will stop
def discreteSequenceGenerate(total, start, end):
    format = '#%02x%02x%02x'
    color_array = ['']

    for index in range(total):
        color = colorsys.hsv_to_rgb(((index + start) / (total + end)), 0.6, 0.9)
        color_array[index] = format % (tuple( int(val * 255) for val in color ))
        color_array.append('#ffffff')

    return (color_array)


def ISPcloudCreate(session):
    df = createdfApi(session, prefix + '/all/internet_providers?host_type=cloud', ['isp', 'total_nodes'])

    plotname = 'cloud-isp'

    color_sequence = discreteSequenceGenerate(len(df), 0, 4)

    fig = pieCreate(df, 'total_nodes', 'isp',
            { 'color_discrete_sequence' : color_sequence },
            'Number of Nodes Per Cloud ISP'
    )

    legendUpdate(fig, True,
        dict(
            x = 0.5,
            y = -0.25
        )
    )

    plot_div = fig.to_html(full_html = False, include_plotlyjs = False)

    return { plotname: plot_div }

def ISPresidentialCreate(session):
    df = createdfApi(session, prefix + '/all/internet_providers?host_type=residential', ['isp', 'total_nodes'])

    plotname = 'residential-isp'

    color_sequence = discreteSequenceGenerate(len(df), 5, 1)

    fig = pieCreate(df, 'total_nodes', 'isp',
            { 'color_discrete_sequence' : color_sequence },
            'Number of Nodes Per Residential ISP'
    )

    legendUpdate(fig, True,
        dict(
            x = 0.5,
            y = -0.25
        )
    )

    plot_div = fig.to_html(full_html = False, include_plotlyjs = False)

    return { plotname: plot_div }

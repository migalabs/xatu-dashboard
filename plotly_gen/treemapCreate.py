from   creates        import prefix, createdfApi, sortByPercentage, setBoldLabels
from   utils          import addAnnotations, updateHoverplate, formatTitle, legendUpdate, addWatermark
import plotly.express as px
import pandas         as pd

def treemapCreate(df, title, names, values, path, hoverdata, colors, color, custom_data):
    fig = px.treemap(
        df,
        title = title,
        labels = names,
        values = values,
        path = path,
        color_continuous_scale = colors,
        hover_name = names,
        color = color,
        custom_data = custom_data
    )

    formatTitle(fig,
        dict(
            title_text = '<b>' + title + '</b>',
        )
    )

    lido_percent = df.loc[df[names] == '<b>lido</b>', custom_data[0]].values[0]

    # overrides customdata (percentage in this case)
    for a, id in enumerate(fig.data[0].ids):
        if (id == 'Active Validators/<b>lido</b>'):
            fig.data[0].customdata[a][0] = lido_percent
        if (id == 'Active Validators'):
            fig.data[0].customdata[a][0] = '100'
        if (id == 'Active Validators/ '):
            # percent of all nodes excluding lido
            fig.data[0].customdata[a][0] = (100 - lido_percent).round(3)

    updateHoverplate(
        fig,
        '<b>%{label}:</b> %{value} Active Validators<br><b>Percent:</b> %{customdata[0]}%<extra></extra>'
    )

    addWatermark(fig, '/templates/img/migalabsLogo.png', 0.5, 0.5, 0.33)

    setBoldLabels(fig)

    fig.update_traces(
        marker = dict(cornerradius = 5)
    )

    return (fig)

color_map = [
        '#E8A06A', '#EEC750', '#82AE4E', '#9EC8CE', '#5492C3', '#A795BA', '#636490'
    ]

def handleLidoNesting(df):
    df['parents'] = df['entity'].apply(lambda x: 'lido' if 'lido' in x else ' ')

    lido_nvalidators = (((df[df['parents'] == 'lido'])['num_validators']).astype(int))
    lido_total = lido_nvalidators.sum()
    lido_percent = (lido_total / df['num_validators'].sum() * 100).round(3)

    # this is a workaround
    # (sum of children to be taken as color)
    df['true_percentage'] = (df['percentage'].astype(float)).round(3)
    df.loc[len(df)] = ['lido', 0.00001, 0.000001, '<b>lido</b>', 'Active Validators', lido_percent]

    df['percentage'] = df.apply(
        lambda x: round(float(lido_percent), 3) if x['parents'] == 'lido' else round(float(x['percentage']), 3), axis = 1)
    df['parents'] = df['parents'].apply(lambda x: f'<b>lido</b>' if 'lido' in x else ' ')
    df.loc[df['entity'] == 'lido', 'parents'] = 'Active Validators'

def handleWhaleAgg(df):
    df.loc[df['entity'] == 'whales', 'root'] = 'Active Validators'
    df.loc[df['entity'] == 'whales', 'parents'] = ' '
    df.loc[df['entity'] == 'whales', 'legend_labels'] = '<b>whales</b>'

    return (df)

# fields = [ name, value, ...]
def groupBySuffix(df, suffix, item, value, fields, group_name):
    df.loc[df[item].str.contains(suffix), item] = group_name
    df = df.groupby(item)[fields].apply(sum).reset_index()

    return (df)

def entitiesCreate(session):
    plotname = 'validators-entities'

    df = createdfApi(
        session,
        'eth/v1/beacon/consensus/entities/active_validators',
        ['entity', 'num_validators'],
        True
    )
    df = df.drop('timestamp', axis = 1)

    handleLidoNesting(df)

    df['value_strings'] = ''

    df['root'] = df['parents'].apply(lambda x: x if 'lido' in x else 'Active Validators')
    df = groupBySuffix(df, 'whale_0x', 'entity', 'num_validators',
        ['num_validators', 'percentage', 'legend_labels', 'parents', 'true_percentage', 'value_strings', 'root'], 'whales')

    df['value_strings'] = (df['num_validators'].astype(int)).apply(lambda x: f'{x:,}')

    df.loc[df['parents'] == '<b>lido</b>', 'root'] = 'Active Validators'

    df = handleWhaleAgg(df)

    fig = treemapCreate(df, 'Active Validators\' Entities', 'legend_labels',
            'num_validators', ['root', 'parents', 'legend_labels', 'value_strings'],
            'legend_labels', color_map, 'percentage', ['true_percentage']
        )

    plot_div = fig.to_html(full_html = False, include_plotlyjs = False)

    return { plotname: plot_div }

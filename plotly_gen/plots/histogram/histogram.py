import plotly.express as px
from plots.area.area import yaxis_format_amounts
from creates import bold_labels_set
from datetime import datetime
from export import ABS_PATH
from utils import (
    date_since, watermark_add, hoverplate_update, title_format,
    legend_update, bold
)

end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')


def histogramCreate(
    df, x, y, title, ytitle, xtitle,
    name, color_sequence, customdata,
    xticktext, xtickvals,
    y_formatter, yskips,
    hovertemplate, nbins, legend: bool = False,
    opacity: float = 0.45
):
    fig = px.histogram(
        df,
        x=x,
        y=y,
        title=title,
        color=name,
        color_discrete_sequence=color_sequence,
        nbins=nbins,
        histfunc='avg'
    )

    if (legend):
        bold_labels_set(fig)

        legend_update(fig, True, dict(
                orientation='v',
                yanchor='top',
                xanchor='left',
                x=1,
                y=1,
                title_text='',
            )
        )
    else:
        legend_update(fig, False)

    fig.update_layout(bargap=0.1)

    yaxis_format_amounts(fig, df, y, y_formatter, yskips)

    fig.update_yaxes(
        title_text=bold(ytitle),
        title_font_size=15,
        title_standoff=10,
        showgrid=True,
        gridcolor='#f9f9f9',
        title_font_family='Lato',
        title_font_color='#4c5773'
    )

    fig.update_xaxes(
        title_text=bold(xtitle),
        title_font_size=15,
        title_standoff=10,
        range=date_since(days=1),
        dtick=6000000,
        tick0=0.1,
        tickvals=xtickvals,
        tickformat=bold('%B %d, %Y, %I:%M %p'),
        ticktext=xticktext if (xticktext) else None
    )

    title_format(fig, dict(
            title_text=bold(title) + '   (   Avg. ' + y_formatter(df['values'].mean().round(3)) + ')',
        )
    )

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

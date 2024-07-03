import plotly.express as px
from creates import sort_by_column
from export import ABS_PATH
from utils import (
    annotations_add, hoverplate_update, title_format,
    legend_update, watermark_add, bold
)


def pie_fig_create(
    df, values: str, names: str, slices_data: str,
    colors: dict, title: str, hole: float = 0.635,
    hoverplate='%{label}: %{value}', title_annotation=None,
    custom_data: list[str] = [], hole_text='TOTAL'
):
    fig = px.pie(
        df,
        values=values,
        names=names,
        category_orders=dict(
            legend_labels=sort_by_column(
                'percentage', df, slices_data)),
        hole=hole,
        color=slices_data,
        color_discrete_map=colors.get('color_discrete_map'),
        color_discrete_sequence=colors.get('color_discrete_sequence'),
        custom_data=custom_data
    )

    hoverplate_update(fig, hovertemplate=hoverplate)

    fig.update_traces(
        marker=dict(
            line=dict(
                color='white',
                width=0.5
            )
        ),
        textinfo='percent',
        textposition='none'
    )

    # This adds an annotation inside of the donut
    annotations_add(fig, [
            dict(
                text=hole_text,
                font_color='gray',
                x=0.5,
                y=0.45,
                font_size=22
            ),
            dict(
                text='<b>' + str('{:,}'.format(df.sum()[values])) + '</b>',
                x=0.5,
                y=0.5333,
                font_size=35
            )
        ]
    )

    legend_update(fig, True, dict(
            orientation='h',
            yanchor='auto',
            xanchor='auto',
            x=0.5,
            y=-0.2
        )
    )
    if (title_annotation):
        title = bold(title) + "   -   " + title_annotation

    title_format(fig, dict(title_text=title))

    watermark_add(fig, f'{ABS_PATH}/assets/migalabsLogo.png', 0.5, 0.33)

    return (fig)

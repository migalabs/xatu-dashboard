import plotly.express as px
import colorsys
from creates import prefix, df_api_create, percentage_sort_by
from export import ABS_PATH
from utils import (
    annotations_add, hoverplate_update, title_format,
    legend_update, watermark_add, bold
)


def pieCreate(df, values, slices_data, colors: dict, title, hole=0.635):
    fig = px.pie(
        df,
        values=values,
        names='legend_labels',
        category_orders=dict(legend_labels=percentage_sort_by(df, slices_data)),
        hole=hole,
        color=slices_data,
        color_discrete_map=colors.get('color_discrete_map'),
        color_discrete_sequence=colors.get('color_discrete_sequence')
    )

    hoverplate_update(fig, "%{label}: %{value}")

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

    # This adds the 'TOTAL' annotation inside of the donut
    annotations_add(fig,
        [
            dict(
                text='TOTAL',
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

    title_format(fig, dict(title_text=bold(title)))

    watermark_add(fig, f'{ABS_PATH}/assets/migalabsLogo.png', 0.5, 0.33)

    return (fig)

import pandas as pd
import plotly.express as px
from creates import bold_labels_set
from export import ABS_PATH
from utils import (
    hoverplate_update, title_format, watermark_add, bold
)


def treemapCreate(
    df, title, names, values, path, hoverdata, colors, color, custom_data,
    hoverplate
):
    fig = px.treemap(
        df,
        title=title,
        labels=names,
        values=values,
        path=path,
        color_continuous_scale=colors,
        hover_name=names,
        color=color,
        custom_data=custom_data
    )

    title_format(fig, dict(title_text=bold(title)))

    hoverplate_update(fig, hoverplate)

    watermark_add(fig, f'{ABS_PATH}/assets/migalabsLogo.png', 0.5, 0.5, 0.33)

    bold_labels_set(fig)

    fig.update_traces(marker=dict(cornerradius=5))

    return (fig)

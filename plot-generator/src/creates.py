from dotenv import load_dotenv
from utils import bold
import datetime as dt

NOW = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

load_dotenv()


def notice_print(string) -> None:
    '''
    Stylized printing.
    '''
    length = int(string.__len__() / 2)

    print('\n  ', end='')
    print('-*' * length, end='')
    print('\n| ' + string + ' |', end='\n  ')
    print('*-' * length, end='')
    print('\n')


def sort_by_column(column, df, index):
    sorted_df = df.sort_values(by=column, ascending=False)
    sorted_df = sorted_df.reset_index(drop=True)

    return (sorted_df[index].tolist())


def legend_update(fig, yanchor, xanchor, orientation, font_size, x):
    fig.update_layout(
        legend=dict(
            yanchor=yanchor,
            xanchor=xanchor,
            x=x,
            orientation=orientation,
            font=dict(
                size=font_size,
                family='Lato'
            )
        )
    )


def title_format(fig, title, x, y):
    fig.update_layout(
        title=bold(title),
        font_family='Lato',
        font_color='#4c5773',
        title_font_color='#4c5773',
        title_font_family='Lato',
        title_y=y,
        title_x=x,
        title_font_size=25
    )


def get_current_timestamp(_):
    '''
    Get current timestamp.
    Returns a dict with the format of {'timestamp': timestamp}
    Argument is ignored, since it is treated as a generator.
    '''
    time = dt.datetime.now(dt.timezone.utc)
    timestamp = time.strftime('%B %d, %Y, %H:%M UTC')

    return {'timestamp': timestamp}

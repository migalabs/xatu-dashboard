from time import sleep
from dotenv import load_dotenv
from utils import bold
from json import JSONDecodeError
import datetime as dt
import os
import requests
from clickhouse_driver import Client

NOW = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

load_dotenv()


def notice_print(string):
    length = int(string.__len__() / 2)

    print('\n  ', end='')
    print('-*' * length, end='')
    print('\n| ' + string + ' |', end='\n  ')
    print('*-' * length, end='')
    print('\n')


def endpoint_safe_fetch(session, url, endpoint, params=None):
    for times in range(3):
        try:
            response = (session.get(url + endpoint, params=params))

            if (response.status_code != 200):
                print(f'\nError. Status code: {response.status_code}. Retrying...')
                print(session)
                sleep(times + 1)
                continue

            data = response.json()

            return (data)

        except (JSONDecodeError):
            print('\nData is not a valid JSON.')
            return (None)

        except (requests.exceptions.ConnectionError):
            print('\nConnection failure. Retrying...')
            sleep(1)
            continue

    return (None)


def legend_labels_percent_parse(df, percent_names, no_perc_labels):
    if ('timestamp' in df):
        percentages = df.groupby('timestamp')[percent_names[1]].apply(
            lambda x: (x / x.sum() * 100)
        )
    else:
        percentages = (df[percent_names[1]] / df[percent_names[1]].sum() * 100)

    percentages = percentages.round(3)
    df['percentage'] = percentages.reset_index(drop=True)
    df['legend_labels'] = df[percent_names[0]].apply(bold)

    if (not no_perc_labels):
        df['legend_labels'] = df.apply(
            lambda x: x['legend_labels'] +
            bold(' (' + str(x['percentage']) + '%)'), axis=1)


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
    time = dt.datetime.now(dt.timezone.utc)
    timestamp = time.strftime('%B %d, %Y, %H:%M UTC')

    return {'timestamp': timestamp}

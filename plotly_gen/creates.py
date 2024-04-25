from time import sleep
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from utils import bold
from json import JSONDecodeError
import pandas as pd
import datetime as dt
import os
import requests
from clickhouse_driver import Client

load_dotenv()

SERVER = os.environ['SERVER']

API_URL = os.environ['API_URL']

prefix = 'eth/v1/nodes/consensus/'

NOW = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


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


def current_endpoint_print(endpoint):
    historic = (endpoint.find('historic') != -1)

    name = endpoint.split('/')

    name_len = name.__len__()

    name = name[name_len - 1] if not (historic) else name[name_len - 2]

    print(f'Creating {name}' + (' (historic)' if (historic) else ''))


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


# percent_names is just the column you want to apply the percentage of nodes
# to, for the legend labels. For example, 'client_type'.
def df_api_create(session, endpoint, percent_names=None, no_perc_labels=False):
    current_endpoint_print(endpoint)

    data = endpoint_safe_fetch(session, API_URL, endpoint)

    if (not data):
        notice_print(f'Data from the API could not be fetched. {NOW}')
        exit(1)

    df = pd.json_normalize(data, record_path='data', meta='timestamp')

    if (percent_names):
        legend_labels_percent_parse(df, percent_names, no_perc_labels)

    return (df)


# for precalculated values, just adds the symbol
def symbolAddToLabels(df, symbol, values, names, labels: str = 'legend_labels'):
    df[labels] = df.apply(lambda x: f"{str(x[values])}{symbol}", axis=1)

    if (names):
        df[labels] = df.apply(lambda x: f"{x[names]} {x['legend_labels']}", axis=1)


def generateLabel(row, symbol, values, names, labels: str = 'legend_labels'):
    label = f'{str(row[values])}{symbol}'

    if (names):
        label = f"{row[names]} {label}"
    return (label)


def setPercent(df, target, names=None, labels: str = 'legend_labels'):
    df[target] = df[target].astype(float).round(3)
    symbolAddToLabels(df, '%', target, names, labels)

    return (df)


def setGb(df, target, names=None, labels: str = 'legend_labels'):
    df[target] = df[target].astype(float).round(0).astype(int)

    df[labels] = df.apply(
        lambda x: generateLabel(x, 'Mb', target, names, labels)
        if x[target] < 1000
        else generateLabel(
            round(x / 1024, 2), 'Gb', target, names, labels), axis=1
        )

    return (df)


def setMbps(df, target, names=None, labels: str = 'legend_labels'):
    df[target] = df[target].astype(float).round(0).astype(int)

    df[labels] = df.apply(
        lambda x: generateLabel(x, 'Kb/s', target, names, labels)
        if x[target] < 1000
        else generateLabel(
            round(x / 1024, 2), 'Mb/s', target, names, labels), axis=1
        )

    return (df)


def setWatts(df, target, names=None, labels: str = 'legend_labels'):
    df[target] = df[target].astype(float).round(3)

    df[labels] = df.apply(
        lambda x: generateLabel(x, 'W', target, names, labels), axis=1)

    return (df)


def setWh(df, target, names=None, labels: str = 'legend_labels'):
    df[target] = df[target].astype(float).round(3)

    df[labels] = df.apply(
        lambda x: generateLabel(x, 'Wh', target, names, labels), axis=1)

    return (df)


PROM_HTTP_URL = os.environ['PROM_HTTP_URL']

symbol_functions: dict = {
    '%': setPercent,
    'Mbps': setMbps,
    'W': setWatts,
    'Wh': setWh,
    'Gb': setGb
}


def df_prometheus_create(
    session, endpoint, record_path, params=None, symbol=None, plot_name='',
    labels_column='legend_labels', names=None
):
    if (params):
        current_endpoint_print(plot_name)

    data = endpoint_safe_fetch(
        session,
        PROM_HTTP_URL,
        endpoint,
        params
    )

    if (not data):
        notice_print(f'Data from the API could not be fetched. {NOW}')
        exit(1)

    df = pd.json_normalize(
        data,
        record_path=['data', 'result', record_path]
    )

    df.columns = ['timestamp', 'values']

    df = symbol_functions[symbol](df, record_path, names, labels_column)

    return (df)


def df_clickhouse_create(client: Client, query, plot_name=''):
    current_endpoint_print(plot_name)

    df = client.query_dataframe(query)

    return (df)


# percent_names[0] is supposed to be what you'd be 'coloring' (like client_name)
# percent_names[1] is supposed to be the count (like node_count)
def df_CSV_create(path, print_name=None, percent_names=None, no_perc_labels=False):
    if (print_name):
        print(f'Creating {print_name} from CSV')

    df = pd.read_csv(f'{getRootPath()}/{path}')

    if (percent_names):
        legend_labels_percent_parse(df, percent_names, no_perc_labels)

    return (df)


def percentage_sort_by(df, index):
    sorted_df = df.sort_values(by='percentage', ascending=False)
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


def bold_labels_set(fig):
    fig.for_each_trace(lambda t: t.update(name = bold(t.name)))


def getNodesTimestamp(session):
    df = df_api_create(session, prefix + '/all/client_diversity')
    df_timestamp = pd.to_datetime(df['timestamp'][0]).strftime('%B %d, %Y, %H:%M UTC')

    return {'timestamp': df_timestamp}


def current_timestamp_get(_):
    timestamp = dt.datetime.now(dt.timezone.utc).strftime('%B %d, %Y, %H:%M UTC')

    return {'timestamp': timestamp}

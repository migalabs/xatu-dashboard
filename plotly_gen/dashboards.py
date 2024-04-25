from builder_functions import (blob_functions, get_test_functions)
from creates import notice_print
from sessions import (
    session_create, clickhouse_client_init,
    PROM_USER, PROM_PASS, API_KEY
)

dashboard_dict: dict = {
    'blob': {
        'mode': 'production',
        'template': 'blob.html',
        'function_array': blob_functions,
        'arguments': clickhouse_client_init()
    },
    # If you want to test separate dashboards in /test just add
    # a new dashboard with the functions you want
    # Running with -t will save the file inside /test
    # However -t (no args) will also run the default / normal dashboards
    # but will include dashboards with mode = 'testing'
    # 'metrics_testing': {
    #     'mode': 'testing',
    #     'template': 'node-metrics.html',
    #     'function_array': [],
    #     'arguments': None
    # },
    'dev': {
        'mode': 'list testing',
        'template': 'testing.html',
        'function_array': [],
        'arguments': clickhouse_client_init()
    }
}


def get_dashboards_from_args(
    dashboard_args: dict, dashboards: dict = dashboard_dict
):
    new_dashboards = {}
    dashboard_n_args = len(dashboard_args)

    if (dashboard_n_args == 0):
        notice_print(f'Please provide a dashboard to generate.')
        exit(1)

    for index in range(0, dashboard_n_args):
        dashboard_name = dashboard_args[index]

        if (not dashboards.get(dashboard_name)):
            notice_print(f'Please provide a valid dashboard name.')
            exit(1)

        new_dashboards[dashboard_name] = dashboards[dashboard_name]
    return (new_dashboards)

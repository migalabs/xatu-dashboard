from builder_functions import blob_functions, get_test_functions
from creates import notice_print
from clickhouse import clickhouse_client_init
from typing import Callable


# Dictionary of dashboards
# A dashboard is an array of functions, them being the generators
# of the plots you wish to insert into the 'template' field's file.
# Since these functions will be run in a loop, the 'arguments' field
# specifies what arguments to pass to ALL the generators of that dashboard.
dashboard_dict: dict = {
    'blob': {
        # MODE OPTIONS:
        # 'production' -> insert plot where the `plotname` is
        # 'list testing' -> Insert all plots at a 'testing' comment.
        # * The order is specified by the order of generation/arguments.
        'mode': 'production',
        'template': 'blob.html',  # at /plot-generator/templates/
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
    'dev': {  # This is the configuration for the `-t` flag dashboard
        'mode': 'list testing',
        'template': 'testing.html',
        'function_array': [],  # Functions specified with the flag will be here
        'arguments': clickhouse_client_init()
    }
}


def dashboard_flag(
    dashboard_args: dict, dashboards: dict, testing_functions: list[Callable]
) -> tuple:
    '''
    (`-d` flag)

    Generate specified dashboard.
    '''
    new_dashboards = {}
    dashboard_n_args = len(dashboard_args)

    if (dashboard_n_args == 0):
        notice_print(f'Please provide a dashboard to generate.')
        exit(1)

    for index in range(0, dashboard_n_args):
        dashboard_name = dashboard_args[index]
        if (not dashboards.get(dashboard_name)):
            notice_print(
                f'Please provide a valid dashboard name:'
                f' {dashboard_name} is invalid.')
            exit(1)
        new_dashboards[dashboard_name] = dashboards[dashboard_name]
    return (new_dashboards, testing_functions)


def testing_flag(
    arguments: list[str], dashboards: dict, testing_functions: list[Callable]
) -> tuple:
    '''
    (`-t` flag)

    Save the corresponding generator from the chosen (indexes + 1).

    Example: -t 1 2 3 will generate functions 1, 2 and 3 from builder_functions
    '''
    testing_functions = get_test_functions(arguments)
    dashboards['dev']['function_array'] = testing_functions
    return (dashboards, testing_functions)

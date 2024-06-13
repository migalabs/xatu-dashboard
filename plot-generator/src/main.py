from export import dashboard_dict_execute
from creates import notice_print, NOW
from opt_parse import get_options
from dashboards import get_dashboards_from_args, dashboard_dict
from builder_functions import get_test_functions, builder_functions
import sys


def main():
    n_args = sys.argv.__len__()
    list_testing_mode = False
    testing_functions = []
    options = get_options(n_args, sys.argv)
    dashboards = dashboard_dict

    testing_args = options.get('-t')
    if (testing_args):   # todo make function pointers for opt
        testing_functions = get_test_functions(testing_args)
        # todo get rid of this
        if (testing_functions and len(testing_functions) <= len(builder_functions)):
            list_testing_mode = True
        print(list_testing_mode)
        dashboards['dev']['function_array'] = testing_functions

    # Choosing to generate a specific dashboard(s)
    dashboard_args = options.get('-d')
    print(dashboard_args)  # check for list testing
    if (dashboard_args):
        dashboards = get_dashboards_from_args(dashboard_args)

    if (not list_testing_mode):  # Normal Dashboard
        notice_print('Building dashboards...')
        dashboard_dict_execute(dashboards)

    if (testing_functions):
        if (list_testing_mode):  # When you specify test functions
            notice_print('Building plot testing page...')
            dashboard_dict_execute(dashboards, 'list testing')
        else:
            notice_print('Building test dashboards...')
            dashboard_dict_execute(dashboards, 'testing')

    notice_print(f'Successfully built the dashboard(s). {NOW}')


if __name__ == '__main__':
    main()

from export import dashboard_dict_export
from creates import notice_print, NOW
from opt_parse import get_options
from dashboards import dashboard_flag, testing_flag, dashboard_dict
import sys


def main():
    dashboards = dashboard_dict
    options = get_options(sys.argv.__len__(), sys.argv)
    testing_functions = []
    flags: dict = {'-t': testing_flag, '-d': dashboard_flag}

    # find the corresponding flags and arguments and execute them
    for flag, function in flags.items():
        args = options.get(flag)
        print(flag, args)
        if (args):
            (dashboards, testing_functions) = function(args, dashboards, testing_functions)

    # Generation:
    if (not testing_functions):
        notice_print('Building dashboards...')
        dashboard_dict_export(dashboards)
    else:
        notice_print('Building plot testing page...')
        dashboard_dict_export(dashboards, 'list testing')

    notice_print(f'Successfully built the dashboard(s). {NOW}')


if __name__ == '__main__':
    main()

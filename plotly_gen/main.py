from pieCreate import clientDiversityCreate, hostingDistributionCreate, architectureDistributionCreate, OsDistributionCreate, ISPcreate, ISPcloudCreate, ISPresidentialCreate
from areaCreate import EnergyConsumptionCreate, PowerConsumptionCreate, clientDiversityEvolutionCreate, activeNodesCreate, CpuUsageCreate, memoryUsageCreate, networkBandwidthInOutCreate, FilesystemReadWriteCreate
from barCreate import rttDistCreate, adAttSnSbsCreate, beaconPerIPCreate, BlobsBySlotCreate
from geoCreate import GeoDistCreate
from treemapCreate import entitiesCreate
from creates import noticePrint, NOW, getNodesTimestamp, getCurrentTimestamp
from utils import getRootPath
from opt_parse import getOptions
from clickhouse_driver import Client
import sys
import requests
import os


# Will call all functions and append the result into plots_dict
# ALl functions are expected to return {plotname: plot_div}
def getPlotDivs(functions, argument):
    plots_dict = {}

    for function in functions:
        plots_dict.update(function(argument))

    return (plots_dict)


# This will append all function result's 'plot_div's into a big string
# And then put them inside of the list_testing file (templates/testing.html)
# At the moment
# This is the function used when choosing plots from index with -t
def replaceByList(html, plots_dict):
    plot_string = ''

    for plot, plot_div in plots_dict.items():
        if (not plot):
            continue
        plot_string = f'{plot_string}{plot_div}\n'

    html = html.replace('<!-- testing -->', plot_string)

    return (html)


# Function used normally (not list_testing mode)
# Will replace target comments with the corresponding plot name
def replaceByPlotname(html, plots_dict):
    for plot, plot_div in plots_dict.items():
        if (not plot):
            continue
        html = html.replace(f'<!-- {plot} -->', plot_div)

    return (html)


# Will get the final dashboard HTML
def getPlotHTML(plots_dict, template, replaceHandler):
    with open(template, 'r') as file:
        html = file.read()

    html = replaceHandler(html, plots_dict)

    return (html)


def writeToFile(filename, contents):
    with open(filename, 'w') as file:
        file.write(contents)


# will only generate the dashboards of the specified mode
# 'production' will save the dashboard at /
# 'testing' at /test and can have different plots (added to its function array)
# 'list testing' will only generate the plots you specify in args
# you choose an index according to the function array
# (-t 1 is first function in array, etc)
def createDashboards(dashboards, mode='production'):
    path = getRootPath()
    replaceHandler = replaceByList if mode == 'list testing' else replaceByPlotname
    # replaceByList is used only when you specify which to generate
    template_path, save_path = f'{path}/templates', f'{path}/generated'

    if (mode == 'testing'):
        template_path, save_path = f'{template_path}/test_templates', f'{save_path}/test'

    for dashboard, values in dashboards.items():
        dashboard_mode = values['mode']
        if ((mode != dashboard_mode) or not values['function_array']):
            continue
        print(f"\n** {dashboard} dashboard's plots **\n")
        filename = values['template']
        divs = getPlotDivs(values['function_array'], values['arguments'])
        final_html = getPlotHTML(
            divs, f'{template_path}/{filename}', replaceHandler)

        writeToFile(f'{save_path}/{filename}', final_html)


# Will return all testing functions if there are no arguments in the flag -t
# Otherwise, it will look for the function inside the index given
# order depends on the variable 'all_functions' below
# from the time of writing this, node_functions + metrics_functions
# so -t 1 will select the first function inside node functions
# Would be good to make it into a dictionary instead
def getTestFunctions(args, functions):
    n_args = args.__len__()
    testing_functions = functions.copy()
    testing_functions.extend([entitiesCreate])

    if (n_args > 0):
        testing_list = []

        for index in range(0, n_args):
            function_index = int(args[index]) - 1

            if (index == n_args or function_index >= len(testing_functions)):
                break

            testing_list.append(testing_functions[function_index])

        return (testing_list)

    return (testing_functions)


# This is for not having to create the authentication every time you fetch
# So you pass the created session around instead
def sessionCreate(data: dict):
    session = requests.Session()

    auth = data.get('auth')
    if (auth):
        session.auth = (auth.get('user'), auth.get('pass'))

    headers = data.get('headers')
    if (headers):
        session.headers.update(headers)

    return session


# clickhouse
def initClickhouseClient():
    return (Client(
            host=os.environ['CH_HOST'],
            port=os.environ['CH_PORT'],
            user=os.environ['CH_USER'],
            password=os.environ['CH_PASSWORD'],
            database=os.environ['CH_DATABASE'])
    )


PROM_USER = os.environ['PROM_USER']
PROM_PASS = os.environ['PROM_PASS']
API_KEY = os.environ['API_KEY']


def main():
    n_args = sys.argv.__len__()
    args = sys.argv
    list_testing_mode = False

    node_functions = [
        getNodesTimestamp, clientDiversityCreate, hostingDistributionCreate,
        ISPcreate, ISPcloudCreate, ISPresidentialCreate,
        architectureDistributionCreate, OsDistributionCreate,
        clientDiversityEvolutionCreate, activeNodesCreate, GeoDistCreate,
        rttDistCreate, adAttSnSbsCreate, beaconPerIPCreate, entitiesCreate
    ]

    metrics_functions = [
        getCurrentTimestamp, CpuUsageCreate, memoryUsageCreate,
        networkBandwidthInOutCreate, FilesystemReadWriteCreate,
        PowerConsumptionCreate, EnergyConsumptionCreate
    ]

    blob_functions = [
        getCurrentTimestamp, BlobsBySlotCreate
    ]

    all_functions = node_functions + metrics_functions + blob_functions

    testing_functions = []

    options = getOptions(n_args, sys.argv)

    testing_args = options.get('-t')

    if (testing_args):   # todo make function pointers for opt
        testing_functions = getTestFunctions(testing_args, all_functions)

        if (testing_functions and len(testing_functions) <= len(all_functions)):
            list_testing_mode = True

    dashboards = {
        'nodes': {
            'mode': 'production',
            'template': 'nodes.html',
            'function_array': node_functions,
            'arguments': sessionCreate({
                    'headers': {'X-API-Key': API_KEY}
                })
        },
        'metrics': {
            'mode': 'production',
            'template': 'node_metrics.html',
            'function_array': metrics_functions,
            'arguments': sessionCreate({
                    'auth': {'user': PROM_USER, 'pass': PROM_PASS}
                })
        },
        'blob': {
            'mode': 'production',
            'template': 'blob.html',
            'function_array': blob_functions,
            'arguments': initClickhouseClient()
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
            'function_array': testing_functions,
            'arguments': sessionCreate({
                    'auth': {'user': PROM_USER, 'pass': PROM_PASS}
                })
        }
    }

    dashboard_args = options.get('-d')

    # Choosing to generate a specific dashboard(s)
    if (dashboard_args):
        new_dashboards = {}
        dashboard_n_args = len(dashboard_args)

        if (dashboard_n_args == 0):
            noticePrint(f'Please provide a dashboard to generate.')
            exit(1)

        for index in range(0, dashboard_n_args):
            dashboard_name = dashboard_args[index]

            if (not dashboards.get(dashboard_name)):
                noticePrint(f'Please provide a valid dashboard name.')
                exit(1)

            new_dashboards[dashboard_name] = dashboards[dashboard_name]
        dashboards = new_dashboards

    if (getRootPath()):
        if (not list_testing_mode):  # Normal Dashboard
            noticePrint(f'Generating dashboards...')
            createDashboards(dashboards)

        if (testing_functions):
            if (list_testing_mode):  # When you specify test functions
                noticePrint(f'Generating plot testing page...')
                createDashboards(dashboards, 'list testing')
            else:
                noticePrint(f'Generating test dashboards...')
                createDashboards(dashboards, 'testing')

        noticePrint(f'Successfully generated the dashboard. {NOW}')
    else:
        noticePrint(f'''Please provide the absolute path of the project without
                     a slash at the end. {NOW}''')
        exit(1)


if __name__ == '__main__':
    main()

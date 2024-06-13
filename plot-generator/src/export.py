import os

ABS_PATH = os.path.dirname(os.path.abspath(__file__)) + '/..'


# will only generate the dashboards of the specified mode
# 'production' will save the dashboard at /
# 'testing' at /test and can have different plots (added to its function array)
# 'list testing' will only generate the plots you specify in args
# you choose an index according to the function array
# (-t 1 is first function in array, etc)
def dashboard_dict_execute(dashboards, mode='production') -> None:
    replaceHandler = html_replace_by_list if (mode == 'list testing') else html_replace_by_plotname
    # replaceByList is used only when you specify which to generate
    template_path, save_path = f'{ABS_PATH}/templates', f'{ABS_PATH}/generated'

    if (mode == 'testing'):
        template_path = f'{template_path}/test_templates'
        save_path = f'{save_path}/test'

    for (dashboard, values) in (dashboards.items()):
        dashboard_mode = values['mode']
        if ((mode != dashboard_mode) or not values['function_array']):
            continue
        print(f"\n** {dashboard} dashboard's plots **\n")
        filename = values['template']
        divs = plot_get_divs(values['function_array'], values['arguments'])

        final_html = plot_get_HTML(
            divs, f'{template_path}/{filename}', replaceHandler
        )
        file_write(f'{save_path}/{filename}', final_html)


def file_write(filename, contents) -> None:
    with open(filename, 'w') as file:
        file.write(contents)


# Will call all functions and append the result into plots_dict
# ALl functions are expected to return {plotname: plot_div}
def plot_get_divs(functions, argument) -> dict:
    plots_dict = {}

    for function in functions:
        plots_dict.update(function(argument))

    return (plots_dict)


# This will append all function result's 'plot_div's into a big string
# And then put them inside of the list_testing file (templates/testing.html)
# At the moment
# This is the function used when choosing plots from index with -t
def html_replace_by_list(html, plots_dict) -> str:
    plot_string = ''

    for plot, plot_div in plots_dict.items():
        if (not plot):
            continue
        plot_string = f'{plot_string}{plot_div}\n'

    html = html.replace('<!-- testing -->', plot_string)

    return (html)


# Function used normally (not list_testing mode)
# Will replace target comments with the corresponding plot name
def html_replace_by_plotname(html, plots_dict) -> str:
    for plot, plot_div in plots_dict.items():
        if (not plot):
            continue
        html = html.replace(f'<!-- {plot} -->', plot_div)

    return (html)


# Will get the final dashboard HTML
def plot_get_HTML(plots_dict, template, replaceHandler) -> str:
    with open(template, 'r') as file:
        html = file.read()

    html = replaceHandler(html, plots_dict)

    return (html)

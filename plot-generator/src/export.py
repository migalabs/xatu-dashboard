import os

ABS_PATH = os.path.dirname(os.path.abspath(__file__)) + '/..'


def dashboard_dict_export(dashboards, mode='production') -> None:
    '''
    Generate the dashboards of the specified mode.

    modes:

    'production': Save the dashboard at /

    'testing': Save at /test

    'list testing': Only generate the plots specified by
    choosing an index according to the function array
    (-t 1 is first function in the array, etc)

    Won't export all dashboards,
    only the ones with the matching mode!
    '''
    replace_handler = html_replace_by_plotname
    template_path, save_path = f'{ABS_PATH}/templates', f'{ABS_PATH}/generated'

    if (mode == 'list testing'):
        replace_handler = html_replace_by_list
    if (mode == 'testing'):
        template_path = f'{template_path}/test_templates'
        save_path = f'{save_path}/test'

    for (dashboard, values) in (dashboards.items()):
        dashboard_mode = values['mode']
        if ((mode != dashboard_mode) or not values['function_array']):
            continue
        print(f"\n** {dashboard} dashboard's plots **\n")
        filename = values['template']
        # Generate plots and get them as HTML
        divs = plot_get_divs(values['function_array'], values['arguments'])
        # Insert into template
        final_html = plot_get_HTML(divs, f'{template_path}/{filename}', replace_handler)
        file_write(f'{save_path}/{filename}', final_html)  # Output to save path


def file_write(filename, contents) -> None:
    with open(filename, 'w') as file:
        file.write(contents)


def plot_get_divs(functions, argument) -> dict:
    '''
    Call all functions in `functions` and append the result into plots_dict.

    Generators are expected to return in `{plotname: plot_div}`
    '''
    plots_dict = {}

    for function in functions:
        plots_dict.update(function(argument))

    return (plots_dict)


def html_replace_by_list(html, plots_dict) -> str:
    '''
    Append all function results (plot_div) into a big string
    and then put them inside of the dev dashboard's template.
    '''
    plot_string = ''

    for plot, plot_div in plots_dict.items():
        if (not plot):
            continue
        plot_string = f'{plot_string}{plot_div}\n'

    html = html.replace('<!-- testing -->', plot_string)

    return (html)


def html_replace_by_plotname(html, plots_dict) -> str:
    '''
    Replace target comments with the corresponding plotname
    '''
    for plot, plot_div in plots_dict.items():
        if (not plot):
            continue
        html = html.replace(f'<!-- {plot} -->', plot_div)

    return (html)


def plot_get_HTML(plots_dict, template, replace_handler) -> str:
    '''
    Use `replace_handler` to insert the plot divs into the file `template`
    '''
    with open(template, 'r') as file:
        html = file.read()

    html = replace_handler(html, plots_dict)

    return (html)

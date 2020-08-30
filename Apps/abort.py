from dearpygui.dearpygui import *

set_theme('Gold')
set_main_window_title('TVMaze Management - Production DB')

add_menu_bar("Menu")
add_menu("Tools")
add_menu_item('View Console', callback='view_console')
add_menu_item('View Script Errors', callback='view_errors')
add_menu("Debug")
add_menu_item("About", callback="show_about")
add_menu_item("Metrics", callback="show_metrics")
add_menu_item("Documentation", callback="show_documentation")
add_menu_item("Debug##UI", callback="show_debug")
end_menu('Debug')
end_menu('Tools')
end_menu_bar('Menu')
add_seperator()


def refresh_console(sender, data):
    mode = get_data('mode')
    if mode == 'Test':
        logfile = '/Volumes/HD-Data-CA-Server/Development/PycharmProjects/TVM-Management/Apps/out.log'
    else:
        logfile = '/Volumes/HD-Data-CA-Server/Development/PycharmProjects/TVM-Management/Apps/Logs/gui.log'
    try:
        file = open(logfile, 'r')
    except IOError as err:
        log_warning(f'Console log file IOError: {err}')
        return
    log_info(f'refresh console file: {sender}, {data}')
    consolelines = file.readlines()
    table = []
    for line in consolelines:
        table.append([line.replace("\n", "")])
    set_value('console_table', table)
    file.close()


def refresh_errors(sender, data):
    mode = get_data('mode')
    if mode == 'Test':
        logfile = '/Volumes/HD-Data-CA-Server/Development/PycharmProjects/TVM-Management/Apps/err.log'
    else:
        logfile = '/Volumes/HD-Data-CA-Server/Development/PycharmProjects/TVM-Management/Apps/Logs/gui_err.log'
    try:
        file = open(logfile, 'r')
    except IOError as err:
        log_warning(f'Error log file IOError: {err}')
        return
    log_info(f'refresh error log: {sender}, {data}')
    errorlines = file.readlines()
    table = []
    for line in errorlines:
        table.append([line.replace("\n", "")])
    set_value('errors_table', table)
    file.close()


def view_console(sender, data):
    log_info(f'View Console with {sender} and data {data}')
    add_window(f'View Console##{sender}', on_close="fs_close")
    set_style_window_title_align(0.5, 0.5)
    add_button(f'Refresh Console', callback='refresh_console')
    add_spacing(count=2)
    add_seperator()
    add_table(f'console_table',
              headers=['Console - Info'])
    refresh_console(sender, data)
    end_window()


def view_errors(sender, data):
    log_info(f'View Errors with {sender} and data {data}')
    add_window(f'View Errors##{sender}', on_close="fs_close")
    set_style_window_title_align(0.5, 0.5)
    add_button(f'Refresh Error Log', callback='refresh_errors')
    add_spacing(count=2)
    add_seperator()
    add_table(f'errors_table',
              headers=['Error - Info'])
    refresh_errors(sender, data)
    end_window()

def set_logging_T(sender, data):
    set_log_level(mvTRACE)


def set_logging_D(sender, data):
    set_log_level(mvDEBUG)


def set_logging_I(sender, data):
    set_log_level(mvINFO)


def set_logging_W(sender, data):
    set_log_level(mvWARNING)


def set_logging_E(sender, data):
    set_log_level(mvERROR)


def set_logging_O(sender, data):
    set_log_level(mvOFF)

start_dearpygui()
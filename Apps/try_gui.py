from dearpygui.dearpygui import *
import requests
import os
import subprocess

from db_lib import execute_sql

add_data('follow', False)
add_data('unfollow', False)
add_data('skip', False)
add_data('find', False)
add_data('selected', False)
add_data('showid', 0)
add_data('mode', 'Prod')

set_theme('Gold')
set_main_window_title('TVMaze Management')

add_menu_bar("Menu")
add_menu("Shows")
add_menu_item('Follow', callback='follow_show')
add_menu_item('Unfollow', callback='unfollow_show')
add_menu_item('Start Skipping', callback='skip_show')
add_menu_item('Find Downloads', callback='find_downloads')
end_menu("Shows")

add_menu('TVMaze')
add_menu('Logs')
add_menu_item('Full run Log', callback='run_log')
add_menu_item('Transmission Log', callback='transmission_log')
add_menu_item('Plex Watched Log', callback='plex_watched_log')
add_menu_item('Plex Cleanup Log', callback='plex_cleanup_log')
end_menu('TVMaze')
add_menu('Programs')
add_menu_item('Run Shows', callback='run_shows')
add_menu_item('Run Episodes', callback='run_episodes')
end_menu('Programs')
add_menu_item('Misc', callback='misc')
end_menu('Processes')

add_menu('Statistics')
add_menu_item('Overview', callback='stats_on_web')
add_menu_item('Interactive', callback='stats_interactive')
end_menu('Statistics')

add_menu("Tools")
add_menu("Log Level")
add_menu_item('Trace', callback='set_logging_T')
add_menu_item('Debug##LL', callback='set_logging_D')
add_menu_item('Info', callback='set_logging_I')
add_menu_item('Warning', callback='set_logging_W')
add_menu_item('Error', callback='set_logging_E')
add_menu_item('Off', callback='set_logging_O')
end_menu('Log Level')

add_menu_item("View Log", callback="show_logger")
add_menu_item('View Console', callback='view_console')
add_menu_item('View Script Errors', callback='view_errors')
add_menu_item("Toggle DB", callback='toggle_db')

add_menu("UI")
add_menu_item("About", callback="show_about")
add_menu_item("Metrics", callback="show_metrics")
add_menu_item("Documentation", callback="show_documentation")
add_menu_item("Debug##UI", callback="show_debug")
end_menu('UI')
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
    log_info(f'refresh error file: {sender}, {data}')
    errorlines = file.readlines()
    table = []
    for line in errorlines:
        table.append([line.replace("\n", "")])
    set_value('errors_table', table)
    file.close()
    

def refresh_run_log(sender, data):
    file = open('/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/30M-Process.log', 'r')
    log_info(f'refresh error file: {sender}, {data}')
    lines = file.readlines()
    table = []
    for line in lines:
        table.append([line.replace("\n", "")])
    set_value('run_log_table', table)
    file.close()


def view_console(sender, data):
    log_info(f'View Console with {sender} and data {data}')
    add_window(f'View Console##{sender}', on_close="fs_close")
    set_style_window_title_align(0.5, 0.5)
    add_button(f'Refresh Console', callback='refresh_console')
    add_table(f'console_table',
              headers=['Console - Info'])
    refresh_console(sender, data)
    end_window()


def view_errors(sender, data):
    log_info(f'View Errors with {sender} and data {data}')
    add_window(f'View Errors##{sender}', on_close="fs_close")
    set_style_window_title_align(0.5, 0.5)
    add_button(f'Refresh Error Log', callback='refresh_errors')
    add_table(f'errors_table',
              headers=['Error - Info'])
    refresh_errors(sender, data)
    end_window()
    
    
def run_log(sender, data):
    log_info(f'View Run Log with {sender} and data {data}')
    add_window(f'View Run Log##{sender}', 1250, 750, start_x=15, start_y=35, resizable=True, movable=True,
               on_close="fs_close")
    set_style_window_title_align(0.5, 0.5)
    add_button(f'Refresh Run Log', callback='refresh_run_log')
    add_table(f'run_log_table',
              headers=['Run Log - Info'])
    refresh_run_log(sender, data)
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


def find_shows(si, sn):
    log_info(f'Find Shows SQL with showid {si} and showname {sn}')
    showid = get_data('showid')
    if showid != 0:
        sql = f'select showid, showname, network, type, showstatus, status, premiered ' \
              f'from shows where `showid` = {si}'
    else:
        sql = f'select showid, showname, network, type, showstatus, status, premiered ' \
              f'from shows where `showname` like "{sn}" order by premiered desc'
    if get_data('mode') == 'Prod':
        fs = execute_sql(sqltype='Fetch', sql=sql)
    else:
        fs = execute_sql(sqltype='Fetch', sql=sql, d='Test-TVM-DB')
    return fs


def tvm_follow(fl, si):
    info_api = 'https://api.tvmaze.com/v1/user/follows/shows/' + str(si)
    if fl == "F":
        shows = requests.put(info_api,
                             headers={'Authorization':
                                          'Basic RGlja0tsdWlzOlRUSFlfQ2hIeUF5SU1fV1ZZRmUwcDhrWTkxTkE1WUNH'})
        if shows.status_code != 200:
            log_error(f"Error trying to follow show: {si}, {shows.status_code}")
            return False
    elif fl == "U":
        shows = requests.delete(info_api,
                                headers={'Authorization':
                                             'Basic RGlja0tsdWlzOlRUSFlfQ2hIeUF5SU1fV1ZZRmUwcDhrWTkxTkE1WUNH'})
        if shows.status_code != 200 and shows.status_code != 404:
            log_error(f"Error trying to follow show: {si}, {shows.status_code}")
            return False
    return True


def toggle_db(sender, data):
    if get_data('mode') == 'Prod':
        add_data('mode', 'Test')
        set_main_window_title('TVMaze Management - Test DB Access')
    else:
        add_data('mode', 'Prod')
        set_main_window_title('TVMaze Management')


def fs_close(sender, data):
    log_info(f'Close Find Show with sender {sender} and data {data}')
    if 'Follow' in str(sender):
        add_data('follow', False)
    elif 'Unfollow' in str(sender):
        add_data('unfollow', False)
    elif 'Skip' in str(sender):
        add_data('skip', False)
    elif 'Find' in str(sender):
        add_data('find', False)
    delete_item(sender)


def table_click(sender, data):
    log_info(f'Table Click with sender {sender} and data {data}')
    window = str(sender).split('##')[1]
    row_cell = get_table_selections(f'fs_table##{window}')
    row = row_cell[0][0]
    add_data('selected', True)
    showid = get_value(f'fs_table##{window}')[row][0]
    add_data('showid', showid)
    showname = get_value(f'fs_table##{window}')[row][1]
    set_value(f'##SB{window}', f"Selected Show: {showid}, {showname}")
    set_value(f'Show ID##{window}', int(showid))
    set_value(f'Show Name##{window}', showname)
    log_info(f'Table Click for row cell {row_cell} selected showid {showid}')
    for sel in row_cell:
        set_table_selection(f'fs_table##{window}', sel[0], sel[1], False)


def stats_on_web(sender, data):
    log_info(f'Stats on Web with sender {sender} and data {data}')
    follow_str = 'open -a safari http://127.0.0.1:8050'
    os.system(follow_str)
    try:
        subprocess.call("python3 /Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Apps/visualize.py",
                        shell=True)
    except KeyboardInterrupt:
        pass


def stats_interactive(sender, data):
    log_info(f'Stats Interactive with sender {sender} and data {data}')


def clear_fs_show(sender, data):
    log_info(f'Clear with sender {sender} and data {data}')
    window = str(sender).split('##')[1]
    set_value(f'Show ID##{window}', 0)
    set_value(f'Show Name##{window}', '')
    set_value(f'fs_table##{window}', [])
    set_value(f'##SB{window}', '')
    add_data('selected', False)


def view_tvmaze(sender, data):
    window = str(sender).split('##')[1]
    selected = get_data('selected')
    if not selected:
        set_value(f'##SB{window}', 'No Show was selected yet, nothing to do yet')
    else:
        window = str(sender).split('##')[1]
        get_value(f'Show ID##{window}')
        tvm_link = "  https://www.tvmaze.com/shows/" + str(get_value(f'Show ID##{window}'))
        follow_str = 'open -a safari ' + tvm_link
        os.system(follow_str)


def execute_shows(sender, data):
    showid = get_data('showid')
    selected = get_data('selected')
    log_info(f'Executing Submit for Shows with sender {sender} and data {data} with showid {showid}')
    window = str(sender).split('##')[1]
    if not selected:
        set_value(f'##SB{window}', 'No Show was selected yet, nothing to do yet')
    else:
        if window == 'Follow':
            result = tvm_follow('F', showid)
            log_info(f'TVMaze Follow result: {result}')
            set_value(f'##SB{window}', f'Show {showid} update on TVMaze and set Follow = {result}')
            add_data('selected', False)
        elif window == 'Unfollow':
            result = tvm_follow('U', showid)
            log_info(f'TVMaze Unfollow result: {result}')
            set_value(f'##SB{window}', f'Show {showid} update on TVMaze and set Unfollow = {result}')
            add_data('selected', False)


def find_show(sender, data):
    print(f'Find Show {sender}, {data}', flush=True)
    if sender == 'Follow':
        y = 35
    elif sender == 'Unfollow':
        y = 55
    elif sender == 'Start Skipping':
        y = 75
    else:
        y = 95
    
    log_info(f'Find Show with sender {sender} and data {data}')
    add_window(f'{data}##{sender}', 1250, 600, start_x=15, start_y=y, resizable=True, movable=True,
               on_close="fs_close")
    set_style_window_title_align(0.5, 0.5)
    add_input_int(f'Show ID##{sender}', width=250, data_source='showid')
    add_input_text(f'Show Name##{sender}', hint='Use % as wild-card', width=250, data_source='showname')
    add_button(f'Clear##{sender}', callback='clear_fs_show')
    add_same_line(spacing=10)
    add_button(f'Search##{sender}', callback='fill_fs_table')
    add_seperator()
    add_input_text(f'##SB{sender}', readonly=True, default_value='', width=750)
    add_same_line(spacing=25)
    add_button(f'View on TVMaze##{sender}', callback='view_tvmaze')
    add_same_line(spacing=10)
    add_button(f'Submit##{sender}', callback=f'execute_shows')
    add_seperator()
    add_spacing()
    add_table(f'fs_table##{sender}',
              headers=['Show ID', 'Show Name', 'Network', 'Type', 'Status', 'My Status', 'Premiered'],
              callback=f'table_click')
    end_window()


def fill_fs_table(sender, data):
    log_info(f'Fill FS Table with sender {sender} and data {data}')
    window = str(sender).split('##')[1]
    showid = get_value(f'Show ID##{window}')
    add_data('showid', showid)
    showname = get_value(f'Show Name##{window}')
    if showid == 0 and showname == '':
        set_value(f'##SB{window}', 'Nothing was entered in Show ID or Showname')
    
    log_info(f'showid: {showid} - showname: {showname}')
    found_shows = find_shows(showid, showname)
    table = []
    for rec in found_shows:
        table_row = []
        for field in rec:
            table_row.append(field)
        table.append(table_row)
    set_value(f'fs_table##{window}', table)


def follow_show(sender, data):
    if get_data('follow'):
        log_info(f'Follow Show already running with sender {sender} and data {data}')
    else:
        log_info(f'Follow Show with sender {sender} and data {data}')
        find_show(sender, 'Follow a Show')
        add_data('follow', True)


def unfollow_show(sender, data):
    if get_data('unfollow'):
        log_info(f'Unfollow Show already running with sender {sender} and data {data}')
    else:
        log_info(f'Unfollow Show with sender {sender} and data {data}')
        find_show(sender, 'Unfollow a Show')
        add_data('unfollow', True)


def skip_show(sender, data):
    if get_data('skip'):
        log_info(f'Skip Show already running with sender {sender} and data {data}')
    else:
        log_info(f'Skip Show with sender {sender} and data {data}')
        find_show(sender, 'Skip a Show')
        add_data('skip', True)


def find_downloads(sender, data):
    if get_data('find'):
        log_info(f'Find Downloads already running with sender {sender} and data {data}')
    else:
        log_info(f'Find Downloads with sender {sender} and data {data}')
        find_show(sender, 'Find Downloads')
        add_data('find', True)


start_dearpygui()

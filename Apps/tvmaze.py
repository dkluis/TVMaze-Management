"""

tvmaze.py   The App that is the UI to all TVMaze function.

Usage:
  actions.py [-p]
  actions.py -h | --help
  actions.py --version

Options:
  -h --help      Show this screen
  -p             Start in Production mode, otherwise it starts in Test mode.
                 Production or Test DB and Production or Test Log Files

"""

from dearpygui.dearpygui import *
import subprocess
import os
import requests
from docopt import docopt
import time

from tvm_lib import execute_sql


def func_breakout_window(sender, pos):
    window = str(sender).split('##')[pos]
    return window


def func_db_opposite():
    log_info(f'Retrieving Mode {get_data("mode")}')
    if get_data('mode') == 'Prod':
        add_data('db_opposite', 'Test DB')
    else:
        add_data('db_opposite', "Production DB")
        

def func_exec_sql(func, sql):
    if get_data('mode') == 'Prod':
        res = execute_sql(sqltype=func, sql=sql)
    else:
        res = execute_sql(sqltype=func, sql=sql, d='Test-TVM-DB')
    log_info(f'SQL {sql} executed {res}')


def func_find_shows(si, sn):
    log_info(f'Find Shows SQL with showid {si} and showname {sn}')
    if si == 0 and sn == 'New':
        sql = f'select showid, showname, network, type, showstatus, status, premiered, download ' \
              f'from shows where status = "New" or status = "Undecided" order by download, showid'
    else:
        showid = get_data('shows_showid')
        if showid != 0:
            sql = f'select showid, showname, network, type, showstatus, status, premiered, download ' \
                  f'from shows where `showid` = {si}'
        elif sn != '':
            sql = f'select showid, showname, network, type, showstatus, status, premiered, download ' \
                  f'from shows where `showname` like "{sn}" order by premiered desc'
        else:
            return []
    if get_data('mode') == 'Prod':
        fs = execute_sql(sqltype='Fetch', sql=sql)
    else:
        fs = execute_sql(sqltype='Fetch', sql=sql, d='Test-TVM-DB')
    return fs


def func_tvm_f_u(fl, si):
    log_info(f'TVMaze update {fl}, {si}')
    api = f'https://api.tvmaze.com/v1/user/follows/shows/{si}'
    if fl == "F":
        shows = requests.put(api,
                             headers={'Authorization':
                                      'Basic RGlja0tsdWlzOlRUSFlfQ2hIeUF5SU1fV1ZZRmUwcDhrWTkxTkE1WUNH'})
        if shows.status_code != 200:
            log_error(f"Web error trying to follow show: {si}, {shows.status_code}")
            return False
        success = 'Followed'
        download = 'Multi'
    elif fl == "U":
        shows = requests.delete(api,
                                headers={'Authorization':
                                         'Basic RGlja0tsdWlzOlRUSFlfQ2hIeUF5SU1fV1ZZRmUwcDhrWTkxTkE1WUNH'})
        if shows.status_code != 200 and shows.status_code != 404:
            log_error(f"Web error trying to unfollow show: {si}, {shows.status_code}")
            return False
        success = 'Skipped'
        download = None
    sql = f'update shows set status = "{success}", download = "{download}" where `showid` = {si}'
    sql = sql.replace('"None"', 'NULL')
    func_exec_sql('Commit', sql)
    return True


def func_toggle_db(sender, data):
    if get_data('mode') == 'Prod':
        add_data('mode', 'Test')
        add_data('db_opposite', 'Production DB')
        set_main_window_title(f'TVMaze Management - Test DB')
    else:
        add_data('mode', 'Prod')
        add_data('db_opposite', 'Test DB')
        set_main_window_title(f'TVMaze Management - Production DB')
    log_info(f'Toggled the DB access')
    
    
def func_toggle_theme(sender, data):
    ot = get_data('theme_opposite')
    set_theme(str(ot))
    if ot == 'Dark':
        add_data('theme_opposite', 'Gold')
    else:
        add_data('theme_opposite', 'Dark')
        

def graph_execute_get_data(sql, sender, pi):
    log_info(f'Filling the plot data for {sender} with {sql}')
    if get_data('mode') == 'Prod':
        data = execute_sql(sqltype='Fetch', sql=sql)
        log_info('Getting Prod Data')
    else:
        data = execute_sql(sqltype='Fetch', sql=sql, d='Test-TVM-DB')
        log_info('Getting Test Data')
    plot_index = sender
    if sender == 'Other Shows':
        plot_index = pi
    add_line_series(f'{sender}##plot', plot_index, data)
    # ToDo Figure graph call back from auto refresh option
    # set_render_callback('graph_render_callback')


def graph_get_data(sender):
    log_info(f'Grabbing the graphs for {sender}')
    data = []
    if sender == 'All Shows':
        sql = f'select statepoch, tvmshows from statistics where statrecind = "TVMaze"'
    elif sender == 'Followed Shows':
        sql = f'select statepoch, myshows from statistics where statrecind = "TVMaze"'
    elif sender == 'In Development Shows':
        sql = f'select statepoch, myshowsindevelopment from statistics where statrecind = "TVMaze"'
    elif sender == 'All Episodes':
        sql = f'select statepoch, myepisodes from statistics where statrecind = "TVMaze"'
    elif sender == "Watched Episodes":
        sql = f'select statepoch, myepisodeswatched from statistics where statrecind = "TVMaze"'
    elif sender == "Episodes to Watch":
        sql = f'select statepoch, myepisodestowatch from statistics where statrecind = "TVMaze"'
    elif sender == "Upcoming Episodes":
        sql = f'select statepoch, myepisodesannounced from statistics where statrecind = "TVMaze"'
    elif sender == "Episodes to Get":
        sql = f'select statepoch, myepisodestodownloaded from statistics where statrecind = "TVMaze"'
    elif sender == "Skipped Episodes":
        sql = f'select statepoch, myepisodesskipped from statistics where statrecind = "TVMaze"'
    elif sender == 'Other Shows':
        graph_refresh_other('Other Shows')
        return
    else:
        add_line_series(f'{sender}##plot', "Unknown", data)
        return
    graph_execute_get_data(sql, sender, data)


def graph_refresh(sender, data):
    log_info(f'Refreshing Graph Data for {sender}')
    if '##' in sender:
        requester = func_breakout_window(sender, 1)
    else:
        requester = sender
    graph_get_data(requester)


def graph_refresh_other(sender):
    log_info(f'Graph refresh for all Others')
    if sender != 'Other Shows':
        return
    sql = f'select statepoch, myshowsended from statistics where statrecind = "TVMaze"'
    graph_execute_get_data(sql, 'Other Shows', 'Ended')
    sql = f'select statepoch, myshowsrunning from statistics where statrecind = "TVMaze"'
    graph_execute_get_data(sql, 'Other Shows', 'Running')
    sql = f'select statepoch, myshowstbd from statistics where statrecind = "TVMaze"'
    graph_execute_get_data(sql, 'Other Shows', 'TBD')
    
    
# Todo part of the render callback todo
"""
def graph_render_callback(sender, data):
    log_info(f'Graph Render Callback Triggered {sender} {data}')
"""


def program_callback(sender, data):
    log_info(f'Main Callback activated {sender}, {data}')
    if sender == 'Shows':
        sql = f'select count(*) from shows where status = "New" or status = "Undecided"'
        if get_data('mode') == 'Prod':
            count = execute_sql(sqltype='Fetch', sql=sql)
        else:
            count = execute_sql(sqltype='Fetch', sql=sql, d='Test-TVM-DB')
        add_data('shows_ds_new_shows', f': {str(count[0][0])}')


def program_data():
    add_data('shows_ds_new_shows', '0')
    add_data('shows_showid', 0)
    add_data('selected', False)
    add_data('theme_opposite', 'Dark')
    add_data('label##All Shows', "All the shows that are available on TVMaze")
    add_data('label##Followed Shows', "Only the followed shows")
    add_data('label##In Development Shows', "Only the followed shows that have not started yet")
    add_data('label##Other Shows',
             "Only the followed shows that are currently 'Running', have 'Ended' or are 'In Limbo")
    add_data('label##All Episodes', "All episodes (followed shows only)")
    add_data('label##Watched Episodes', "All watched episodes (followed shows only)")
    add_data('label##Skipped Episodes', "All skipped episodes (followed shows only)")
    add_data('label##Episodes to Get', "All episodes to get onto Plex (followed shows only)")
    add_data('label##Episodes to Watch', "All available episodes on Plex not watched yet (followed shows only)")
    add_data('label##Upcoming Episodes', "All announced episodes beyond today (followed shows only)")


def program_mainwindow():
    if get_data('mode') == 'Test':
        set_main_window_title(f'TVMaze Management - Test DB')
    else:
        set_main_window_title('TVMaze Management - Production DB')
    set_style_window_title_align(0.5, 0.5)
    set_main_window_size(2140, 1210)
    set_theme('Gold')
    
    add_menu_bar('Menu Bar')
    
    add_menu('TVMaze')
    add_menu_item('Calendar', callback='tvmaze_calendar', tip='Starts in Safari')
    add_spacing(count=1)
    add_seperator()
    add_spacing(count=1)
    add_menu_item('Quit', callback='window_quit')
    end_menu()
    
    add_menu('Shows')
    add_menu_item('Eval New Shows', callback='window_shows')
    add_same_line(xoffset=115)
    add_label_text('##no_new_shows', value='0', data_source='shows_ds_new_shows', color=[250, 250, 0, 250])
    add_spacing(count=1)
    add_seperator()
    add_spacing(count=1)
    add_menu_item('Show Maintenance', callback='window_shows')
    add_menu('Graphs##shows')
    add_menu_item('All Shows', callback='window_graphs')
    add_menu_item('Followed Shows', callback='window_graphs')
    add_menu_item('In Development Shows', callback='window_graphs')
    add_menu_item('Other Shows', callback='window_graphs')
    add_spacing(count=1)
    add_seperator()
    add_spacing(count=1)
    add_menu_item('All Graphs##Shows', callback='window_shows_all_graphs')
    end_menu()
    end_menu()
    
    add_menu('Episodes', tip='Only of Followed Shows')
    add_menu_item('Search', callback='window_episodes')
    add_menu('Graphs##episodes')
    add_menu_item('All Episodes', callback='window_graphs')
    add_menu_item('Skipped Episodes', callback='window_graphs')
    add_menu_item('Watched Episodes', callback='window_graphs')
    add_menu_item('Episodes to Get', callback='window_graphs')
    add_menu_item('Episodes to Watch', callback='window_graphs')
    add_menu_item('Upcoming Episodes', callback='window_graphs')
    add_spacing(count=1)
    add_seperator()
    add_spacing(count=1)
    add_menu_item('All Graphs##episodes', callback='window_episodes_all_graphs')
    end_menu()
    end_menu()
    
    add_menu('Tools')
    add_menu_item('Toggle Database to', callback='func_toggle_db')
    add_same_line(xoffset=140)
    add_label_text(f'##db', value='Test', data_source='db_opposite', color=[250, 250, 0, 250])
    add_menu_item('Toggle Theme to', callback='func_toggle_theme')
    add_same_line(xoffset=140)
    add_label_text(f'##theme', value='Gold', data_source='theme_opposite', color=[250, 250, 0, 250])
    add_spacing(count=1)
    add_seperator()
    add_spacing(count=1)
    add_menu_item('Test Window for Tabs', callback='window_tests')
    end_menu()
    
    add_menu('Windows')
    add_menu_item('Close Open Windows', callback='window_close_all')
    add_menu_item('Get Open Window Positions', callback='window_get_pos')
    end_menu()
    
    end_menu_bar()

    set_render_callback('program_callback', 'Shows')


def show_fill_table(sender, data):
    log_info(f'Fill Show Table {sender} {data}')
    window = func_breakout_window(sender, 1)
    showid = get_value(f'Show ID##{window}')
    add_data('shows_showid', showid)
    showname = get_value(f'Show Name##{window}')
    if showid == 0 and showname == '':
        set_value(f'##show_showname{window}', 'Nothing was entered in Show ID or Showname')
    
    log_info(f'showid: {showid} - showname: {showname}')
    if window == 'Show Maintenance':
        found_shows = func_find_shows(showid, showname)
    else:
        found_shows = func_find_shows(0, 'New')
    table = []
    for rec in found_shows:
        table_row = []
        for field in rec:
            table_row.append(field)
        table.append(table_row)
    set_value(f'shows_table##{window}', table)


def show_maint_clear(sender, data):
    log_info(f'Show Maint clear {sender} {data}')
    window = func_breakout_window(sender, 1)
    set_value(f'Show ID##{window}', 0)
    set_value(f'Show Name##{window}', '')
    set_value(f'shows_table##{window}', [])
    set_value(f'##show_name{window}', '')
    add_data('selected', False)
    set_value(f'##show_showname{window}', "")


def shows_table_click(sender, data):
    log_info(f'Shows Table Click {sender} {data}')
    window = func_breakout_window(sender, 1)
    row_cell = get_table_selections(f'shows_table##{window}')
    row = row_cell[0][0]
    add_data('selected', True)
    showid = get_value(f'shows_table##{window}')[row][0]
    add_data('showid', showid)
    showname = get_value(f'shows_table##{window}')[row][1]
    set_value(f'##show_showname{window}', f"Selected Show: {showid}, {showname}")
    set_value(f'Show ID##{window}', int(showid))
    set_value(f'Show Name##{window}', showname)
    log_info(f'Table Click for row cell {row_cell} selected showid {showid}')
    for sel in row_cell:
        set_table_selection(f'shows_table##{window}', sel[0], sel[1], False)
        
        
def tvmaze_calendar(sender, data):
    log_info('TVM Calendar started in Safari')
    subprocess.call("open -a safari  https://www.tvmaze.com/calendar", shell=True)
    

def tvmaze_f_u_show(sender, data):
    log_info(f'TVMaze follow unfollow {sender}, {data}')
    window = func_breakout_window(sender, 1)
    function = func_breakout_window(sender, 0)
    selected = get_data('selected')
    si = get_value(f'Show ID##{window}')
    if not selected:
        set_value(f'##show_showname{window}', 'No Show was selected yet, nothing to do yet')
    else:
        if function == 'Follow':
            result = func_tvm_f_u('F', si)
            log_info(f'TVMaze Follow result: {result}')
            set_value(f'##show_showname{window}', f'Show {si} update on TVMaze and set Follow = {result}')
        elif function == 'Unfollow':
            result = func_tvm_f_u('U', si)
            log_info(f'TVMaze Unfollow result: {result}')
            set_value(f'##show_showname{window}', f'Show {si} update on TVMaze and set Unfollow = {result}')
    

def tvmaze_view_show(sender, data):
    window = func_breakout_window(sender, 1)
    selected = get_data('selected')
    if not selected:
        set_value(f'##show_showname{window}', 'No Show was selected yet, nothing to do yet')
    else:
        si = get_value(f'Show ID##{window}')
        tvm_link = f"https://www.tvmaze.com/shows/{si}"
        follow_str = 'open -a safari ' + tvm_link
        os.system(follow_str)


def window_close(sender, data):
    window = f'{sender}'
    delete_item(window)
    log_info(f'Delete item (window): "{window}"')
    

def window_close_all(sender, data):
    log_info('Close Open Windows')
    all_windows = get_windows()
    for window in all_windows:
        log(f'Processing to close: {window}')
        if 'MainWindow' in window:
            continue
        log_info(f'Closing window found: {window}')
        delete_item(window)
        

def window_episodes_all_graphs(sender, data):
    window_graphs('All Episodes', None)
    set_window_pos('All Episodes##graphs', 15, 35)
    set_item_width('All Episodes##graphs', 690)
    set_item_height('All Episodes##graphs', 515)
    window_graphs('Skipped Episodes', None)
    set_window_pos('Skipped Episodes##graphs', 720, 35)
    set_item_width('Skipped Episodes##graphs', 690)
    set_item_height('Skipped Episodes##graphs', 515)
    window_graphs('Watched Episodes', None)
    set_window_pos('Watched Episodes##graphs', 1420, 35)
    set_item_width('Watched Episodes##graphs', 690)
    set_item_height('Watched Episodes##graphs', 515)
    window_graphs('Episodes to Get', None)
    set_window_pos('Episodes to Get##graphs', 15, 570)
    set_item_width('Episodes to Get##graphs', 690)
    set_item_height('Episodes to Get##graphs', 515)
    window_graphs('Episodes to Watch', None)
    set_window_pos('Episodes to Watch##graphs', 720, 570)
    set_item_width('Episodes to Watch##graphs', 690)
    set_item_height('Episodes to Watch##graphs', 515)
    window_graphs('Upcoming Episodes', None)
    set_window_pos('Upcoming Episodes##graphs', 1420, 570)
    set_item_width('Upcoming Episodes##graphs', 690)
    set_item_height('Upcoming Episodes##graphs', 515)


def window_get_pos(sender, data):
    all_windows = get_windows()
    log_info(f'Log Open Window Positions for {all_windows}')
    for window in all_windows:
        if window == 'MainWindow':
            continue
        data = get_window_pos(window)
        log_info(f'Position for: {window} is {data[0]}, {data[1]}')


def window_graphs(sender, data):
    window = f'{sender}##graphs'
    if not does_item_exist(window):
        add_window(window, 1250, 600, start_x=15, start_y=35, resizable=True, movable=True, on_close="window_close")
        add_button(f'Refresh##{sender}', callback='graph_refresh')
        add_same_line()
        add_label_text(f'##{sender}', "", data_source=f'label##{sender}', color=[250, 250, 0, 250])
        add_plot(f'{sender}##plot')
        end_window()
        set_style_window_title_align(0.5, 0.5)
        graph_refresh(sender, data)
        log_info(f'Create item (window): "{window}"')
        
        
def window_quit(sender, data):
    stop_dearpygui()
    
    
def window_episodes(sender, data):
    window = f'{sender}##window'
    log_info(f'Window Shows {sender}')


def window_shows(sender, data):
    window = f'{sender}##window'
    log_info(f'Window Shows {sender}')
    if not does_item_exist(window):
        add_window(window, 1250, 600, start_x=15, start_y=35, resizable=False, movable=True, on_close="window_close")
        if sender == 'Show Maintenance' or sender == 'Eval New Shows':
            add_input_int(f'Show ID##{sender}', default_value=0, width=250)
            add_input_text(f'Show Name##{sender}', hint='Use % as wild-card', width=250)
            add_button(f'Clear##{sender}', callback='show_maint_clear')
            add_same_line(spacing=10)
            add_button(f'Search##{sender}', callback='show_fill_table')
            add_seperator()
            add_input_text(f'##show_showname{sender}', readonly=True, default_value='', width=650)
            add_same_line(spacing=10)
            add_button(f'View on TVMaze##{sender}', callback='tvmaze_view_show')
            add_same_line(spacing=10)
            add_button(f'Follow##{sender}', callback='tvmaze_f_u_show')
            add_same_line(spacing=10)
            if sender == 'Eval New Shows':
                add_button(f'Skip##{sender}', callback='shows_skip', tip='Set new show to Skipped')
                add_same_line(spacing=10)
                add_button(f'Undecided##{sender}', callback='shows_undecided',
                           tip='Keep show on this list for later determination')
            else:
                add_button(f'Unfollow##{sender}', callback='tvmaze_f_u_show',
                           tip='Unfollow show, delete viewing history')
                add_same_line(spacing=10)
                add_button(f'Start Skipping##{sender}', callback=f'shows_skipping',
                           tip='Start Skipping, leave episode history intact')
                add_same_line(spacing=10)
                add_button(f'Find on the Web##{sender}', callback='shows_find_on_web')
            add_seperator()
            add_spacing()
            add_table(f'shows_table##{sender}',
                      headers=['Show ID', 'Show Name', 'Network', 'Type', 'Status', 'My Status', 'Premiered',
                               'Downloader'],
                      callback=f'shows_table_click')
        else:
            add_label_text(f'##uw{sender}', value='Tried to create an undefined Show Window')
        end_window()
        set_style_window_title_align(0.5, 0.5)
        if sender == 'Eval New Shows':
            show_fill_table(f'Search##{sender}', None)
        log_info(f'Create item (window): "{window}"')
        
        
def window_shows_all_graphs(sender, data):
    window_graphs('Other Shows', None)
    set_window_pos('Other Shows##graphs', 830, 600)
    set_item_width('Other Shows##graphs', 800)
    set_item_height('Other Shows##graphs', 550)
    window_graphs('In Development Shows', None)
    set_window_pos('In Development Shows##graphs', 15, 600)
    set_item_width('In Development Shows##graphs', 800)
    set_item_height('In Development Shows##graphs', 550)
    window_graphs('Followed Shows', None)
    set_window_pos('Followed Shows##graphs', 830, 35)
    set_item_width('Followed Shows##graphs', 800)
    set_item_height('Followed Shows##graphs', 550)
    window_graphs('All Shows', None)
    set_window_pos('All Shows##graphs', 15, 35)
    set_item_width('All Shows##graphs', 800)
    set_item_height('All Shows##graphs', 550)


def window_tests(sender, data):
    window = f'{sender}##window'
    log_info(f'Window Shows {sender}')
    if not does_item_exist(window):
        add_window(window, 1250, 600, start_x=15, start_y=35, resizable=False, movable=True, on_close="window_close")
        if sender == 'Test Window for Tabs':
            add_tab_bar(f'Tab Bar##{sender}')
            add_tab(f'Tab1', parent=f'Tab Bar##{sender}')
            add_text('some text')
            end_tab()
            add_tab(f'Tab2##{sender}')
            add_text('some other text')
            end_tab()
            end_tab_bar()
        else:
            add_label_text(f'##uw{sender}', value='Tried to create an undefined Show Window')
        end_window()
        set_style_window_title_align(0.5, 0.5)
    log_info(f'Create item (window): "{window}"')


# Program

print()
print(f'{time.strftime("%D %T")} TVMaze UI >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Started')
options = docopt(__doc__, version='TVMaze V1')
if options['-p']:
    add_data('mode', 'Prod')
    add_data('db_opposite', "Test DB")
    print('Starting in Production Mode')
else:
    add_data('mode', 'Test')
    add_data('db_opposite', "Production DB")
    print('Starting in Test Mode')


program_data()
program_mainwindow()

show_logger()
set_window_pos('logger##standard', 500, 925)
set_item_width('logger##standard', 1000)
set_item_height('logger##standard', 175)
show_debug()
set_window_pos('debug##standard', 50, 800)

start_dearpygui()

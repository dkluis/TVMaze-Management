"""
tvmaze.py   The App that is the UI to all TVMaze function.
Usage:
  tvmaze.py [-p] [-e] [-l] [-d] [--th=<theme>]
  tvmaze.py [-p] [-s] [-l] [-d] [--th=<theme>]
  tvmaze.py -p   [-m] [-l] [-d] [--th=<theme>]
  tvmaze.py -h | --help
  tvmaze.py --version

Options:
  -h --help      Show this screen
  -p             Start in Production mode, otherwise the UI starts in Test mode.
                 Production or Test DB and Production or Test Log Files
  -m             Start with the Show Maintenance window opened
  -d             Start with the standard Debug and standard Logger windows opened
  -s             Start with all show graphs windows opened
  -e             Start with all episode graphs windows opened
  --th=<theme>   Level of verbosity *******  NOT IMPLEMENTED YET  *******
                   D = Dark Theme, G = Gold Theme  [default: G]
  --version      Show version.
"""

import os
import subprocess
from datetime import datetime, timedelta

from dearpygui.core import *
from dearpygui.simple import *
from docopt import docopt

from db_lib import tvm_views
from tvm_api_lib import *
from tvm_lib import execute_sql


class paths:
    def __init__(self, mode):
        log_prod = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/'
        if mode == 'Prod':
            lp = log_prod
            ap = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Apps/'
        else:
            lp = '/Volumes/HD-Data-CA-Server/Development/PycharmProjects/TVM-Management/Logs/'
            ap = '/Volumes/HD-Data-CA-Server/Development/PycharmProjects/TVM-Management/Apps/'
        self.log_path = lp
        self.app_path = ap
        self.console = lp + 'TVMaze.log'
        self.errors = lp + 'Errors.log'
        self.process = log_prod + 'Process.log'
        self.cleanup = log_prod + 'Cleanup.log'
        self.watched = log_prod + 'Watched.log'
        self.transmission = log_prod + "Transmission.log"


class lists:
    getters = ['Multi', 'ShowRSS', 'rarbgAPI', 'eztvAPI', 'piratebay', 'magnetdl', 'eztv', 'Skip']
    show_statuses = ['Running', 'In Development', 'To Be Determined', 'Ended', 'All']
    maintenance_buttons = ['Follow', 'Unfollow', 'Episode Skipping', 'Not Interested', 'Undecided', 'Change Getter']


def func_db_opposite():
    """
    Function to return the DB that can be toggled to
    
    :return: The name of the opposite DB to toggle to
    """
    log_info(f'Retrieving Mode {get_value("mode")}')
    if get_value('mode') == 'Prod':
        set_value('db_opposite', 'Test DB')
    else:
        set_value('db_opposite', "Production DB")
    log_info(f'db_opposite {get_value("db_opposite")}')


def func_buttons(win='', fc='Show', buttons=None):
    """
    Function to turn buttons visible or hide them
    
    :param win:     The name of the Window where the buttons are located, currently only for win = 'Maintenance'
    :param fc:      The function to be executed. (Hide or Show)
    :param buttons: A list of button widgets to hide or show, full list is in lists.maintenance_buttons
    :return:        None
    """
    if buttons is None:
        buttons = []
    log_info(f'function Buttons s {win} f {fc}, b {buttons}')
    if fc == 'Hide':
        for button in buttons:
            log_info(f'Hiding button {button}')
            hide_item(f'{button}##{win}')
    elif fc == 'Show':
        log_info(f'Showing buttons for {win}')
        if win == 'Maintenance':
            buttons = lists.maintenance_buttons
            log_info(f'Buttons are {buttons}')
            for button in buttons:
                log_info(f'Showing button {button}')
                show_item(f'{button}##{win}')
    else:
        log_error(f'None existing function code {fc}')


def func_empty_logfile(sender='', data=''):
    """
    Function to empty a log file
    
    :param sender:  The name of the button and the window
    :param data:    Not Used
    :return:        None
    """
    win = func_sender_breakup(sender, 1)
    log_info(f'Start the empty logfile process with {sender}, {data}')
    paths_info = paths(get_value('mode'))
    if win == 'Cleanup Log':
        logfile = paths_info.cleanup
        func_remove_logfile(logfile)
        log_info(f'Removing Cleanup Log {logfile}')
    elif win == 'Processing Log':
        logfile = paths_info.process
        func_remove_logfile(logfile)
        log_info(f'Removing Run Log: {logfile}')
    elif win == 'Python Errors':
        logfile = paths_info.errors
        func_remove_logfile(logfile)
    elif win == 'TVMaze Log':
        logfile = paths_info.console
        func_remove_logfile(logfile)
    else:
        log_warning(f'Did not process the emptying, could not find {sender}')
    delete_item(f'{win}##window')
    
    
def func_episode_statuses(sender, data):
    pass


def func_exec_sql(f='', s=''):
    """
    Function to execute SQL which automatically figures out which DB to use
    
    :param f:  Type of SQL request:  'Fetch' or 'Commit'
    :param s:  The full sql command
    :return:   Result of the sql execution
    """
    if get_value('mode') == 'Prod':
        res = execute_sql(sqltype=f, sql=s)
    else:
        res = execute_sql(sqltype=f, sql=s, d='Test-TVM-DB')
    log_info(f'SQL {f} {s} executed {res}')
    return res


def func_every_frame(sender, data):
    if is_item_clicked('Tools'):
        set_item_label(f'##db', get_value('db_opposite'))
        set_item_label(f'##theme', get_value('theme_opposite'))
        log_info(f'Every Frame: Tools was clicked')
    elif is_item_clicked('Shows'):
        sql = tvm_views.shows_to_review_count
        count = func_exec_sql('Fetch', sql)
        set_item_label('##no_new_shows', str(count[0][0]))
        log_info(f'Every Frame: Shows was clicked')
        

def func_filter_graph_sql(sql, g_filter):
    if g_filter == 'Last 7 days':
        d = datetime.today() + timedelta(days=-7)
        stat_date = str(d)[:10]
        sql = f'{sql} and statdate > "{stat_date}"'
    return sql


def func_find_shows(si, sn):
    log_info(f'Find Shows SQL with showid {si} and showname {sn}')
    if si == 0 and sn == 'New':
        sql = tvm_views.shows_to_review_tvmaze
    elif sn == 'Shows Due':
        sql = f'select DISTINCT a.showid, a.showname, a.network, a.language, a.type, a.showstatus, ' \
              f'a.status, a.premiered, a.download, a.imdb, a.thetvdb ' \
              f'from shows a join episodes e on e.showid = a.showid ' \
              f'where e.mystatus is NULL and e.airdate is not NULL and e.airdate <= current_date ' \
              f'and download != "Skip" ORDER BY showid;'
    else:
        showid = get_value('shows_showid')
        if showid != 0:
            sql = f'select showid, showname, network, language, type, showstatus, status, premiered, download, ' \
                  f'imdb, thetvdb ' \
                  f'from shows where `showid` = {si} order by showid'
        elif sn != '':
            sql = f'select showid, showname, network, type, language, showstatus, status, premiered, download, ' \
                  f'imdb, thetvdb ' \
                  f'from shows where `showname` like "{sn}" order by showname, premiered desc'
        else:
            return []
    fs = func_exec_sql('Fetch', sql)
    return fs


def func_get_getter(getters):
    log_info(f'Get Getters {getters}')
    links = []
    for getter in getters:
        link = func_exec_sql('Fetch', f"SELECT * from download_options WHERE `providername` = '{getter}'")
        links.append(link)
    return links


def func_key_login(sender, data):
    log_info(f'Login Key Press detected s {sender} d {data}')
    if data == mvKey_Return:
        func_login(sender, data)


def func_key_main(sender, data):
    log_info(f'Main Window Key detected s {sender} d {data}')


def func_key_shows(sender, data):
    function = func_sender_breakup(sender, 1)
    log_info(f'Shows Key Press detected s {sender} d {data} w {function}')
    if data == mvKey_Return:
        shows_fill_table(f'Search##{sender}', data)


def func_key_logs(sender, data):
    function = func_sender_breakup(sender, 0)
    log_info(f'Logs Key Press detected s {sender} d {data} w {function}')
    if data == mvKey_Return:
        func_log_filter(f'Filter##{function}', data)


def func_log_filter(sender, data):
    log_info(f'Func Log Filter s {sender}, d {data}')
    win = func_sender_breakup(sender, 1)
    filter_table = get_value(f'log_table##{win}')
    if len(get_value(f'##{win}ft')) != 0:
        new_table = []
        for row in filter_table:
            if str(get_value(f'##{win}ft')).lower() in str(row).lower():
                new_table.append(row)
        set_table_data(f'log_table##{win}', new_table)
        set_value(f'##{win}ft', '')


def func_login(sender, data):
    log_info(f'Password Checker s {sender}, d {data}')
    if get_value('Password') == 'password':
        delete_item('Login Window')
        func_recursively_show_main('MainWindow')
    else:
        set_value('##Error', 'Wrong Username or Password')
        # ToDo figure out style and color for set_item
        set_item_color('##Error', style=mvGuiCol_Text, color=[250, 0, 0])


def func_recursively_show_main(container):
    for item in get_item_children(container):
        if get_item_children(item):
            if 'SEP' in item:
                continue
            show_item(item)
            func_recursively_show_main(item)
        else:
            if 'SEP' in item:
                continue
            show_item(item)


def func_remove_logfile(logfile):
    log_info(f'Removing logfile {logfile}')
    try:
        os.remove(logfile)
    except IOError as err:
        log_warning(f'Could not remove logfile {logfile} due to {err}')
    else:
        log_info(f'Removed the plex {logfile}')
        open(logfile, 'a').close()


def func_sender_breakup(sender, pos):
    if '##' in sender:
        win = str(sender).split('##')[pos]
    else:
        win = ''
    return win


def func_show_statuses(sender, data):
    srd = get_value(f'srd##Top 10 Graphs')
    log_info(f'Show Statuses s {sender}, d {data}, srd {srd}')
    set_value(f'srd#{sender}', srd)
    if does_item_exist('Shows##Top 10 Charts'):
        clear_plot('Shows##Top 10 Charts')
        delete_series('Shows##Top 10 Charts', sender)
    else:
        add_plot(f'Shows##Top 10 Charts', xaxis_no_gridlines=True, xaxis_no_tick_labels=True, xaxis_no_tick_marks=True,
                 yaxis_no_gridlines=True, yaxis_no_tick_labels=True, yaxis_no_tick_marks=True, no_mouse_pos=True)
        set_plot_xlimits(f'Shows##Top 10 Charts', -.1, 1.1)
        set_plot_ylimits(f'Shows##Top 10 Charts', -.1, 1.1)
    ss = ''
    if srd == 0:
        ss = 'Running'
        set_value(f'srd##{sender}', 0)
    elif srd == 1:
        ss = 'In Development'
        set_value(f'srd##{sender}', 1)
    elif srd == 2:
        ss = 'To Be Determined'
        set_value(f'srd##{sender}', 2)
    elif srd == 3:
        ss = 'Ended'
        set_value(f'srd##{sender}', 3)
    sql = ''
    if srd == 4:
        sql = f'select network, count(*) from shows ' \
              f'where status = "Followed" ' \
              f'group by network order by count(*) desc limit 10'
    else:
        sql = f'select network, count(*) from shows ' \
              f'where status = "Followed" and showstatus = "{ss}" ' \
              f'group by network order by count(*) desc limit 10'
    result = func_exec_sql('Fetch', sql)
    pie_data = []
    for res in result:
        rec = [res[0], res[1]]
        pie_data.append(rec)
    add_pie_series('Shows##Top 10 Charts', sender, pie_data, 0.5, 0.5, 0.5)


def func_tvm_update(fl, si):
    log_info(f'TVMaze update {fl}, {si}')
    api = f'{tvm_apis.followed_shows}/{si}'
    sql = []
    if fl == "F":
        shows = execute_tvm_request(api, req_type='put', code=True)
        if not shows:
            log_error(f"Web error trying to follow show: {si}")
            return False
        success = 'Followed'
        download = 'Multi'
        sql.append(f'update shows set status = "{success}", download = "{download}" where `showid` = {si}')
    elif fl == "U":
        shows = execute_tvm_request(api, req_type='delete', code=True)
        if not shows:
            log_error(f"Web error trying to unfollow show: {si}")
            return False
        success = 'Skipped'
        download = None
        sql.append(f'update shows set status = "{success}", download = "{download}" where `showid` = {si}')
        sql.append(f'delete from episodes where `showid` = {si}')
    elif fl == 'UD':
        success = 'Undecided'
        d = datetime.today() + timedelta(days=14)
        download = str(d)[:10]
        sql.append(f'update shows set status = "{success}", download = "{download}" where `showid` = {si}')
    elif fl == 'SK':
        success = 'Skipped'
        download = None
        sql.append(f'update shows set status = "{success}", download = "{download}" where `showid` = {si}')
    else:
        log_info(f'Not implement {fl} option')
        return False
    any_error = False
    for esql in sql:
        esql = esql.replace('"None"', 'NULL')
        result = func_exec_sql('Commit', esql)
        if not result:
            any_error = True
            log_error(f'Update of the DB failed: {sql}, {result}')
    return any_error


def func_toggle_db(sender, data):
    log_info(f'Toggle DB')
    if get_value('mode') == 'Prod':
        set_value('mode', 'Test')
        set_value('db_opposite', 'Production DB')
        set_main_window_title(f'TVMaze Management - Test DB')
    else:
        set_value('mode', 'Prod')
        set_value('db_opposite', 'Test DB')
        set_main_window_title(f'TVMaze Management - Production DB')


def func_toggle_theme(sender, data):
    ot = get_value('theme_opposite')
    set_theme(str(ot))
    if ot == 'Dark':
        set_value('theme_opposite', 'Gold')
    else:
        set_value('theme_opposite', 'Dark')


def epis_fill_table(sender, data):
    log_info(f'Fill Episode Table {sender} {data}')
    win = func_sender_breakup(sender, 1)
    button = func_sender_breakup(sender, 0)
    showid = get_value(f'Show ID##{win}')
    set_value('epi_showid', showid)
    showname = get_value(f'Show Name##{win}')
    if showid == 0 and showname == '' and button == 'Search':
        set_value(f'##epi_showname{win}', 'Nothing was entered in Show ID or Showname')
    log_info(f'showid: {showid} - showname: {showname}')
    found_shows = ''
    if button == 'Search':
        found_shows = func_find_shows(showid, showname)
    elif button == 'Evaluate Shows':
        found_shows = func_find_shows(0, 'New')
    elif button == 'Shows Due':
        found_shows = func_find_shows(0, 'Shows Due')
    else:
        log_error(f'Unknown Button Pressed to fill the table b {button}')
    
    table = []
    for rec in found_shows:
        table_row = []
        for field in rec:
            table_row.append(field)
        table.append(table_row)
    set_table_data(f'shows_table##{win}', table)
    func_buttons(win=win, fc='Show')
    epis_view_clear('fill_table##View', 'input_fields_only')


def epis_view_clear(sender, data):
    log_info(f'Epi Maint clear {sender} {data}')
    win = func_sender_breakup(sender, 1)
    if data != 'input_fields_only':
        set_table_data(f'shows_table##{win}', [])
        set_value(f'##show_showname{win}', "")
        func_buttons(win=win, fc='Show')
    
    set_value(f'Show ID##{win}', 0)
    set_value(f'Show Name##{win}', '')
    set_value(f'##show_name{win}', '')
    set_value(f'selected##{win}', False)


def graph_execute_get_value(sql, sender, pi, g_filter):
    log_info(f'Filling the plot data for {sender} with {sql} and {g_filter}')
    data = func_exec_sql('Fetch', sql)
    plot_index = sender
    if sender == 'Other Shows':
        plot_index = pi
    if g_filter == 'Last 7 days':
        plot_index = f'{plot_index} - {g_filter}'
    else:
        plot_index = f'{plot_index} - All Days'
    add_line_series(f'{sender}##plot', f'{plot_index}', data)
    # ToDo Figure graph call back from auto refresh option
    # set_render_callback(graph_render_callback)


def graph_get_value(sender, g_filter):
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
        graph_refresh_other('Other Shows', g_filter)
        return
    else:
        add_line_series(f'{sender}##plot', "Unknown", data)
        return
    sql = func_filter_graph_sql(sql, g_filter)
    graph_execute_get_value(sql, sender, data, g_filter)


def graph_refresh(sender, data):
    if data:
        g_filter = data
    else:
        g_filter = ''
    if '##' in sender:
        requester = func_sender_breakup(sender, 1)
        g_filter = func_sender_breakup(sender, 0)
    else:
        requester = sender
    log_info(f'Refreshing Graph Data for {requester} with filter {g_filter}')
    graph_get_value(requester, g_filter)


def graph_refresh_other(sender, g_filter):
    log_info(f'Graph refresh for all Others')
    if sender != 'Other Shows':
        return
    sql = f'select statepoch, myshowsended from statistics where statrecind = "TVMaze"'
    sql = func_filter_graph_sql(sql, g_filter)
    graph_execute_get_value(sql, 'Other Shows', f'Ended', g_filter)
    sql = f'select statepoch, myshowsrunning from statistics where statrecind = "TVMaze"'
    sql = func_filter_graph_sql(sql, g_filter)
    graph_execute_get_value(sql, 'Other Shows', f'Running', g_filter)
    sql = f'select statepoch, myshowstbd from statistics where statrecind = "TVMaze"'
    sql = func_filter_graph_sql(sql, g_filter)
    graph_execute_get_value(sql, 'Other Shows', f'TBD', g_filter)


# Todo part of the render callback todo
def graph_render_callback(sender, data):
    log_info(f'Graph Render Callback Triggered {sender} {data}')


def program_callback(sender, data):
    log_info(f'Main Callback activated {sender}, {data}')
    if sender == 'Shows':
        sql = tvm_views.shows_to_review_count
        count = func_exec_sql('Fetch', sql)
        set_value('shows_ds_new_shows', f': {str(count[0][0])}')


def program_data():
    add_value('shows_ds_new_shows', '0')
    add_value('shows_showid', 0)
    add_value(f'selected##Maintenance', False)
    add_value(f'selected##View', False)
    add_value('theme_opposite', 'Dark')
    add_value('label##All Shows', "All the shows that are available on TVMaze")
    add_value('label##Followed Shows', "Only the followed shows")
    add_value('label##In Development Shows', "Only the followed shows that have not started yet")
    add_value('label##Other Shows',
              "Only the followed shows that are currently 'Running', have 'Ended' or are 'In Limbo")
    add_value('label##All Episodes', "All episodes (followed shows only)")
    add_value('label##Watched Episodes', "All watched episodes (followed shows only)")
    add_value('label##Skipped Episodes', "All skipped episodes (followed shows only)")
    add_value('label##Episodes to Get', "All episodes to get onto Plex (followed shows only)")
    add_value('label##Episodes to Watch', "All available episodes on Plex not watched yet (followed shows only)")
    add_value('label##Upcoming Episodes', "All announced episodes beyond today (followed shows only)")
    add_value('theme_opposite', 'Dark')


def program_mainwindow():
    if get_value('mode') == 'Test':
        set_main_window_title(f'TVMaze Management - Test DB')
    else:
        set_main_window_title('TVMaze Management - Production DB')
    set_style_window_title_align(0.5, 0.5)
    set_main_window_size(2140, 1210)
    set_theme('Gold')
    # add_image('TVMaze BG', '/Users/dick/Desktop/tvm-icon-1210.png')
    with menu_bar('Menu Bar'):
        with menu('TVMaze'):
            add_menu_item('Calendar', callback=tvmaze_calendar, tip='Starts in Safari')
            add_spacing(count=1)
            add_separator(name=f'##TVMazeSEP1')
            add_spacing(count=1)
            add_menu_item('Log Out', callback=tvmaze_logout, shortcut='cmd+L')
            add_spacing(count=1)
            add_separator(name=f'##TVMazeSEP2')
            add_spacing(count=1)
            add_menu_item('Quit', callback=window_quit, shortcut='cmd+Q')
        with menu('Shows'):
            add_menu_item('Eval New Shows', callback=window_shows)
            add_same_line()
            add_label_text('##no_new_shows', value='')
            add_spacing(count=1)
            add_separator(name=f'##TVMazeSEP3')
            add_spacing(count=1)
            add_menu_item('Maintenance', callback=window_shows)
            with menu('Graphs##shows'):
                add_menu_item('All Shows', callback=window_graphs)
                add_menu_item('Followed Shows', callback=window_graphs)
                add_menu_item('In Development Shows', callback=window_graphs)
                add_menu_item('Other Shows', callback=window_graphs)
                add_spacing(count=1)
                add_separator(name=f'Graphs##ShowsSEP1')
                add_spacing(count=1)
                add_menu_item('All Graphs##Shows', callback=window_shows_all_graphs, shortcut='cmd+S')
        with menu('Episodes', tip='Only of Followed Shows'):
            add_menu_item('View', callback=window_episodes)
            with menu('Graphs##episodes'):
                add_menu_item('All Episodes', callback=window_graphs)
                add_menu_item('Skipped Episodes', callback=window_graphs)
                add_menu_item('Watched Episodes', callback=window_graphs)
                add_menu_item('Episodes to Get', callback=window_graphs)
                add_menu_item('Episodes to Watch', callback=window_graphs)
                add_menu_item('Upcoming Episodes', callback=window_graphs)
                add_spacing(count=1)
                add_separator(name='Graphs##episodesSEP1')
                add_spacing(count=1)
                add_menu_item('All Graphs##episodes', callback=window_episodes_all_graphs, shortcut='cmd+E')
        add_menu_item('Top 10 Graphs', callback=window_top_10)
        with menu('Process'):
            add_menu_item('Get Episodes', callback=tvmaze_processes)
            add_spacing(count=1)
            add_separator(name='ProcessSEP1')
            add_spacing(count=1)
            add_menu_item('Transmission Files', callback=window_files)
        with menu('Logs'):
            add_menu_item('Cleanup Log', callback=window_logs)
            add_menu_item('Processing Log', callback=window_logs)
            add_menu_item('Python Errors', callback=window_logs)
            add_menu_item('Transmission Log', callback=window_logs)
            add_menu_item('TVMaze Log', callback=window_logs)
        with menu('Tools'):
            add_menu_item('Toggle Database to', callback=func_toggle_db)
            add_same_line(xoffset=140)
            add_label_text(f'##db')
            add_menu_item('Toggle Theme to', callback=func_toggle_theme)
            add_same_line(xoffset=140)
            add_label_text(f'##theme', label='Gold')
            add_spacing(count=1)
            add_separator(name='ToolsSEP1')
            add_spacing(count=1)
            add_menu_item('Show Logger', callback=window_standards)
            add_spacing(count=1)
            add_separator(name='ToolsSEP2')
            add_spacing(count=1)
            with menu('Debug Mode'):
                add_menu_item('Show Debugger', callback=window_standards)
                add_menu_item('Show Documentation', callback=window_standards)
                add_menu_item('Show Source Code', callback=window_standards)
                add_menu_item('Show Style Editor', callback=show_style_editor)
                add_spacing(count=1)
                add_separator(name='Debug ModeSEP')
                add_spacing(count=1)
                add_menu_item('Get Open Window Positions', callback=window_get_pos)
        with menu('Windows'):
            add_menu_item('Close Open Windows', callback=window_close_all)
    
    # add_additional_font("/System/Library/Fonts/Menlo.ttc", 14)
    add_additional_font("/Users/dick/Library/Fonts/KlokanTechNotoSans-Bold.ttf", 16,
                        custom_glyph_ranges=[[0x370, 0x377], [0x400, 0x4ff], [0x530, 0x58f], [0x10a0, 0x10ff],
                                             [0x30a0, 0x30ff], [0x0590, 0x05ff]])
    # add_additional_font("/Users/dick/Library/Fonts/ProggyClean.ttf", 14,
    # add_additional_font("/Users/dick/Library/Fonts/unifont-13.0.03.ttf", 14,
    #                    custom_glyph_ranges=[[0x370, 0x377], [0x400, 0x4ff], [0x530, 0x58f], [0x10a0, 0x10ff]])
    set_key_down_callback(func_key_main)
    set_key_press_callback(func_key_main)
    if options['-s'] and not options['-l']:
        window_shows_all_graphs('All Graphs', 'set_item_callback')
    elif options['-e'] and not options['-l']:
        window_episodes_all_graphs('All Graphs', 'set_item_callback')
    elif options['-m'] and not options['-l']:
        window_shows('Maintenance', 'set_item_callback')
    if options['-d']:
        window_standards('Show Logger', '')
        window_standards('Show Debugger', '')


def shows_fill_table(sender, data):
    log_info(f'Fill Show Table {sender} {data}')
    win = func_sender_breakup(sender, 1)
    button = func_sender_breakup(sender, 0)
    showid = get_value(f'Show ID##{win}')
    set_value('shows_showid', showid)
    showname = get_value(f'Show Name##{win}')
    found_shows = ''
    if showid == 0 and showname == '' and button == 'Search':
        set_value(f'##show_showname{win}', 'Nothing was entered in Show ID or Showname')
    log_info(f'showid: {showid} - showname: {showname}')
    if button == 'Search':
        found_shows = func_find_shows(showid, showname)
    elif button == 'Evaluate Shows':
        found_shows = func_find_shows(0, 'New')
    elif button == 'Shows Due':
        found_shows = func_find_shows(0, 'Shows Due')
    else:
        log_error(f'Unknown Button Pressed to fill the table b {button}')
    
    table = []
    for rec in found_shows:
        table_row = []
        for field in rec:
            table_row.append(str(field).replace('None', ''))
        table.append(table_row)
    set_table_data(f'shows_table##{win}', table)
    func_buttons(win=win, fc='Show')
    shows_maint_clear('fill_table##Maintenance', 'input_fields_only')


def shows_find_on_web(sender, data):
    win = func_sender_breakup(sender, 1)
    function = func_sender_breakup(sender, 0)
    selected = get_value(f'selected##{win}')
    showid = get_value(f'Show ID##{win}')
    log_info(f'Shows Find On the Web s {sender}, d {data}, w "{win}", f "{function}", si {showid}')
    if not selected:
        set_value(f'##show_showname{win}', 'No Show was selected yet, nothing to do yet')
    else:
        links = func_get_getter(getters=['rarbg', 'piratebay', 'eztv', 'magnetdl'])
        showinfo = func_exec_sql('Fetch', f'select * from shows where `showid` = {showid}')[0]
        for link in links:
            li = link[0]
            if not li[2]:
                sfx = ''
            else:
                sfx = str(li[2])
            if "magnetdl" in li[1]:
                link_str = f'{li[1]}{str(showinfo[1][0]).lower()}/'
            else:
                link_str = li[1]
            full_link = f'{link_str}{str(showinfo[1]).replace(" ", li[3]).lower()}{sfx}'
            start_find = 'open -a safari ' + full_link
            os.system(start_find)


def shows_maint_clear(sender, data):
    log_info(f'Show Maint clear {sender} {data}')
    win = func_sender_breakup(sender, 1)
    if data != 'input_fields_only':
        set_table_data(f'shows_table##{win}', [])
        set_value(f'##show_showname{win}', "")
        func_buttons(win=win, fc='Show')
    
    set_value(f'Show ID##{win}', 0)
    set_value(f'Show Name##{win}', '')
    set_value(f'##show_name{win}', '')
    set_value(f'selected##{win}', False)


def shows_table_click(sender, data):
    log_info(f'Shows Table Click {sender} {data}')
    show_options = ''
    win = func_sender_breakup(sender, 1)
    row_cell = get_table_selections(f'shows_table##{win}')
    row = row_cell[0][0]
    set_value(f'selected##{win}', True)
    showid = get_table_data(f'shows_table##{win}')[row][0]
    show_status = get_table_data(f'shows_table##{win}')[row][6]
    my_status = get_table_data(f'shows_table##{win}')[row][7]
    log_info(f'Show Table Click id {showid}, status {show_status}, my status {my_status}')
    func_buttons(win, 'Show')
    if show_status == 'New' or show_status == 'Undecided':
        func_buttons(win=win, fc='Hide',
                     buttons=['Unfollow', 'Episode Skipping', 'Change Getter'])
    elif show_status == 'Followed' and my_status == 'Skip':
        func_buttons(win=win, fc='Hide',
                     buttons=['Follow', 'Episode Skipping', 'Not Interested', 'Undecided'])
    elif show_status == 'Followed':
        func_buttons(win=win, fc='Hide',
                     buttons=['Follow', 'Not Interested', 'Undecided'])
    elif show_status == 'Skipped':
        func_buttons(win=win, fc='Hide',
                     buttons=['Unfollow', 'Episode Skipping', 'Not Interested', 'Undecided', 'Change Getter'])
    else:
        func_buttons(win=win, fc='Show')
    set_value('showid', showid)
    showname = str(get_table_data(f'shows_table##{win}')[row][1])[:35]
    set_value(f'##show_showname{win}', f"Selected Show: {showid}, {showname} {show_options}")
    set_value(f'Show ID##{win}', int(showid))
    set_value(f'Show Name##{win}', showname)
    log_info(f'Table Click for row cell {row_cell} selected showid {showid}')
    for sel in row_cell:
        set_table_selection(f'shows_table##{win}', sel[0], sel[1], False)


def tvmaze_calendar(sender, data):
    log_info('TVM Calendar started in Safari')
    subprocess.call("open -a safari  https://www.tvmaze.com/calendar", shell=True)


def tvmaze_change_getter(sender, si):
    win = func_sender_breakup(sender, 1)
    function = func_sender_breakup(sender, 0)
    log_info(f'Change where to get s {sender}, showid {si}, w {win}, f {function}')
    if function == 'Submit':
        ind = get_value(f'Getters##Maintenance')
        log_info(f'Getter Selected {lists.getters[ind]}')
        sql = f'update shows set download = "{lists.getters[ind]}" where `showid` = {si}'
        func_exec_sql('Commit', sql)
    delete_item(f'Getters##w{win}')


def tvmaze_logout(sender, data):
    hide_item('MainWindow', children_only=True)
    window_close_all('', '')
    window_login()


def tvmaze_processes(sender, data):
    log_info(f'TVMaze processes Started s {sender}, d {data}')
    paths_info = paths(get_value('mode'))
    loc = paths_info.app_path
    action = ''
    if sender == 'Get Shows':
        action = f"python3 {loc}actions.py -d "
    # ToDo 0.4 run_async_function(subprocess.call(action, shell=True), data)
    log_info(f'TVMaze processes ASYNC Finished s {action}')
    window_logs('TVMaze Log', '')
    window_logs('Python Errors', '')


def tvmaze_update(sender, data):
    win = func_sender_breakup(sender, 1)
    function = func_sender_breakup(sender, 0)
    selected = get_value(f'selected##{win}')
    si = get_value(f'Show ID##{win}')
    log_info(f'TVMaze update s {sender}, d {data}, w "{win}", f "{function}", si {si}')
    if not selected:
        set_value(f'##show_showname{win}', 'No Show was selected yet, nothing to do yet')
    else:
        if function == 'Follow':
            result = func_tvm_update('F', si)
            log_info(f'TVMaze Follow result: {result}')
            set_value(f'##show_showname{win}', f'Show {si} update on TVMaze and set Follow = {result}')
        elif function == 'Unfollow':
            result = func_tvm_update('U', si)
            log_info(f'TVMaze Unfollow result: {result}')
            set_value(f'##show_showname{win}', f'Show {si} update on TVMaze and set Unfollow = {result}')
        elif function == 'Undecided':
            result = func_tvm_update('UD', si)
            log_info(f'TVMaze Undecided result: {result}')
            set_value(f'##show_showname{win}', f'Show {si} update on TVMaze and set Unfollow = {result}')
        elif function == 'Change Getter':
            log_info(f'Starting window change getter with {sender}, {data}')
            window_change_getters(sender, si)
        elif function == 'Not Interested':
            result = func_tvm_update('SK', si)
            log_info(f'TVMaze Skipping result: {result}')
            set_value(f'##show_showname{win}', f'Show {si} update on TVMaze and set Skipped = {result}')
        else:
            log_error(f'Unknown Function: "{function}"')
        shows_maint_clear(sender, 'input_fields_only')


def tvmaze_view_show(sender, data):
    win = func_sender_breakup(sender, 1)
    selected = get_value(f'selected##{win}')
    if not selected:
        set_value(f'##show_showname{win}', 'No Show was selected yet, nothing to do yet')
    else:
        si = get_value(f'Show ID##{win}')
        tvm_link = f"https://www.tvmaze.com/shows/{si}"
        follow_str = 'open -a safari ' + tvm_link
        os.system(follow_str)


def window_change_getters(sender, si):
    function = func_sender_breakup(sender, 0)
    win = func_sender_breakup(sender, 1)
    log_info(f'Trying to create window Change Getter with f {function}, w {win}, showid {si}')
    with window(f'Getters##w{win}', on_close=window_close, autosize=True,
                x_pos=670, y_pos=290, no_resize=True):
        add_radio_button(f'Getters##{win}',
                         items=lists.getters, default_value=0,
                         tip='Multiple will use rarbgAPI, eztvAPI, Piratebay and eztv.')
        add_spacing(count=1)
        add_separator(name=f'Getter##w{win}SEP')
        add_spacing(count=3)
        add_button(f'Cancel##{win}', callback=tvmaze_change_getter)
        add_same_line(spacing=12)
        add_button(f"Submit##{win}", callback=tvmaze_change_getter, callback_data=si)
        add_spacing(count=1)


def window_close(sender, data):
    win = f'{sender}'
    delete_item(win)
    log_info(f'Delete item (window): "{win}"')


def window_close_all(sender, data):
    log_info('Close Open Windows')
    all_windows = get_windows()
    for win in all_windows:
        log(f'Processing to close: {win}')
        if 'MainWindow' in win:
            continue
        log_info(f'Closing window found: {win}')
        delete_item(win)
    hide_item('debug##standard')
    hide_item('logger#standard')


def window_episodes(sender, data):
    win = f'{sender}##window'
    log_info(f'Window Shows {sender}')
    if not does_item_exist(win):
        with window(win, 1500, 750, x_pos=30, y_pos=70, no_resize=True, on_close=window_close):
            add_input_int(f'Show ID##{sender}', default_value=0, width=250)
            add_input_text(f'Show Name##{sender}', hint='Use % as wild-card', width=250)
            add_button(f'Clear##{sender}', callback=epis_view_clear)
            add_same_line(spacing=10)
            add_button(f'Search##{sender}', callback=epis_fill_table)
            with group('View Options', horizontal=True):
                add_label_text(f'##cbl{sender}', 'Select Options:')
                add_checkbox(f'Test##{sender}')
                add_checkbox(f'Test2##{sender}')
        set_style_window_title_align(0.5, 0.5)


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


def window_files(sender, data):
    win = f'{sender}##window'
    log_info(f'Window Files {sender}')
    if not does_item_exist(win):
        with window(win, 1500, 750, x_pos=30, y_pos=70, no_resize=True, on_close=window_close):
            add_button('Folder', callback=open_file_dialog())
        set_style_window_title_align(0.5, 0.5)


def window_login():
    with window('Login Window', x_pos=900, y_pos=400, no_title_bar=True, no_move=True, autosize=True,
                no_resize=True, no_background=True):
        add_input_text('Username', hint='Your email address', width=250)
        add_input_text('Password', hint='Password is "password" for now', password=True, width=250)
        add_button('Submit', callback=func_login)
        add_same_line(spacing=5)
        add_label_text('##Error', label='')
    set_key_release_callback(func_key_login)


def window_logs(sender, data):
    log_info(f'View Logs Window -> s {sender} d {data}')
    if does_item_exist(f'{sender}##window'):
        log_info(f'{sender}##window already running')
    else:
        if sender == 'Processing Log':
            width = 1955
            height = 600
            sx = 135
            sy = 35
        else:
            width = 600
            height = 500
            sx = 1505
            sy = 35
        with window(f'{sender}##window', x_pos=sx, y_pos=sy, width=width, height=height, on_close=window_close):
            set_style_window_title_align(0.5, 0.5)
            add_button(f'Refresh##{sender}', callback=window_logs_refresh)
            if sender != 'Transmission Log':
                add_same_line(spacing=10)
                add_button(f"Empty Log##{sender}", callback=func_empty_logfile)
            add_button(f"Filter##{sender}", callback=func_log_filter)
            add_same_line(spacing=10)
            add_input_text(f'##{sender}ft', hint='No wildcards, case does not matter')
            add_spacing(count=2)
            add_separator(name=f'{sender}##windowSEP')
            add_table(f'log_table##{sender}',
                      headers=[f'{sender} - Info'])
            window_logs_refresh(f'Refresh##{sender}', data)
        set_key_press_callback(func_key_logs)


def window_logs_refresh(sender, data):
    win = func_sender_breakup(sender, 1)
    function = func_sender_breakup(sender, 0)
    log_info(f'Log Refresh s {sender}, d {data}, f {function}, w {win}')
    paths_info = paths(get_value('mode'))
    logfile = ''
    if win == 'Processing Log':
        logfile = paths_info.process
    elif win == 'TVMaze Log':
        logfile = paths_info.console
    elif win == 'Python Errors':
        logfile = paths_info.errors
    elif win == 'Cleanup Log':
        logfile = paths_info.cleanup
    elif win == 'Transmission Log':
        logfile = paths_info.transmission
    else:
        log_error(f'Refresh for {sender} not defined')
    try:
        file = open(logfile, 'r')
    except IOError as err:
        log_warning(f'Console log file IOError: {err}')
        open(logfile, 'a').close()
        return
    log_info(f'refresh console file: {sender}, {data}')
    consolelines = file.readlines()
    table = []
    for line in consolelines:
        table.append([line.replace("\n", "")])
    set_table_data(f'log_table##{win}', table)
    file.close()
    set_value(f'##{win}ft', '')


def window_get_pos(sender, data):
    all_windows = get_windows()
    log_info(f'Log Open Window Positions for {all_windows}')
    if len(all_windows) >= 2:
        for win in all_windows:
            if win == 'MainWindow':
                continue
            pos = get_window_pos(win)
            height = get_item_height(win)
            width = get_item_width(win)
            log_info(f'Position for: {win} is {pos[0]}, {pos[1]}, width {width}, height {height}')


def window_graphs(sender, data):
    win = f'{sender}##graphs'
    if not does_item_exist(win):
        with window(win, 1250, 600, x_pos=15, y_pos=35, on_close=window_close):
            add_button(f'All days##{sender}', callback=graph_refresh)
            add_same_line()
            add_button(f'Last 7 days##{sender}', callback=graph_refresh)
            add_plot(f'{sender}##plot', xaxis_time=True, crosshairs=True)
        set_style_window_title_align(0.5, 0.5)
        graph_refresh(sender, 'Last 7 days')
        graph_refresh(sender, 'All Days')
        log_info(f'Create item (window): "{win}"')


def window_quit(sender, data):
    stop_dearpygui()


def window_shows(sender, data):
    if sender == 'Eval New Shows':
        sender = 'Maintenance'
        ens = True
    else:
        ens = False
    
    win = f'{sender}##window'
    log_info(f'Window Shows {sender}')
    if not does_item_exist(win):
        with window(win, 1500, 750, x_pos=15, y_pos=35, no_resize=True, on_close=window_close):
            if sender == 'Maintenance':
                add_input_int(f'Show ID##{sender}', default_value=0, width=250)
                add_input_text(f'Show Name##{sender}', hint='Use % as wild-card', width=250)
                add_button(f'Clear##{sender}', callback=shows_maint_clear)
                add_same_line(spacing=10)
                add_button(f'Search##{sender}', callback=shows_fill_table)
                add_same_line(spacing=10)
                add_button(f'Evaluate Shows##{sender}', callback=shows_fill_table)
                add_same_line(spacing=10)
                add_button(f'Shows Due##{sender}', callback=shows_fill_table)
                add_separator(name=f'Maintenance##SEP1')
                add_input_text(f'##show_showname{sender}', readonly=True, default_value='', width=450)
                add_same_line(spacing=10)
                add_button(f'View on TVMaze##{sender}', callback=tvmaze_view_show)
                add_same_line(spacing=10)
                add_button(f'Find on the Web##{sender}', callback=shows_find_on_web,
                           tip='find the websites where to get the show')
                add_same_line(spacing=10)
                add_button(f'Follow##{sender}', callback=tvmaze_update, tip='Start Following selected show')
                add_same_line(spacing=10)
                add_button(f'Unfollow##{sender}', callback=tvmaze_update,
                           tip='Unfollow selected show and deleted episode info')
                add_same_line(spacing=10)
                add_button(f'Episode Skipping##{sender}', callback=tvmaze_update,
                           tip='Do not acquire episodes going forward')
                add_same_line(spacing=10)
                add_button(f'Not Interested##{sender}', callback=tvmaze_update, tip='Set new show to Skipped')
                add_same_line(spacing=10)
                add_button(f'Undecided##{sender}', callback=tvmaze_update,
                           tip='Keep show on Evaluate list for later determination')
                # add_label_text(f'##{sender}', ' ')
                # add_same_line(spacing=643)
                add_same_line(spacing=10)
                add_button(f'Change Getter##{sender}', callback=tvmaze_update,
                           tip='Set the website where to get the show')
                add_separator(name=f'Maintenance##SEP2')
                add_spacing()
                add_table(f'shows_table##{sender}',
                          headers=['Show ID', 'Show Name', 'Network', 'Language', 'Type', 'Status', 'My Status',
                                   'Premiered', 'Getter', 'IMDB', 'TheTVDB'],
                          callback=shows_table_click)
            else:
                add_label_text(f'##uw{sender}', value='Tried to create an undefined Show Window')
        
        set_style_window_title_align(0.5, 0.5)
        set_key_press_callback(func_key_shows)
        if ens:
            shows_fill_table(f'Evaluate Shows##{sender}', None)
        log_info(f'Create item (window): "{win}"')


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


def window_standards(sender, data):
    if sender == 'Show Logger':
        show_logger()
        set_window_pos('logger##standard', 1120, 1015)
        set_item_width('logger##standard', 1000)
        set_item_height('logger##standard', 175)
    elif sender == 'Show Debugger':
        show_debug()
        set_window_pos('debug##standard', 1120, 445)
    elif sender == 'Show Source Code':
        paths_info = paths(get_value('mode'))
        show_source(f'{paths_info.app_path}tvmaze.py')
        set_window_pos('source##standard', 520, 35)
        set_item_width('source##standard', 975)
        set_item_height('source##standard', 955)
    elif sender == 'Show Documentation':
        show_documentation()
        set_window_pos('documentation##standard', 540, 135)
        set_item_width('documentation##standard', 800)
        set_item_height('documentation##standard', 700)


def window_top_10(sender, data):
    win = f'{sender}##window'
    log_info(f'Window Top 10 s {sender}, d {data}')
    if not does_item_exist(win):
        with window(win, 945, 945, x_pos=15, y_pos=35, on_close=window_close):
            if sender == 'Top 10 Graphs':
                with tab_bar(f'Tab Bar##{sender}'):
                    with tab(f'Followed Shows - Network', parent=f'Tab Bar##{sender}'):
                        add_label_text(name=f'##rdl{sender}', value='Select Followed Shows by Status:')
                        set_value(f'srd##{sender}', 0)
                        add_radio_button(name=f'srd##{sender}', items=lists.show_statuses, horizontal=True,
                                         callback=func_show_statuses)
                        func_show_statuses(sender, '')
                    with tab(f'Followed Episodes - Network##{sender}'):
                        add_label_text(name=f'##edl{sender}', value='Select Followed Episodes by Status:')
                        set_value(f'erd##{sender}', 0)
                        add_radio_button(name=f'erd##{sender}', items=lists.show_statuses, horizontal=True,
                                         callback=func_episode_statuses)
                        add_plot(f'Episodes##Top 10 Charts', xaxis_no_gridlines=True, xaxis_no_tick_labels=True,
                                 xaxis_no_tick_marks=True,
                                 yaxis_no_gridlines=True, yaxis_no_tick_labels=True, yaxis_no_tick_marks=True,
                                 no_mouse_pos=True)
                        set_plot_xlimits(f'Episodes##Top 10 Charts', -.1, 1.1)
                        set_plot_ylimits(f'Episodes##Top 10 Charts', -.1, 1.1)
                        sql = 'select s.network, count(*) from episodes e ' \
                              'join shows s on e.showid = s.showid group by s.network order by count(*) desc limit 10'
                        result = func_exec_sql('Fetch', sql)
                        pie_data = []
                        for res in result:
                            rec = [res[0], res[1]]
                            pie_data.append(rec)
                        add_pie_series('Episodes##Top 10 Charts', sender, pie_data, 0.5, 0.5, 0.5)
            else:
                add_label_text(f'##uw{sender}', value='Tried to create an undefined Pie Graph Window')
        set_style_window_title_align(0.5, 0.5)
    log_info(f'Create item (window): "{win}"')


# Program

print(f'{time.strftime("%D %T")} TVMaze UI >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Started')
options = docopt(__doc__, version='TVMaze V1')
if options['-p']:
    add_value('mode', 'Prod')
    add_value('db_opposite', "Test DB")
    print('Starting in Production Mode')
else:
    add_value('mode', 'Test')
    add_value('db_opposite', "Production DB")
    print('Starting in Test Mode')
if options['-d']:
    print('Starting in Debug Mode')
if options['-e']:
    print('Starting with all the Episode Graphs')
if options['-s']:
    print('Starting with all the Show Graphs')

program_data()
program_mainwindow()
set_render_callback(func_every_frame)

if options['-l']:
    tvmaze_logout('', '')

start_dearpygui()

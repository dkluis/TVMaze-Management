from dearpygui.dearpygui import *
import requests
import os
import subprocess

from db_lib import execute_sql

follow = False
unfollow = False
skip = False
find = False
selected = False
showid = 0


def find_shows(showid, showname):
    log_info(f'Find Shows SQL with showid {showid} and showname {showname}')
    if showid != 0:
        sql = f'select showid, showname, network, type, showstatus, status, premiered ' \
              f'from shows where `showid` = "{showid}"'
    else:
        sql = f'select showid, showname, network, type, showstatus, status, premiered ' \
              f'from shows where `showname` like "{showname}" order by premiered desc'
    fs = execute_sql(sqltype='Fetch', sql=sql)
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


set_theme('Gold')
set_main_window_title('TVMaze Management')
add_menu_bar("Menu")

add_menu("Shows")
add_menu_item('Follow', callback='follow_show')
add_menu_item('Unfollow', callback='unfollow_show')
add_menu_item('Start Skipping', callback='skip_show')
add_menu_item('Find Downloads', callback='find_downloads')
end_menu()

add_menu('Statistics')
add_menu_item('Overview', callback='stats_on_web')
add_menu_item('Interactive', callback='stats_interactive')
end_menu()

add_menu("Help")
add_menu_item("Logger", callback="show_logger")
add_menu("UI")
add_menu_item("About", callback="show_about")
add_menu_item("Metrics", callback="show_metrics")
add_menu_item("Documentation", callback="show_documentation")
add_menu_item("Debug", callback="show_debug")
end_menu()
end_menu()
end_menu_bar()

add_seperator()


def fs_close(sender, data):
    log_info(f'Close Find Show with sender {sender} and data {data}')
    if 'Follow' in str(sender):
        global follow
        follow = False
    elif 'Unfollow' in str(sender):
        global unfollow
        unfollow = False
    elif 'Skip' in str(sender):
        global skip
        skip = False
    elif 'Find' in str(sender):
        global find
        find = False
    delete_item(sender)
    

def table_click(sender, data):
    log_info(f'Table Click with sender {sender} and data {data}')
    window = str(sender).split('##')[1]
    row_cell = get_table_selections(f'fs_table##{window}')
    row = row_cell[0][0]
    global showid
    global selected
    selected = True
    showid = get_value(f'fs_table##{window}')[row][0]
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
    global selected
    selected = False
    
    
def view_tvmaze(sender, data):
    window = str(sender).split('##')[1]
    if not selected:
        set_value(f'##SB{window}', 'No Show was selected yet, nothing to do yet')
    else:
        window = str(sender).split('##')[1]
        get_value(f'Show ID##{window}')
        tvm_link = "  https://www.tvmaze.com/shows/" + str(get_value(f'Show ID##{window}'))
        follow_str = 'open -a safari ' + tvm_link
        os.system(follow_str)
    
    
def execute_shows(sender, data):
    global showid
    global selected
    log_info(f'Executing Submit for Shows with sender {sender} and data {data} with showid {showid}')
    window = str(sender).split('##')[1]
    if not selected:
        set_value(f'##SB{window}', 'No Show was selected yet, nothing to do yet')
    else:
        if window == 'Follow':
            result = tvm_follow('F', showid)
            log_info(f'TVMaze Follow result: {result}')
            set_value(f'##SB{window}', f'Show {showid} update on TVMaze and set Follow = {result}')
            selected = False
        elif window == 'Unfollow':
            result = tvm_follow('U', showid)
            log_info(f'TVMaze Unfollow result: {result}')
            set_value(f'##SB{window}', f'Show {showid} update on TVMaze and set Unfollow = {result}')
            selected = False


def find_show(sender, data):
    log_info(f'Find Show with sender {sender} and data {data}')
    add_window(f'{data}##{sender}', 1250, 600, start_x=15, start_y=35, resizable=False, movable=False,
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
    global follow
    if follow:
        log_info(f'Follow Show already running with sender {sender} and data {data}')
    else:
        log_info(f'Follow Show with sender {sender} and data {data}')
        find_show(sender, 'Follow a Show')
        follow = True
    
    
def unfollow_show(sender, data):
    global unfollow
    if unfollow:
        log_info(f'Unfollow Show already running with sender {sender} and data {data}')
    else:
        log_info(f'Unfollow Show with sender {sender} and data {data}')
        find_show(sender, 'Unfollow a Show')
        unfollow = True
    
    
def skip_show(sender, data):
    global skip
    if skip:
        log_info(f'Skip Show already running with sender {sender} and data {data}')
    else:
        log_info(f'Skip Show with sender {sender} and data {data}')
        find_show(sender, 'Skip a Show')
        skip = True
    
    
def find_downloads(sender, data):
    global find
    if find:
        log_info(f'Find Downloads already running with sender {sender} and data {data}')
    else:
        log_info(f'Find Downloads with sender {sender} and data {data}')
        find_show(sender, 'Find Downloads')
        find = True
    

start_dearpygui()

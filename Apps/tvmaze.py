from dearpygui.dearpygui import *

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


def func_find_shows(si, sn):
    log_info(f'Find Shows SQL with showid {si} and showname {sn}')
    if si == 0 and sn == 'New':
        sql = f'select showid, showname, network, type, showstatus, status, premiered, download ' \
              f'from shows where status = "New" or status = "Undecided" order by premiered'
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


def main_callback(sender, data):
    log_info(f'Main Callback activated {sender}, {data}')
    if sender == 'Shows':
        sql = f'select count(*) from shows where status = "New" or status = "Undecided"'
        if get_data('mode') == 'Prod':
            count = execute_sql(sqltype='Fetch', sql=sql)
        else:
            count = execute_sql(sqltype='Fetch', sql=sql, d='Test-TVM-DB')
        add_data('shows_ds_new_shows', f': {str(count[0][0])}')


def show_fill_table(sender, data):
    log_info(f'Fill Show Table {sender} {data}')
    window = func_breakout_window(sender, 1)
    showid = get_value(f'Show ID##{window}')
    add_data('shows_showid', showid)
    showname = get_value(f'Show Name##{window}')
    if showid == 0 and showname == '':
        set_value(f'##show_showname{window}', 'Nothing was entered in Show ID or Showname')
    
    log_info(f'showid: {showid} - showname: {showname}')
    print(window)
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


def window_close(sender, data):
    window = f'{sender}'
    delete_item(window)
    log_info(f'Delete item (window): "{window}"')


def window_graphs(sender, data):
    window = f'{sender}##graphs'
    if not does_item_exist(window):
        add_window(window, 1250, 600, start_x=15, start_y=35, resizable=True, movable=True, on_close="window_close")
        add_button(f'Refresh##{sender}', callback='graph_refresh')
        add_plot(f'{sender}##plot')
        end_window()
        set_style_window_title_align(0.5, 0.5)
        graph_refresh(sender, data)
        log_info(f'Create item (window): "{window}"')


def window_shows(sender, data):
    window = f'{sender}##window'
    log_info(f'Window Shows {sender}')
    if not does_item_exist(window):
        add_window(window, 1250, 600, start_x=15, start_y=35, resizable=False, movable=True, on_close="window_close")
        if sender == 'Test Window':
            add_tab_bar(f'Tab Bar##{sender}')
            add_tab(f'Tab1', parent=f'Tab Bar##{sender}')
            add_text('some text')
            end_tab()
            add_tab(f'Tab2##{sender}')
            add_text('some other text')
            end_tab()
            end_tab_bar()
        elif sender == 'Show Maintenance' or sender == 'Eval New Shows':
            add_input_int(f'Show ID##{sender}', default_value=0, width=250)
            add_input_text(f'Show Name##{sender}', hint='Use % as wild-card', width=250)
            add_button(f'Clear##{sender}', callback='show_maint_clear')
            add_same_line(spacing=10)
            add_button(f'Search##{sender}', callback='show_fill_table')
            add_seperator()
            add_input_text(f'##show_showname{sender}', readonly=True, default_value='', width=650)
            add_same_line(spacing=10)
            add_button(f'View on TVMaze##{sender}', callback='func_view_tvmaze')
            add_same_line(spacing=10)
            add_button(f'Follow##{sender}', callback='shows_follow')
            add_same_line(spacing=10)
            if sender == 'Eval New Shows':
                add_button(f'Skip##{sender}', callback='shows_skip')
                add_same_line(spacing=10)
                add_button(f'Undecided##{sender}', callback='shows_undecided')
            else:
                add_button(f'Unfollow##{sender}', callback='shows_unfollow')
                add_same_line(spacing=10)
                add_button(f'Start Skipping##{sender}', callback=f'shows_skipping')
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


# Main Program

add_data('shows_ds_new_shows', '0')
add_data('mode', 'Test')
add_data('shows_showid', 0)
add_data('db_opposite', "Production DB")

set_main_window_title(f'TVMaze Management - Test DB')
set_style_window_title_align(0.5, 0.5)
set_main_window_size(2140, 1210)

add_menu_bar('Menu Bar')

add_menu('Shows')
add_menu_item('Eval New Shows', callback='window_shows')
add_same_line(xoffset=115)
add_label_text('##no_new_shows', value='0', data_source='shows_ds_new_shows', color=[250, 250, 0, 250])
add_spacing(count=1)
add_seperator()
add_spacing(count=1)
add_menu_item('Show Maintenance', callback='window_shows')
add_menu('Graphs')
add_menu_item('All Shows', callback='window_graphs')
add_menu_item('Followed Shows', callback='window_graphs')
add_menu_item('In Development Shows', callback='window_graphs')
add_menu_item('Other Shows', callback='window_graphs')
end_menu()
add_spacing(count=1)
add_seperator()
add_spacing(count=1)
add_menu_item('Test Window', callback='window_shows')
end_menu()

add_menu('Tools')
add_menu_item('Toggle Database to', callback='func_toggle_db')
add_same_line(xoffset=140)
add_label_text(f'##db', value='Test', data_source='db_opposite', color=[250, 250, 0, 250])
end_menu()

end_menu_bar()


set_render_callback('main_callback', 'Shows')

show_logger()
set_window_pos('logger##standard', 500, 925)
set_item_width('logger##standard', 1000)
set_item_height('logger##standard', 175)
show_debug()
set_window_pos('debug##standard', 50, 800)

start_dearpygui()

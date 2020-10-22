from dearpygui.core import *
from dearpygui.simple import *
from Libraries.tvm_db import execute_sql


def window_crud_maintenance(sender, data):
    log_info(f'Function: CRUD Maintenance Window, {sender}, {data}')
    if does_item_exist(f'{data}##window'):
        log_info(f'Already exist {data}##window')
        pass
    else:
        if data == 'Key Values':
            table_headers = ['Key', 'Value', 'Comment']
        elif data == 'Plex Shows':
            table_headers = ['Show Name', 'Show Id', 'Cleaned Show Name']
        elif data == 'Plex Episodes':
            table_headers = ['Show Name', 'Season', 'Episode', 'Date Watched', 'TVM Updated', 'TVM Update Status']
        else:
            table_headers = ['Unknown']
        with window(name=f'{data}##window', width=2130, height=650, x_pos=5, y_pos=45):
            add_input_text(name=f'{data}_input', no_spaces=True, multiline=False, decimal=False, label=data, width=200)
            add_same_line(spacing=10)
            add_button(name=f'Search##{data}', callback=func_crud_search, callback_data=data)
            if data == 'Key Values':
                add_same_line(spacing=10)
                add_button(name=f"Add New##{data}")
            add_same_line(spacing=10)
            add_button(name=f"Edit##{data}")
            if data == 'Key Values':
                add_same_line(spacing=10)
                add_button(name=f"Delete##{data}")
            add_same_line(spacing=30)
            add_button(name=f"Clear##{data}", callback=func_crud_clear, callback_data=f'Table##{data}')
            add_separator(name=f'##{data}SEP1')
            add_table(name=f'Table##{data}', headers=table_headers)
            add_separator(name=f'##{data}SEP1')
            

def func_crud_clear(sender, data):
    func_fill_a_table(data, [])
            
            
def func_crud_search(sender, data):
    key = get_value(f'{data}_input')
    if data == 'Key Values':
        sql = f"select * from key_values where `key` like '%{key}%' order by `key`"
    elif data == 'Plex Shows':
        sql = f"select * from TVMazeDB.plex_shows where showname like '%{key}%' order by `showid`, 'cleaned_showname'"
    elif data == 'Plex Episodes':
        sql = f"select * from TVMazeDB.plex_episodes where showname like '%{key}%' " \
              f"order by `showname`, 'season', `episode`"
    else:
        sql = ''
    result = execute_sql(sqltype='Fetch', sql=sql)
    func_fill_a_table(f'Table##{data}', result)


def func_fill_a_table(table_name, data):
    table = []
    for rec in data:
        table_row = []
        for field in rec:
            table_row.append(str(field).replace('None', ''))
        table.append(table_row)
    set_table_data(table_name, table)

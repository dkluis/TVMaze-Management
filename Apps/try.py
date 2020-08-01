from db_lib import *
# from tvm_lib import *
from tvm_api_lib import *
from bs4 import BeautifulSoup as Soup
import re
from tvm_api_lib import execute_tvm_request
from sqlalchemy import create_engine
from datetime import datetime, timedelta, date
import mariadb
import os


def magnetdl_download(show, seas):
    main_link_pre = '''http://www.magnetdl.com/search/?m=1&q="'''
    main_link_suf = '"'
    main_link = main_link_pre + show.replace(' ', '-') + '-' + seas + main_link_suf
    main_link = 'https://www.magnetdl.com/t/the-last-narc/'
    main_link = '''http://www.magnetdl.com/search/?m=1&q="the-last-narc-s01"'''
    # main_link = '''https://stackoverflow.com/questions/27652543/how-to-use-python-requests-to-fake-a-browser-visit'''
    main_request = execute_tvm_request(api=main_link, req_type='get')
    print(main_link, main_request ,main_request.content)
    if not main_request:
        return False, main_link
    titles = main_request['torrent_results']
    dl_options = []
    for title in titles:
        name = title['title']
        magnet = title['download']
        seeders = title['seeders']
        size = title['size']
        prio = validate_requirements(name, False, show)
        if prio > 100:
            dl_options.append((prio, size, seeders, name, magnet))
    if len(dl_options) > 0:
        dl_options.sort(reverse=True)
        for do in dl_options:
            command_str = 'open -a transmission ' + do[4]
            os.system(command_str)
            return True, main_link
    else:
        return False, main_link
    
result = magnetdl_download('the last narc', 's01')
print(result)

quit()

mdbe = create_engine('mysql://dick:Sandy3942@127.0.0.1/TVMazeDB')
df = pd.read_sql_query('select * from statistics', mdbe)
print(df)
quit()

print(generate_insert_sql(primary='1',
                          table='all_shows',
                          showname=('quotes', '"So"ss"mething"'),
                          premiered=('1', '"2020-01-01"'),
                          somethingelse=(1, '123'),
                          tvrage=('none', None)
                          ))

showid = 1
val = 'None'
sql = generate_update_sql(tvmaze_updated=904837504873,
                          tvmaze_upd_da=f"{date.fromtimestamp(1837504873)}",
                          network='CBS',
                          country='USA',
                          record_upd='current_date',
                          alt_sn_override='None',
                          where=f"WHERE showid={showid}",
                          table='shows')

print(sql)
quit()

tvmaze = connect_mdb(d=mdb_info.db)
db = tvmaze['mdb']
cur = tvmaze['mcursor']
execute_sql(con="Y", batch='Y', db=db, cur=cur, sqltype='Commit', sql='')
print(execute_sql(con="Y", db=db, cur=cur, sqltype='Fetch', sql="select * from information_schema.global_variables "
                                                                "where variable_name = 'AUTOCOMMIT';"))
print(execute_sql(con="Y", db=db, cur=cur, sqltype='Commit', sql='SET autocommit = OFF;'))
print(execute_sql(con="Y", db=db, cur=cur, sqltype='Fetch', sql="select * from information_schema.global_variables "
                                                                "where variable_name = 'AUTOCOMMIT';"))

# Adding to a tuple
t = (1, 2, 3)
t = t + (1,)
print(t)
quit()

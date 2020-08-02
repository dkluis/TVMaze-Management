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

import operator

tl = [(151, 'High.Maintenance.S01E05.1080p.WEB.H264-STRiFE[rartv]', 'magnet:?xt=urn:btih:3887e6309509555ebe7c5f49e61c2b7259e6e81a&dn=High.Maintenance.S01E05.1080p.WEB.H264-STRiFE%5Brartv%5D&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2710&tr=udp%3A%2F%2F9.rarbg.to%3A2710&tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce', '0000001872', 'rarbgAPI'), (141, 'High.Maintenance.S01E05.Selfie.720p.HBO.WEBRip.DD5.1.H264-monkee[rartv]', 'magnet:?xt=urn:btih:e13d90416126a167081a8fe6cb740cfbb8f7f9e2&dn=High.Maintenance.S01E05.Selfie.720p.HBO.WEBRip.DD5.1.H264-monkee%5Brartv%5D&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2710&tr=udp%3A%2F%2F9.rarbg.to%3A2710&tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce', '0000000671', 'rarbgAPI'), (151, 'High.Maintenance.S01E05.Selfie.1080p.HBO.WEBRip.DD5.1.H264-monkee[rartv]', 'magnet:?xt=urn:btih:236d559f63327407a0468594c806682c2e98b13d&dn=High.Maintenance.S01E05.Selfie.1080p.HBO.WEBRip.DD5.1.H264-monkee%5Brartv%5D&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2710&tr=udp%3A%2F%2F9.rarbg.to%3A2710&tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce', '0000000834', 'rarbgAPI'), (141, 'High.Maintenance.S01E05.720p.HDTV.x264-SVA[rartv]', 'magnet:?xt=urn:btih:3ebc84491c90f0d896625fa29fba435372affdf0&dn=High.Maintenance.S01E05.720p.HDTV.x264-SVA%5Brartv%5D&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2710&tr=udp%3A%2F%2F9.rarbg.to%3A2710&tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce', '0000000631', 'rarbgAPI'), (131, 'High.Maintenance.S01E05.480p.x264-mSD', 'magnet:?xt=urn:btih:00A373AEFF52B6C24D6AC80DDD6F7CF09F85C6A0', '0000000129', 'piratebay'), (151, 'High Maintenance S01E05 MULTi 1080p HDTV H264-HYBRiS', 'magnet:?xt=urn:btih:932742073F54027EF9DEDA96402505377ED4932D', '0000001610', 'piratebay'), (151, 'High.Maintenance.S01E05.1080p.WEB.H264-STRiFE', 'magnet:?xt=urn:btih:07A632F57185938AFC3A015E00D103A74A2D6575', '0000001750', 'piratebay')]
for t in tl:
    print(t[0], t[3], t[1])
# tl.sort(reverse=True, key=operator.itemgetter(1, 2))
tls = sorted(tl, key=lambda x: [x[0], x[3]], reverse=True)
print()
print()
for t in tls:
    print(t[0], t[3], t[1])
quit()


'''
db_name = "Testing_Init_DB"
print(f"Create the {db_name} schema {execute_sql(d='', sqltype='Commit', sql=create_db_sql(db_name))}")
print('Create the key_values table', execute_sql(d=db_name, sqltype='Commit', sql=create_tb_key_values.sql))
print('Fill the key_values table', execute_sql(d=db_name, sqltype='Commit', sql=create_tb_key_values.fill))
quit()
'''


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

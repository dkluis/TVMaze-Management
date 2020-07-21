from db_lib import *
from datetime import date
from tvm_lib import *
from tvm_api_lib import *
from bs4 import BeautifulSoup as Soup
import re
from tvm_api_lib import execute_tvm_request

from datetime import datetime, timedelta

print('Filling the Statistics Table')
statistics = execute_sqlite(sqltype='Fetch', sql='SELECT * from statistics order by statepoch ')
print(len(statistics))
for rec in statistics:
    ins_sql = "INSERT INTO statistics VALUES {0};".format(str(rec).replace('None', 'NULL').replace("''", "NULL"))
    execute_sql(sqltype="Commit", sql=ins_sql)

quit()

from sqlalchemy import create_engine

mdbe = create_engine('mysql+mysqlconnector://[dick]:[Sandy3942]@localhost/[TVMazeDB]')

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

t = (1, 2, 3)
t = t + (1,)
print(t)


def find_via_showname(sn):
    to_download = execute_sql(sqltype='Fetch', sql=f"SELECT * from shows WHERE `showname` = '{sn}';")
    if len(to_download) == 0:
        return False
    return to_download


print(find_via_showname('LOST girl'))

'''SQL Stuff (Tests)'''
print(execute_sql(sqltype='Fetch', sql=tvm_views.shows_to_review))
print(execute_df(sql=tvm_views.shows_to_review))
print(execute_df(sql=stat_views.downloaders))
print(execute_df(sql=stat_views.shows))
print(execute_df(sql=stat_views.episodes))
print(execute_df(sql=stat_views.count))

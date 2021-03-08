
"""

statistics     The App that handles finding and inserting as well as updating all statistics for the followed shows
                This is based on the TVMaze API to request all episode info for all followed shows.

Usage:
  statistics -s [--vl=<vlevel]
  statistics [--vl=<vlevel>]
  statistics -h | --help
  statistics --version


Options:
  -s                    Store the Statistics
  -h --help             Show this screen
  --vl=<vlevel>         Level of verbosity
                          1 = Warnings & Errors Only, 2 = High Level Info,
                          3 = Medium Level Info, 4 = Low Level Info, 5 = All  [default: 1]
  --version             Show version.

"""

from docopt import docopt
# import pandas as pd
# from sqlalchemy import create_engine

from Libraries import get_today, time, stat_views, mariaDB, logging, check_vli


def count_by_download_options():
    rarbg_api = db.execute_sql(sqltype='Fetch',
                               sql="SELECT COUNT(*) from shows WHERE download = 'rarbgAPI' AND status = 'Followed'")
    rarbg = db.execute_sql(sqltype='Fetch',
                           sql="SELECT COUNT(*) from shows WHERE download = 'rarbg' AND status = 'Followed'")
    rarbgmirror = db.execute_sql(sqltype='Fetch',
                                 sql="SELECT COUNT(*) from shows "
                                     "WHERE download = 'rarbgmirror' AND status = 'Followed'")
    showrss = db.execute_sql(sqltype='Fetch',
                             sql="SELECT COUNT(*) from shows WHERE download = 'ShowRSS' AND status = 'Followed'")
    eztv_api = db.execute_sql(sqltype='Fetch',
                              sql="SELECT COUNT(*) from shows WHERE download = 'eztvAPI' AND status = 'Followed'")
    no_dl = db.execute_sql(sqltype='Fetch',
                           sql="SELECT COUNT(*) from shows WHERE download is NULL AND status = 'Followed'")
    skip = db.execute_sql(sqltype='Fetch',
                          sql="SELECT COUNT(*) from shows WHERE download = 'Skip' AND status = 'Followed'")
    eztv = db.execute_sql(sqltype='Fetch',
                          sql="SELECT COUNT(*) from shows WHERE download = 'eztv' AND status = 'Followed'")
    magnetdl = db.execute_sql(sqltype='Fetch',
                              sql="SELECT COUNT(*) from shows WHERE download = 'magnetdl' AND status = 'Followed'")
    torrentfunk = db.execute_sql(sqltype='Fetch',
                                 sql="SELECT COUNT(*) from shows "
                                     "WHERE download = 'torrentfunk' AND status = 'Followed'")
    piratebay = db.execute_sql(sqltype='Fetch',
                               sql="SELECT COUNT(*) from shows WHERE download = 'piratebay' AND status = 'Followed'")
    multi = db.execute_sql(sqltype='Fetch',
                           sql="SELECT COUNT(*) from shows WHERE download = 'Multi' AND status = 'Followed'")
    value = (no_dl[0][0], rarbg_api[0][0], rarbg[0][0], rarbgmirror[0][0], showrss[0][0], skip[0][0],
             eztv_api[0][0], eztv[0][0], magnetdl[0][0], torrentfunk[0][0], piratebay[0][0], multi[0][0])
    return value


def go_store_statistics(f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12):
    today_epoch = int(get_today('system'))
    today_human = f"'{str(get_today('human'))[:-7]}'"
    last_rec = view_history(True)
    if len(last_rec) != 0:
        if (str(f1) == str(last_rec[2]) and
                str(f2) == str(last_rec[3]) and
                str(f3) == str(last_rec[4]) and
                str(f4) == str(last_rec[5]) and
                str(f5) == str(last_rec[6]) and
                str(f6) == str(last_rec[7]) and
                str(f7) == str(last_rec[8]) and
                str(f8) == str(last_rec[9]) and
                str(f9) == str(last_rec[10]) and
                str(f10) == str(last_rec[11]) and
                str(f11) == str(last_rec[12]) and
                str(f12) == str(last_rec[13])):
            if vli > 1:
                log.write(f"No Update for TVMaze", 2)
            return False
    sql = f"INSERT INTO statistics VALUES ({today_epoch}, {today_human}, {f1}, {f2}, {f3}, {f4}, {f5}, {f6}, {f7}, " \
          f"{f8}, {f9}, {f10}, {f11}, {f12}, " \
          f"'TVMaze', Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, Null);"
    sql = sql.replace('None', 'NULL')
    db.execute_sql(sqltype='Commit', sql=sql)
    if vli > 1:
        log.write(f"Updated TVMaze", 2)
    return True


def go_store_download_options(dls_in):
    stats = db.execute_sql(sql='SELECT * from statistics where statrecind = "Downloaders" order by statdate desc ',
                           sqltype='Fetch')
    if len(stats) != 0:
        stats = stats[0]
        if (str(dls_in[0]) == str(stats[15]) and
                str(dls_in[1]) == str(stats[16]) and
                str(dls_in[2]) == str(stats[17]) and
                str(dls_in[3]) == str(stats[18]) and
                str(dls_in[4]) == str(stats[19]) and
                str(dls_in[5]) == str(stats[20]) and
                str(dls_in[6]) == str(stats[21]) and
                str(dls_in[7]) == str(stats[22]) and
                str(dls_in[8]) == str(stats[23]) and
                str(dls_in[9]) == str(stats[24]) and
                str(dls_in[10]) == str(stats[25]) and
                str(dls_in[11]) == str(stats[26])):
            if vli > 1:
                log.write(f"No Update for Download Options", 2)
        else:
            time.sleep(1)
            today_epoch = int(get_today('system'))
            today_human = f"'{str(get_today('human'))[:-7]}'"
            sql = f"INSERT INTO statistics VALUES ({today_epoch}, {today_human}, " \
                  f"Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,'Downloaders', " \
                  f"{dls_in[0]}, {dls_in[1]}, {dls_in[2]}, {dls_in[3]}, {dls_in[4]}, {dls_in[5]}, " \
                  f"{dls_in[6]}, {dls_in[7]}, {dls_in[8]}, {dls_in[9]}, {dls_in[10]}, {dls_in[11]});"
            sql = sql.replace('None', 'NULL')
            db.execute_sql(sql=sql, sqltype='Commit')
            if vli > 1:
                log.write(f"Updated Download Options", 2)


def view_history(last: False):
    if last:
        shows = db.execute_sql(sqltype='Fetch',
                               sql='SELECT * from statistics where statrecind = "TVMaze" order by statdate desc ')
        if len(shows) == 0:
            return False
        else:
            return shows[0]
    # else:
    #    mdb_engine = create_engine(f'mysql+pymsql://user:password@localhost/db?host=localhost?port=3306')
    #    mdbe = mdb_engine.connect()
    #    pd.set_option('max_rows', 31)
    #    pd.set_option('min_rows', 30)
    #    df = pd.read_sql_query('select statepoch, statdate, tvmshows, myshows, myshowsended,'
    #                           'myshowstbd, myshowsrunning, myshowsindevelopment,'
    #                           'myepisodes, myepisodeswatched, myepisodestowatch, myepisodesskipped, '
    #                           'myepisodestodownloaded, myepisodesannounced '
    #                           'from statistics where statrecind = "TVMaze" order by statepoch', mdbe)
    #    print(df)
    return


'''
Main Program
'''
log = logging(caller='Statistics', filename='Process')
log.start()

options = docopt(__doc__, version='Statistics Release 1.0')
vli = check_vli(options, log)

db = mariaDB(caller=log.caller, filename=log.filename, vli=vli)

tvmshows = db.execute_sql(sql=stat_views.count_all_shows, sqltype="Fetch")[0][0]
myshows = db.execute_sql(sql=stat_views.count_my_shows, sqltype="Fetch")[0][0]
myshowsrunning = db.execute_sql(sql=stat_views.count_my_shows_running, sqltype="Fetch")[0][0]
myshowsended = db.execute_sql(sql=stat_views.count_my_shows_ended, sqltype="Fetch")[0][0]
myshowstbd = db.execute_sql(sql=stat_views.count_my_shows_in_limbo, sqltype="Fetch")[0][0]
myshowsid = db.execute_sql(sql=stat_views.count_my_shows_in_development, sqltype="Fetch")[0][0]
tvmshows_skipped = db.execute_sql(sql=stat_views.count_all_shows_skipped, sqltype="Fetch")[0][0]

myeps = db.execute_sql(sql=stat_views.count_my_episodes, sqltype='Fetch')[0][0]
mywatchedeps = db.execute_sql(sql=stat_views.count_my_episodes_watched, sqltype='Fetch')[0][0]
mytowatcheps = db.execute_sql(sql=stat_views.count_my_episodes_to_watch, sqltype='Fetch')[0][0]
myskippedeps = db.execute_sql(sql=stat_views.count_my_episodes_skipped, sqltype='Fetch')[0][0]
mytodownloadeps = db.execute_sql(sql=stat_views.count_my_episodes_to_download, sqltype='Fetch')[0][0]
myfutureeps = db.execute_sql(sql=stat_views.count_my_episodes_future, sqltype='Fetch')[0][0] - mytodownloadeps

dls = count_by_download_options()

if options['-s']:
    log.write(f"Storing Option Selected")
    go_store_statistics(tvmshows, myshows, myshowsrunning, myshowsended, myshowstbd, myshowsid,
                        myeps, mywatchedeps, mytowatcheps, myskippedeps, mytodownloadeps, myfutureeps)
    go_store_download_options(dls)
else:
    log.write(f'No option like -d, -s, or -v was supplied', 0)
    
db.close()
log.end()
quit()

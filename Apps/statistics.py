from terminal_lib import *
from tvm_lib import get_today, count_by_download_options
from db_lib import stat_views, execute_sql, connect_mdb, close_mdb
import pandas as pd
from sqlalchemy import create_engine
import time


def get_cli_args():
    tlc = ["-d", "-s", "-v"]
    flc = check_cli_args(tlc)
    if flc['-s']:
        # Store in Table
        return 'Store'
    elif flc['-d']:
        # View current
        return 'Display'
    elif flc['-v']:
        # View history from Table
        return "View"
    else:
        print('No input parameter of -d. -s. or -v provided')
        quit()


def go_store_statistics(f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12):
    today_epoch = int(get_today('system'))
    today_human = f"'{str(get_today('human'))[:-7]}'"
    # Make sure that only new info is stored
    last_rec = view_history(True)
    if last_rec:
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
            print("No Update for TVMaze: ", last_rec)
            return False
    sql = f"INSERT INTO statistics VALUES ({today_epoch}, {today_human}, {f1}, {f2}, {f3}, {f4}, {f5}, {f6}, {f7}, " \
          f"{f8}, {f9}, {f10}, {f11}, {f12}, " \
          f"'TVMaze', None, None, None, None, None, None, None, None, None, None, None);"
    sql = sql.replace('None', 'NULL')
    execute_sql(sqltype='Commit', sql=sql)
    return True


def go_store_download_options(dls):
    stats = execute_sql(sql='SELECT * from statistics where statrecind = "Downloaders" order by statdate desc ',
                        sqltype='Fetch')
    if len(stats) != 0:
        stats = stats[0]
        if (str(dls[0]) == str(stats[15]) and
                str(dls[1]) == str(stats[16]) and
                str(dls[2]) == str(stats[17]) and
                str(dls[3]) == str(stats[18]) and
                str(dls[4]) == str(stats[19]) and
                str(dls[5]) == str(stats[20]) and
                str(dls[6]) == str(stats[21]) and
                str(dls[7]) == str(stats[22]) and
                str(dls[8]) == str(stats[23]) and
                str(dls[9]) == str(stats[24]) and
                str(dls[10]) == str(stats[25])):
            print("No Update for download_options: ", stats)
        else:
            time.sleep(1)
            today_epoch = int(get_today('system'))
            today_human = f"'{str(get_today('human'))[:-7]}'"
            sql = f"INSERT INTO statistics VALUES ({today_epoch}, {today_human}, " \
                  f"None, None, None, None, None, None, None, None, None, None, None, None, 'Downloaders', " \
                  f"{dls[0]}, {dls[1]}, {dls[2]}, {dls[3]}, {dls[4]}, {dls[5]}, " \
                  f"{dls[6]}, {dls[7]}, {dls[8]}, {dls[9]}, {dls[10]});"
            sql = sql.replace('None', 'NULL')
            execute_sql(sql=sql, sqltype='Commit')


def view_history(last: False):
    shows = execute_sql(sqltype='Fetch',
                        sql='SELECT * from statistics where statrecind = "TVMaze" order by statdate desc ')

    mdbe = create_engine('mysql://dick:Sandy3942@127.0.0.1/TVMazeDB')
    if last:
        if len(shows) == 0:
            return False
        else:
            return shows[0]
    else:
        pd.set_option('max_rows', 31)
        pd.set_option('min_rows', 30)
        df = pd.read_sql_query('select statepoch, statdate, tvmshows, myshows, myshowsended,'
                               'myshowstbd, myshowsrunning, myshowsindevelopment,'
                               'myepisodes, myepisodeswatched, myepisodestowatch, myepisodesskipped, '
                               'myepisodestodownloaded, myepisodesannounced '
                               'from statistics where statrecind = "TVMaze" order by statepoch asc', mdbe)
        print(df)
    return


'''
Main Program
'''
print()
print('Statistics Started')
tvmshows = execute_sql(sql=stat_views.count_all_shows, sqltype="Fetch")[0][0]
myshows = execute_sql(sql=stat_views.count_my_shows, sqltype="Fetch")[0][0]
myshowsrunning = execute_sql(sql=stat_views.count_my_shows_running, sqltype="Fetch")[0][0]
myshowsended = execute_sql(sql=stat_views.count_my_shows_ended, sqltype="Fetch")[0][0]
myshowstbd = execute_sql(sql=stat_views.count_my_shows_in_limbo, sqltype="Fetch")[0][0]
myshowsid = execute_sql(sql=stat_views.count_my_shows_in_development, sqltype="Fetch")[0][0]
tvmshows_skipped = execute_sql(sql=stat_views.count_all_shows_skipped, sqltype="Fetch")[0][0]

myeps = execute_sql(sql=stat_views.count_my_episodes, sqltype='Fetch')[0][0]
mywatchedeps = execute_sql(sql=stat_views.count_my_episodes_watched, sqltype='Fetch')[0][0]
mytowatcheps = execute_sql(sql=stat_views.count_my_episodes_to_watch, sqltype='Fetch')[0][0]
myskippedeps = execute_sql(sql=stat_views.count_my_episodes_skipped, sqltype='Fetch')[0][0]
mytodownloadeps = execute_sql(sql=stat_views.count_my_episodes_to_download, sqltype='Fetch')[0][0]
myfutureeps = execute_sql(sql=stat_views.count_my_episodes_future, sqltype='Fetch')[0][0] - mytodownloadeps

dls = count_by_download_options()

prog_option = get_cli_args()
if prog_option == "Display":
    print(term_pos(menu_pos.status_x + 1, menu_pos.menu_2y) + "Total # of Shows on TVMaze         :",
          str(format(tvmshows, ',d')))
    print(term_pos(menu_pos.status_x + 3, menu_pos.menu_2y) + "Number of My Shows                 :",
          str(format(myshows, ',d')).rjust(6))
    print(term_pos(menu_pos.status_x + 4, menu_pos.menu_2y) + "Number of My Shows ended           :",
          str(myshowsended).rjust(6))
    print(term_pos(menu_pos.status_x + 5, menu_pos.menu_2y) + "Number of My Shows to be determined:",
          str(myshowstbd).rjust(6))
    print(term_pos(menu_pos.status_x + 6, menu_pos.menu_2y) + "Number of My Shows running         :",
          str(myshowsrunning).rjust(6))
    print(term_pos(menu_pos.status_x + 7, menu_pos.menu_2y) + "Number of My Shows in development  :",
          str(myshowsid).rjust(6))
    
    print(term_pos(menu_pos.status_x + 1, menu_pos.menu_3y) + "Total # of My Episodes             :",
          str(format(myeps, ',d')))
    print(term_pos(menu_pos.status_x + 3, menu_pos.menu_3y) + "Number of My Episodes watched      :",
          str(format(mywatchedeps, ',d')).rjust(6))
    print(term_pos(menu_pos.status_x + 4, menu_pos.menu_3y) + "Number of My Episodes to watch     :",
          str(format(mytowatcheps, ',d')).rjust(6))
    print(term_pos(menu_pos.status_x + 5, menu_pos.menu_3y) + "Number of My Episodes skipped      :",
          str(format(myskippedeps, ',d')).rjust(6))
    print(term_pos(menu_pos.status_x + 6, menu_pos.menu_3y) + "Number of My Episodes to download  :",
          str(format(mytodownloadeps, ',d')).rjust(6))
    print(term_pos(menu_pos.status_x + 7, menu_pos.menu_3y) + "Number of My Episodes upcoming     :",
          str(format(myfutureeps, ',d')).rjust(6))
elif prog_option == "Store":
    print("TVMaze Statistics Update")
    go_store_statistics(tvmshows, myshows, myshowsrunning, myshowsended, myshowstbd, myshowsid,
                        myeps, mywatchedeps, mytowatcheps, myskippedeps, mytodownloadeps, myfutureeps)
    go_store_download_options(dls)
    print()
else:
    print()
    view_history(False)

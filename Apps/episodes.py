from tvm_api_lib import *
from db_lib import *
from terminal_lib import *

from timeit import default_timer as timer
from datetime import datetime, date

'''Main Program'''
print(term_codes.cl_scr)

started = timer()
print(f'{str(datetime.now())} -> Starting to process recently updated episodes for insert and re-sync')

shows = execute_sql(sqltype='Fetch', sql="SELECT * FROM shows "
                                         "where status = 'Followed' and  record_updated = current_date")
# shows = [(32, "Fargo")]
show_num = (len(shows))
total_episodes = 0
updated = 0
inserted = 0
for show in shows:
    api = f"{tvm_apis.episodes_by_show_pre}{show[0]}{tvm_apis.episodes_by_show_suf}"
    episodes = execute_tvm_request(api=api, sleep=0.5)
    if not episodes:
        continue
    episodes = episodes.json()
    num_eps = len(episodes)
    total_episodes = total_episodes + num_eps
    for epi in episodes:
        result = execute_sql(sql="SELECT * from episodes WHERE epiid = {0}".format(epi['id']), sqltype="Fetch")
        if len(result) == 0:
            if epi['airdate'] == '':
                airdate = None
            else:
                airdate = f"'{epi['airdate']}'"
            sql = generate_insert_sql(
                table='episodes',
                primary=epi['id'],
                f1=(1, show[0]),
                f2=(2, f'''"{str(epi['name']).replace('"', ' ')}"'''),
                f3=(3, f"'{epi['url']}'"),
                f4=(4, epi['season']),
                f5=(5, epi['number']),
                f6=(6, airdate),
                f7=(7, None),
                f8=(8, None),
                f9=(9, f"'{str(datetime.now())[:10]}'")
            )
            sql = sql.replace("'None'", 'NULL').replace('None', 'NULL')
            execute_sql(sql=sql, sqltype='Commit')
            inserted += 1
        elif len(result) == 1:
            if epi['airdate'] is None or epi['airdate'] == '':
                sql = generate_update_sql(epiname=epi['name'],
                                          url=epi['url'],
                                          season=epi['season'],
                                          episode=epi['number'],
                                          rec_updated=f"'{str(datetime.now())[:10]}'",
                                          where=f"epiid={epi['id']}",
                                          table='episodes')
            else:
                sql = generate_update_sql(epiname=epi['name'],
                                          url=epi['url'],
                                          season=epi['season'],
                                          episode=epi['number'],
                                          airdate=f"'{epi['airdate']}'",
                                          rec_updated=f"'{str(datetime.now())[:10]}'",
                                          where=f"epiid={epi['id']}",
                                          table='episodes')
            sql = sql.replace('None', 'NULL')
            execute_sql(sql=sql, sqltype='Commit')
            updated += 1
        else:
            print("Should not happen")
            quit()
        if (updated + inserted) % 250 == 0:
            print(f'Processed {updated + inserted} records')
    # print(f'Do Show update for {show[0]}')
    execute_sql(sqltype='Commit', sql=f'UPDATE shows '
                                      f'set eps_updated = current_date, eps_count = {num_eps} '
                                      f'WHERE showid = {show[0]}')

print(f"Updated existing episodes: {updated} and Inserted new episodes: {inserted}")
print("Episodes Table --->", "Total number of shows:   ", len(shows))
print("Episodes Table --->", "Total number of episodes:", total_episodes)
ended = timer()
print(f'{str(datetime.now())} -> The process (including calling the TVMaze APIs) took: {ended - started} seconds')
print()

print("Starting update of episode statuses for (watched, downloaded and skipped) and what date")
episodes = execute_tvm_request(api=tvm_apis.episodes_status, code=True, sleep=0)
eps_updated = episodes.json()
updated = 0
print("Episodes to process: ", len(eps_updated))
for epi in eps_updated:
    if epi['type'] == 0:
        watch = "Watched"
    elif epi['type'] == 1:
        watch = "Downloaded"
    else:
        watch = "Skipped"
    if epi['marked_at'] == 0:
        when = None
    else:
        when = date.fromtimestamp(epi['marked_at'])
    if when is None:
        sql = generate_update_sql(mystatus=watch,
                                  mystatus_date=None,
                                  rec_updated=f"'{str(datetime.now())[:10]}'",
                                  where=f"epiid={epi['episode_id']}",
                                  table='episodes')
    else:
        sql = generate_update_sql(mystatus=watch,
                                  mystatus_date=f"'{when}'",
                                  rec_updated=f"'{str(datetime.now())[:10]}'",
                                  where=f"epiid={epi['episode_id']}",
                                  table='episodes')
    sql = sql.replace('None', 'NULL')
    result = execute_sql(sqltype='Commit', sql=sql)
    updated += 1
    if updated % 5000 == 0:
        print(f"Processed {updated} records")

print("Total Episodes updated:", updated)

print('Starting to find episodes to reset back')
found = False
result = execute_sql(sqltype='Fetch', sql=std_sql.episodes)
count = 0
ep_list = []
for res in result:
    count += 1
    for epi in eps_updated:
        if epi['episode_id'] == res[0]:
            found = True
            break
        else:
            found = False
    if not found:
        ep_list.append(res[0])
    if count % 5000 == 0:
        print(f'Processed {count} records')

print(f'Number of Episodes to reset is {len(ep_list)}')

for epi in ep_list:
    result = execute_sql(sqltype='Commit', sql=f'UPDATE episodes '
                                               f'SET mystatus = NULL, mystatus_date = NULL '
                                               f'WHERE epiid = {epi}')
    if not result:
        print(f'Epi reset for {epi} went wrong {result}')

print()

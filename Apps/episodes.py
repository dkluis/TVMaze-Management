"""

episodes.py     The App that handles finding and inserting as well as updating all episodes for the followed shows
                This is based on the TVMaze API to request all episode info for all followed shows.

Usage:
  episodes.py [--vl=<vlevel>]
  episodes.py -h | --help
  episodes.py --version


Options:
  -h --help             Show this screen
  --vl=<vlevel>         Level of verbosity (a = All, i = Informational, w = Warnings only) [default: w]
  --version             Show version.

"""

from tvm_api_lib import *
from db_lib import *
from docopt import docopt

from timeit import default_timer as timer
from datetime import datetime, date


'''Main Program'''
options = docopt(__doc__, version='Shows Release 0.9.5')
vli = False
vlw = True
if options['--vl'].lower() == 'a':
    vli = True
elif options['--vl'].lower() == 'i':
    vli = True
if vli:
    print(f'verbosity levels Informational {vli} and Warnings {vlw}')
    print(options)

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
            if vli:
                print(f'Working on EPI: {epi["id"]}')
            if epi['airdate'] is None or epi['airdate'] == '':
                sql = generate_update_sql(epiname=str(epi['name']).replace('"', ' '),
                                          url=epi['url'],
                                          season=epi['season'],
                                          episode=epi['number'],
                                          rec_updated=f"'{str(datetime.now())[:10]}'",
                                          where=f"epiid={epi['id']}",
                                          table='episodes')
            else:
                sql = generate_update_sql(epiname=str(epi['name']).replace('"', ' '),
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
            print(f"Found more than 1 record for {epi['id']} episode which should not happen")
            quit()
        if (updated + inserted) % 250 == 0:
            if vli:
                print(f'Processed {updated + inserted} records')
    if vli:
        print(f'Do Show update for {show[0]}')
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
if vli:
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
        if vli:
            print(f"Processed {updated} records")

print("Total Episodes updated:", updated)

print('Starting to find episodes to reset')
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
        if vli:
            print(f'Processed {count} records')

print(f'Number of Episodes to reset is {len(ep_list)}')
for epi in ep_list:
    result = execute_sql(sqltype='Commit', sql=f'UPDATE episodes '
                                               f'SET mystatus = NULL, mystatus_date = NULL '
                                               f'WHERE epiid = {epi}')
    if not result:
        print(f'Epi reset for {epi} went wrong {result}')
print()

# Checking to see if there are any episodes with no status on TVMaze for Followed shows set to skip downloading
# and tracking so that we can set them to skipped on TVMaze

eps_to_update = execute_sql(sqltype='Fetch', sql=tvm_views.eps_to_check)
if len(eps_to_update) != 0:
    print(f'There are {len(eps_to_update)} episodes to update')
    for epi in eps_to_update:
        baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(epi[0])
        epoch_date = int(date.today().strftime("%s"))
        data = {"marked_at": epoch_date, "type": 2}
        response = execute_tvm_request(baseurl, data=data, req_type='put', code=True)
        print(f'Updating Epi {epi[0]} as Skipped since the Show download is set to Skip')

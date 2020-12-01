"""

episodes.py     The App that handles finding and inserting as well as updating all episodes for the followed shows
                This is based on the TVMaze API to request all episode info for all followed shows.

Usage:
  episodes.py [--vl=<vlevel>]
  episodes.py -s [--vl=<vlevel>]
  episodes.py -h | --help
  episodes.py --version


Options:
  -s                    list all shows with Episodes watched and/ or skipped that are set to 'Followed' in Shows
  -h --help             Show this screen
  --vl=<vlevel>         Level of verbosity
                          1 = Warnings & Errors Only, 2 = High Level Info,
                          3 = Medium Level Info, 4 = Low Level Info, 5 = All  [default: 1]
  --version             Show version.

"""

from Libraries.tvm_apis import *
from Libraries.tvm_db import *
from Libraries.tvm_logging import logging

from time import sleep
from docopt import docopt
from timeit import default_timer as timer
from datetime import datetime, date
from bs4 import BeautifulSoup as Soup


def find_shows_not_followed_or_skipped():
    logfile = logging(caller='Episodes - Shows Not Followed', filename='Episodes without Shows')
    episodes_found = execute_tvm_request(api=tvm_apis.get_episodes_status, code=True, sleep=0)
    eps_to_process = episodes_found.json()
    logfile.write(f'Number of Episodes to Process {len(eps_to_process)}')
    log.write(f'Number of Episodes to Process {len(eps_to_process)}')
    base_url = 'https://www.tvmaze.com/episodes/'
    base_show = ''
    base_epi = -1
    for epi in eps_to_process:
        print(f'Processing {epi["episode_id"]}')
        if vli > 2:
            logfile.write(f'Processing: {epi["episode_id"]}', 2)
        sql = f'select e.showid, s.status ' \
              f'from episodes e join shows s on e.showid = s.showid ' \
              f'where e.epiid = {epi["episode_id"]}'
        show_info = execute_sql(sqltype='Fetch', sql=sql)
        if epi['episode_id'] == base_epi + 1:
            base_epi = epi['episode_id']
            continue
        if not show_info:
            api = base_url + str(epi['episode_id'])
            result = execute_tvm_request(api=api, req_type='get', sleep=2.25)
            if not result:
                logfile.write(f'Could not get info from TVMaze for {api}')
                base_epi = epi['episode_id']
                continue
            page = Soup(result.content, 'html.parser')
            show_page = page.findAll('div', {"id": "general-info-panel"})
            link_page = show_page[0].findAll('a')
            for link in link_page:
                split_link = str(link).split('/')
                if split_link[1] == 'shows':
                    show_id = split_link[2]
                    if base_show != show_id:
                        base_show = show_id
                        logfile.write(f'>>>>>>>>>>>>>>>>>>>>>> Found a showid: {show_id} to follow')
                        episode_processing(show_id, logfile)
                    break
            base_epi = epi['episode_id']
            continue
        if len(show_info) != 1:
            logfile.write(f'Episode Info {epi} found multiple records >>>>>>>>>>>>>> {show_info}', 0)
            base_epi = epi['episode_id']
            continue


def episode_processing(single='', logfile=''):
    started = timer()
    if single == '':
        if vli > 1:
            log.write(f'Starting to process recently updated episodes for insert and re-sync')
        shows_sql = "SELECT * FROM shows " \
                    "where status = 'Followed' and (record_updated = current_date or eps_updated is Null)"
        shows_sql = shows_sql.replace('None', 'Null')
        shows = execute_sql(sqltype='Fetch', sql=shows_sql)
    else:
        # shows = [(32, "Fargo")]
        # show_num = (len(shows))
        shows = [(single, 'A Show')]
        logfile.write(f'Starting to process Single Show: {single}')
    total_episodes = 0
    updated = 0
    inserted = 0
    for show in shows:
        api = f"{tvm_apis.get_episodes_by_show_pre}{show[0]}{tvm_apis.get_episodes_by_show_suf}"
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
                if vli > 3:
                    log.write(f'Working on EPI: {epi["id"]}', 4)
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
                log.write(f"Found more than 1 record for {epi['id']} episode which should not happen", 0)
                log.end()
                quit()
            if (updated + inserted) % 250 == 0:
                if vli > 2:
                    log.write(f'Processed {updated + inserted} records', 3)
        if vli > 2:
            log.write(f'Do Show update for {show[0]}', 3)
        execute_sql(sqltype='Commit', sql=f'UPDATE shows '
                                          f'set eps_updated = current_date, eps_count = {num_eps} '
                                          f'WHERE showid = {show[0]}')
    
    log.write(f"Updated existing episodes: {updated} and Inserted new episodes: {inserted}")
    log.write(f"Total number of shows: {len(shows)}")
    log.write(f"Total number of episodes: {total_episodes}")
    ended = timer()
    log.write(f'The process (including calling the TVMaze APIs) took: {ended - started} seconds')
    
    log.write(f"Starting update of episode statuses and date")
    episodes = execute_tvm_request(api=tvm_apis.get_episodes_status, code=True, sleep=0)
    eps_updated = episodes.json()
    updated = 0
    if vli > 2:
        log.write(f"Episodes to process: {len(eps_updated)}", 3)
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
        execute_sql(sqltype='Commit', sql=sql)
        updated += 1
        if updated % 5000 == 0:
            if vli > 2:
                log.write(f"Processed {updated} records", 3)
    
    log.write(f"Total Episodes updated: {updated}")
    if single != '':
        logfile.write(f'Finished Single')
        return
    
    log.write(f'Starting to find episodes to reset')
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
            if vli > 2:
                log.write(f'Processed {count} records', 3)
    
    log.write(f'Number of Episodes to reset is {len(ep_list)}')
    for epi in ep_list:
        result = execute_sql(sqltype='Commit', sql=f'UPDATE episodes '
                                                   f'SET mystatus = NULL, mystatus_date = NULL '
                                                   f'WHERE epiid = {epi}')
        if not result:
            log.write(f'Epi reset for {epi} went wrong {result}')
    
    # Checking to see if there are any episodes with no status on TVMaze for Followed shows set to skip downloading
    # and tracking so that we can set them to skipped on TVMaze
    
    eps_to_update = execute_sql(sqltype='Fetch', sql=tvm_views.eps_to_check)
    if len(eps_to_update) != 0:
        log.write(f'There are {len(eps_to_update)} episodes to update')
        for epi in eps_to_update:
            baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(epi[0])
            epoch_date = int(date.today().strftime("%s"))
            data = {"marked_at": epoch_date, "type": 2}
            response = execute_tvm_request(baseurl, data=data, req_type='put', code=True)
            if not response:
                log.write(f'TVMaze update did not work: {baseurl}, {data} {response}')
            else:
                log.write(f'Updating Epi {epi[0]} as Skipped since the Show download is set to Skip')


'''Main Program'''
log = logging(caller='Episodes', filename='Process')
log.open()
log.close()
log.start()

options = docopt(__doc__, version='Episodes Release 1.0')
vli = int(options['--vl'])
if vli > 5 or vli < 1:
    log.write(f"Unknown Verbosity level of {vli}, try plex_extract.py -h", 0)
    quit()
elif vli > 1:
    log.write(f'Verbosity level is set to: {options["--vl"]}')

if options['-s']:
    log.write(f'Processing Episodes where Shows are not set for "Followed"')
    find_shows_not_followed_or_skipped()
else:
    episode_processing()

log.end()
quit()

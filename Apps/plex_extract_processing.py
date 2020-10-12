"""

plex_extract_processing.py   The App that picks up and processes the extracted Plex info into TVM Management

Usage:
  plex_extract_processing.py [--vl=<vlevel>]
  plex_extract_processing.py -h | --help
  plex_extract_processing.py --version

Options:
  -h --help      Show this screen
  --vl=<vlevel>  Level of verbosity
                 1 = Warnings & Errors Only, 2 = High Level Info,
                 3 = Medium Level Info, 4 = Low Level Info, 5 = All
                 [default: 1]
  --version      Show version

"""

from docopt import docopt
import os
from datetime import date
import time

from Libraries.tvm_db import execute_sql
from Libraries.tvm_apis import execute_tvm_request
from Libraries.tvm_functions import fix_showname


def update_plex_shows(psn, sn, si):
    if si:
        f_sql = f"select * from plex_shows where showid = {si}"
    else:
        f_sql = f"select * from plex_shows where showname = {psn} or showname = '{sn}'"
    recs = execute_sql(sqltype='Fetch', sql=f_sql)
    if len(recs) == 0:
        if vli > 3:
            print(f'{time.strftime("%D %T")} Plex Extract Processing: '
                  f'Insert a new records into Plex Shows for {psn}, {sn}, {si}')
        if si == 0:
            w_sql = f"insert into plex_shows values ({psn}, Null, '{sn}')"
        else:
            w_sql = f"insert into plex_shows values ({psn}, {si}, '{sn}')"
        execute_sql(sqltype='Commit', sql=w_sql.replace("None", "NULL"))


def find_show(ssn):
    s_sql = f"select showid from shows where status = 'Followed' and (showname = '{ssn}' or alt_showname = '{ssn}')"
    records = execute_sql(sqltype='Fetch', sql=s_sql)
    return records


def find_plex_show(psn):
    p_sql = f"select showid from plex_shows where showname = {psn}"
    record = execute_sql(sqltype='Fetch', sql=p_sql)
    return record


def update_tvmaze_episode_status(epiid):
    if vli > 3:
        print(f'Updated TVMaze {epiid}')
    baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(epiid)
    epoch_date = int(date.today().strftime("%s"))
    data = {"marked_at": epoch_date, "type": 0}
    response = execute_tvm_request(baseurl, data=data, req_type='put', code=True)
    return response


def do_update_tvmaze(pid, ps, pe, pw):
    epi_sql = f"select epiid, mystatus from episodes where showid = {pid} and season = {ps} and episode = {pe}"
    epi_info = execute_sql(sqltype='Fetch', sql=epi_sql)
    if len(epi_info) == 0:
        if vli > 2:
            print(f'{time.strftime("%D %T")} Plex Extract Processing: '
                  f'Episode not found show {pid}, season {ps}, episode {pe}')
        return False
    if vli > 3:
        print(f'{time.strftime("%D %T")} Plex Extract Processing: '
              f'Episode {epi_info[0][0]} found for show {pid}, season {ps}, episode {pe} with status {epi_info[0][1]}')
    if epi_info[0][1] == 'Watched':
        return True
    utes = update_tvmaze_episode_status(epi_info[0][0])
    if vli > 3:
        print(f"{time.strftime('%D %T')} Plex Extract Processing: "
              f"Updated TVMaze for show {pid} and {epi_info[0][0]} for {ps}, {pe} on {pw}")
    if not utes:
        return False
    else:
        return True
    
    
def find_plex_episodes(psn, pseason, pepi):
    f_sql = f'select * from plex_episodes ' \
            f'where showname = {psn} and season = {pseason} and episode = {pepi}'
    fpe = execute_sql(sqltype='Fetch', sql=f_sql)
    return fpe
    
    
''' Main Program'''
''' Get Options'''
print()
print(f'{time.strftime("%D %T")} Plex Extract Processing >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Started')
options = docopt(__doc__, version='Plex Extract Release 1.0')
vli = int(options['--vl'])
if vli > 5 or vli < 1:
    print(f"{time.strftime('%D %T')} Plex Extract Processing: "
          f"Unknown Verbosity level of {vli}, try plex_extract.py -h")
    quit()
elif vli > 1:
    print(f'{time.strftime("%D %T")} Plex Extract Processing: Verbosity level is set to: {options["--vl"]}')

'''Get Plex Watched Episodes'''
check = os.getcwd()
if 'Pycharm' in check:
    wetxt = '/Volumes/HD-Data-CA-Server/Development/PycharmProjects/TVM-Management/Data/Plex_Watched_Episodes.txt'
else:
    wetxt = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Data/Plex_Watched_Episodes.txt'

we = ''
try:
    we = open(wetxt, "r")
except IOError as err:
    print(f'{time.strftime("%D %T")} Plex Extract Processing: Error Opening the txt file {err}')
    quit()
ew = 0
for episode in we:
    ew += 1
    episode = str(episode).replace('(', "").replace(')', '')
    epi = str((episode[:-1])).split(',')
    plex_sn = epi[0]
    plex_season = epi[1]
    plex_epi = epi[2]
    plex_watch_date = epi[3]
    if vli > 3:
        print(f'{time.strftime("%D %T")} Plex Extract Processing: '
              f'Trying to find episodes for {plex_sn}, s {plex_season} epi {plex_epi}')
    found_pe = find_plex_episodes(plex_sn, plex_season, plex_epi)
    if len(found_pe) != 0:
        if found_pe[0][4]:
            if vli > 3:
                print(f'{time.strftime("%D %T")} Plex Extract Processing: '
                      f'Already updated before {plex_sn}, {plex_season}, {plex_epi}, {plex_watch_date}')
            continue
    else:
        ipe_sql = f'insert into plex_episodes values ' \
                  f'({plex_sn}, {plex_season}, {plex_epi}, {plex_watch_date}, Null, Null)'
        ipe_sql = ipe_sql.replace('None', 'NULL')
        res = execute_sql(sqltype='Commit', sql=ipe_sql)
        if not res:
            print(f'{time.strftime("%D %T")} Plex Extract Processing: Error with inserting or finding this show '
                  f'{episode} with {res}, skipping to the next one')
            continue
    
    plex_show = find_plex_show(plex_sn)
    if plex_show:
        p_show = plex_show[0][0]
        if vli > 3:
            print(f'{time.strftime("%D %T")} Plex Extract Processing: '
                  f'Found Show in Plex Shows {plex_sn} with id {p_show}')
        result = do_update_tvmaze(p_show, plex_season, plex_epi, plex_watch_date)
        if result:
            if vli > 2:
                print(f'{time.strftime("%D %T")} Plex Extract Processing: '
                      f'Processed {plex_sn}, {plex_season}, {plex_epi}, {plex_watch_date}')
            upe_sql = f'update plex_episodes set tvm_updated = current_date, tvm_update_status = "Watched" ' \
                      f'where showname = {plex_sn} and season = {plex_season} and episode = {plex_epi}'
            execute_sql(sqltype='Commit', sql=upe_sql)
        else:
            print(f'{time.strftime("%D %T")} Plex Extract Processing: '
                  f'Failed to Process {plex_sn}, {plex_season}, {plex_epi}, {plex_watch_date}')
            upe_sql = f'update plex_episodes set tvm_update_status = "Failed Update" ' \
                      f'where showname = {plex_sn} and season = {plex_season} and episode = {plex_epi}'
            execute_sql(sqltype='Commit', sql=upe_sql)
    else:
        fsn = fix_showname(plex_sn)
        found_show = find_show(fsn)
        if not found_show:
            found_show = [(None,)]
        if vli > 3:
            print(f'{time.strftime("%D %T")} Plex Extract Processing: Found showid {found_show[0][0]} for {fsn}')
        update_plex_shows(plex_sn, fsn, found_show[0][0])
        print(f'{time.strftime("%D %T")} Plex Extract Processing: '
              f'Updated Plex Show with new entry {plex_sn}, {fsn}, {found_show[0][0]}')
    
we.close()
if vli > 1:
    print(f'{time.strftime("%D %T")} Plex Extract Processing: Found Plex Episodes {ew} in the extract')
print(f'{time.strftime("%D %T")} Plex Extract Processing >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Ended')

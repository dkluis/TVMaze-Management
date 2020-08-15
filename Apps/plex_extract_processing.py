"""

plex_extract_processing.py   The App that picks up and processes the extracted Plex info into TVM Management

Usage:
  plex_extract_processing.py [--vl=<vlevel>]
  plex_extract_processing.py -h | --help
  plex_extract_processing.py --version

Options:
  -h --help      Show this screen
  --vl=<vlevel>  Level of verbosity
                 1 = Warnings & Errors Only, 2 = High Level Info, 3 = Medium Level Info, 4 = Low Level Info, 5 = All
                 [default: 1]
  --version      Show version

"""

from docopt import docopt
import os
from datetime import date

from db_lib import execute_sql
from tvm_api_lib import execute_tvm_request


def fix_showname(sn):
    sn = sn.replace(" : ", " ").replace("vs.", "vs").replace("'", "").replace(":", '').replace("&", "and")
    sn = sn.replace('"', '')
    if sn[-1:] == " ":
        sn = sn[:-1]
    lsix = sn[-6:]
    if lsix[0] == "(" and lsix[5] == ")":
        sn = sn[:-7]
    lfour = sn[-4:]
    if lfour.lower() == "(us)":
        sn = sn[:-5]
    if lfour.isnumeric():
        sn = sn[:-5]
    ltree = sn[-3:]
    if ltree.lower() == " us":
        sn = sn[:-3]
    return sn


def update_plex_shows(psn, sn, si):
    f_sql = f"select * from plex_shows where showname = {psn}"
    recs = execute_sql(sqltype='Fetch', sql=f_sql)
    if len(recs) == 0:
        if vli > 3:
            print(f'Insert a new records into Plex Shows for {psn}')
        if si == 0:
            w_sql = f"insert into plex_shows values ({psn}, None, '{sn}')"
        else:
            w_sql = f"insert into plex_shows values ({psn}, {si}, '{sn}')"
        execute_sql(sqltype='Commit', sql=w_sql.replace("None", "NULL"))


def find_show(ssn):
    s_sql = f"select showid from shows where showname = '{ssn}' or alt_showname = '{ssn}'"
    records = execute_sql(sqltype='Fetch', sql=s_sql)
    return records


def find_plex_show(psn):
    p_sql = f"select showid from plex_shows where showname = {psn}"
    record = execute_sql(sqltype='Fetch', sql=p_sql)
    return record


def update_tvmaze_episode_status(epiid):
    if vli:
        print("Updating", epiid)
    baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(epiid)
    epoch_date = int(date.today().strftime("%s"))
    data = {"marked_at": epoch_date, "type": 0}
    response = execute_tvm_request(baseurl, data=data, req_type='put', code=True)
    return response


def do_update_tvmaze(pid, ps, pe, pw):
    epi_sql = f"select epiid, mystatus from episodes where showid = {pid} and season = {ps} and episode = {pe}"
    epi_info = execute_sql(sqltype='Fetch', sql=epi_sql)
    if len(epi_info) == 0:
        print(f'Episode not found show {pid}, season {ps}, episode {pe}')
        return False
    if vli > 3:
        print(f'Episode {epi_info[0][0]} found for show {pid}, season {ps}, episode {pe} with status {epi_info[0][1]}')
    if epi_info[0][1] == 'Watched':
        return True
    result = update_tvmaze_episode_status(epi_info[0][0])
    if not result:
        return False
    else:
        return True
    
    
''' Main Program'''
''' Get Options'''
options = docopt(__doc__, version='Plex Extract Release 0.1')
vli = int(options['--vl'])
if vli > 5 or vli < 1:
    print(f"Unknown Verbosity level of {vli}, try plex_extract.py -h")
    quit()
elif vli > 1:
    print(f'Verbosity level is set to: {options["--vl"]}')

'''Get Plex Watched Episodes'''
check = os.getcwd()
if 'Pycharm' in check:
    wetxt = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Data/Plex_Watched_Episodes.txt'
else:
    wetxt = '/Volumes/HD-Media-CA-Media/PlexMedia/PlexProcessing/TVMaze/Data/Plex_Watched_Episodes.txt'

try:
    we = open(wetxt, "r")
except IOError as err:
    print(f'Error Opening the txt file {err}')
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
    plex_show = find_plex_show(plex_sn)
    if plex_show:
        p_show = plex_show[0][0]
        if vli > 3:
            print(f'Found Show in Plex Shows {plex_sn} with id {p_show}')
        result = do_update_tvmaze(p_show, plex_season, plex_epi, plex_watch_date)
        if result:
            if vli > 2:
                print(f'Processed {plex_sn}, {plex_season}, {plex_epi}, {plex_watch_date}')
        else:
            print(f'Failed to Process {plex_sn}, {plex_season}, {plex_epi}, {plex_watch_date}')
    else:
        fsn = fix_showname(plex_sn)
        found_show = find_show(fsn)
        if not found_show:
            found_show = [(None,)]
        if vli > 3:
            print(f'Found showid {found_show[0][0]} for {fsn}')
        update_plex_shows(plex_sn, fsn, found_show[0][0])
        print(f'Updated Plex Show with new entry {plex_sn}, {fsn}, {found_show[0][0]}')
    
we.close()
if vli > 1:
    print(f'Found Plex Episodes {ew} in the extract')

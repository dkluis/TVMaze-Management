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
import sqlite3
import os

from db_lib import execute_sql


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
    fsn = fix_showname(plex_sn)
    found_show = find_show(fsn)
    if not found_show:
        found_show = [(None,)]
    if vli > 3:
        print(f'Found showid {found_show[0][0]} for {fsn}')
    update_plex_shows(plex_sn, fsn, found_show[0][0])
    if vli > 2:
        print(f'Processed {plex_sn}, {fsn}, {plex_season}, {plex_epi}, {plex_watch_date}')
    
we.close()
if vli > 1:
    print(f'Found Plex Episodes {ew} in the extract')

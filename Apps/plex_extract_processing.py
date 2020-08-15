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


class sdb_info:
    check = os.getcwd()
    if 'Pycharm' in check:
        data = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/Plex DB/com.plexapp.plugins.library.db'
    else:
        data = '/Users/dick/Library/Application Support/Plex Media Server/' \
               'Plug-in Support/Databases/com.plexapp.plugins.library.db'


def connect_sdb():
    try:
        sdb = sqlite3.connect(sdb_info.data)
    except sqlite3.Error as err:
        print(f'Error Opening the DB with error {err} on {sdb_info.data}')
        quit()
    scur = sdb.cursor()
    sdict = {'sdb': sdb,
             'scursor': scur}
    return sdict


def close_sdb(sdb):
    sdb.close()


def execute_sqlite(sqltype='', sql=''):
    sdb = connect_sdb()
    sdbcur = sdb['scursor']
    sdbdb = sdb['sdb']
    if sqltype == 'Commit':
        try:
            sdbcur.execute(sql)
            sdbdb.commit()
        except sqlite3.Error as er:
            print('Commit Database Error: ', er, sql)
            print('----------------------------------------------------------------------')
            close_sdb(sdbdb)
            return False, er
        close_sdb(sdbdb)
        return True
    elif sqltype == "Fetch":
        try:
            sdbcur.execute(sql)
            result = sdbcur.fetchall()
        except sqlite3.Error as er:
            print('Execute SQL Database Error: ', er, sql)
            print('----------------------------------------------------------------------')
            close_sdb(sdbdb)
            return False, er
        close_sdb(sdbdb)
        return result
    else:
        return False, 'Not implemented yet'


def fix_showname(sn):
    sn = sn.replace(" : ", " ").replace("vs.", "vs").replace("'", "").replace(":", '').replace("&", "and")
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
if options['-a']:
    if vli > 1:
        print(f'Getting all Plex Watched Episodes')
    sqlw = f"select grandparent_title, parent_index, `index`, viewed_at " \
           f"from metadata_item_views " \
           f"where parent_index > 0 and metadata_type = 4 " \
           f"order by grandparent_title asc, parent_index asc, `index` asc"
else:
    if vli > 1:
        print(f'Getting Plex Watched Episodes since yesterday')
    sqlw = f"select grandparent_title, parent_index, `index`, viewed_at " \
           f"from metadata_item_views " \
           f"where parent_index > 0 and metadata_type = 4 and viewed_at > date('now', '-1 day') " \
           f"order by grandparent_title asc, parent_index asc, `index` asc"

watched_episodes = execute_sqlite(sqltype='Fetch', sql=sqlw)
if not watched_episodes:
    print(f'Reading Plex DB while trying to get the watched episodes {watched_episodes}')
    quit()

check = os.getcwd()
if 'Pycharm' in check:
    wetxt = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Data/Plex_Watched_Episodes.txt'
else:
    wetxt = '/Volumes/HD-Media-CA-Media/PlexMedia/PlexProcessing/TVMaze/Data/Plex_Watched_Episodes.txt'

try:
    we = open(wetxt, "w")
except IOError as err:
    print(f'Error Opening the txt file {err}')
    quit()
ew = 0
for episode in watched_episodes:
    we.write(f'{str(episode)}\n')
    ew += 1
    if vli > 2:
        print(f'Processed {episode}')

we.close()
if vli > 1:
    print(f'Found Plex Episodes {len(watched_episodes)} and written {ew} to file')

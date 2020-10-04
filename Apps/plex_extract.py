"""

plex_extract.py   The App that runs on the Plex Server Machine and extracts the relevant Plex data needed
                  by TVM-Management.  Currently only the episodes that Plex has marked as watched.

Usage:
  plex_extract.py [-a] [--vl=<vlevel>]
  plex_extract.py -h | --help
  plex_extract.py --version

Options:
  -a             Extract all watched episodes from Plex otherwise only the ones since yesterday
  -h --help      Show this screen
  --vl=<vlevel>  Level of verbosity
                 1 = Warnings & Errors Only, 2 = High Level Info, 3 = Medium Level Info, 4 = Low Level Info, 5 = All
                 [default: 1]
  --version      Show version

"""

from docopt import docopt
import sqlite3
import os


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
           f"where parent_index > 0 and metadata_type = 4 and viewed_at > date('now', '-1 day') and account_id = 1 " \
           f"order by grandparent_title asc, parent_index asc, `index` asc"

watched_episodes = execute_sqlite(sqltype='Fetch', sql=sqlw)
if not watched_episodes:
    print(f'Reading Plex DB while trying to get the watched episodes {watched_episodes}')
    quit()
    
check = os.getcwd()
if 'Pycharm' in check:
    wetxt = '/Volumes/HD-Data-CA-Server/Development/PycharmProjects/TVM-Management/Data/Plex_Watched_Episodes.txt'
else:
    # wetxt = '/Volumes/HD-Media-CA-Media/PlexMedia/PlexProcessing/TVMaze/Data/Plex_Watched_Episodes.txt'
    wetxt = '/Volumes/SharedFolders/PlexMedia/PlexProcessing/TVMaze/Data/Plex_Watched_Episodes.txt'

try:
    we = open(wetxt, "w")
except IOError as err:
    print(f'Error Opening the txt file {err}')
    quit()
ew = 0
for episode in watched_episodes:
    f1 = str(episode[0]).replace(',', '')
    f2 = episode[1]
    f3 = episode[2]
    f4 = episode[3]
    watched = (f1, f2, f3, f4)
    print(watched)
    we.write(f'{str(watched).strip()}\n')
    ew += 1
    if vli > 2:
        print(f'Processed {episode}')
        
we.close()
if vli > 1:
    print(f'Found Plex Episodes {len(watched_episodes)} and written {ew} to file')

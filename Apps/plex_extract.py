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

from db_lib import execute_sql


class sdb_info:
    check = os.getcwd()
    if 'Pycharm' in check:
        data = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/Plex DB/com.plexapp.plugins.library.db'
    else:
        data = '/Users/dick/Application Support/Plex Media Server/' \
               'Plug-in Support/Databases/com.plexapp.plugins.library.db'


def connect_sdb():
    sdb = sqlite3.connect(sdb_info.data)
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
    if vli > 2:
        print(f'Getting all Plex Watched Episodes')
    sqlw = f"select grandparent_title, parent_index, `index`, viewed_at " \
          f"from metadata_item_views " \
          f"where parent_index > 0 and metadata_type = 4 " \
          "order by grandparent_title asc, parent_index asc, `index` asc"
else:
    if vli > 2:
        print(f'Getting Plex Watched Episodes since 2020-07-31')
    sqlw = f"select grandparent_title, parent_index, `index`, viewed_at " \
          f"from metadata_item_views " \
          f"where parent_index > 0 and metadata_type = 4 and viewed_at > '2020-07-31' " \
          f"order by grandparent_title asc, parent_index asc, `index` asc"

watched_episodes = execute_sqlite(sqltype='Fetch', sql=sqlw)
if not watched_episodes:
    print(f'Error Reading Plex DB while trying to get the watched episodes {watched_episodes}')
    quit()
if vli > 1:
    print(f'Number of Watched Episodes is: {len(watched_episodes)}')

'''For each extracted episode update TVMaze if necessary'''
last_sn = ''
for episode in watched_episodes:
    sn = fix_showname(str(episode[0]))
    if sn == last_sn and nf_sn:
        continue
    if vli > 3:
        print(f'Original Showname {episode[0]} adjusted Show Name {sn}')
    record = execute_sql(sqltype='Fetch', sql=f'''select showid, showname, status from shows '''
                                              f'''where (LOWER(showname) like "{sn.lower()}%" or '''
                                              f'''LOWER(alt_showname) like "{sn.lower()}%")''')
    if not record:
        if vli > 1:
            print(f'Show not found >>> original Showname {episode[0]} adjusted Show Name {sn}')
        last_sn = sn
        nf_sn = True
        continue
    nf_sn = False
    if record[0][2] != 'Followed':
        if vli > 2:
            print(f'Watched something that is not being followed {record}')
        continue

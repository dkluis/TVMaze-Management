"""

episodes_update.py    The App that update all episodes with the latest tvmaze information

Usage:
  episodes_update.py -f [--vl=<vlevel>]
  episodes_update.py -o [--vl=<vlevel>]
  episodes_update.py -a [--vl=<vlevel]
  episodes_update.py -t <epiid> [--vl=<vlevel]
  episodes_update.py -r <epiid> [--vl=<vlevel]
  episodes_update.py -h | --help
  episodes_update.py --version

Options:
  -h --help             Show this screen
  --vl=<vlevel>         Level of verbosity
                          1 = Warnings & Errors Only, 2 = High Level Info,
                          3 = Medium Level Info, 4 = Low Level Info, 5 = all [default: 5]
  -r                    restart at epiid
  -t                    try updating only epiid
  -a                    all episodes
"""

from docopt import docopt

from Libraries.tvm_apis import *
from Libraries.tvm_db import mariaDB
from Libraries.tvm_logging import logging


def func_get_cli():
    global vli
    global sql
    options = docopt(__doc__, version='Update episodes Release 2.0')
    vli = int(options['--vl'])
    if vli > 5 or vli < 0:
        log.write(f"Unknown Verbosity level of {vli}, try plex_extract.py -h", 0)
        quit()
    elif vli > 1:
        log.write(f'Verbosity level is set to: {options["--vl"]}', 2)
    if options['-a']:
        sql = 'select epiid, showid from episodes'
    elif options['-t']:
        sql = f'select epiid, showid from episodes where showid = {options["<epiid>"]}'
    elif options['-r']:
        sql = f'select showid, showname from episodes where showid >= {options["<epiid>"]}'
    else:
        log.write(f"{time.strftime('%D %T')} episodes: No known - parameter given, try episodes_update.py -h", 0)
        quit()


def func_get_the_episodes():
    episodes = db.execute_sql(sqltype='Fetch', sql=sql)
    return episodes


def func_get_tvmaze_show_info(epiid):
    epiinfo = execute_tvm_request(f'http://api.tvmaze.com/episodes/{epiid}', timeout=(20, 10), return_err=True)
    if not epiinfo:
        log.write(f'Error with API call {epiinfo}', 0)
        return
    if 'Error Code:' in epiinfo:
        log.write(f'This episode gives an error: {epiid} {showid}')
        if "404" in epiinfo:
            log.write(f'Now Deleting: {showid}')
            sql_tvm = f'delete from episodes where `showid` = {showid}'
            result = db.execute_sql(sqltype='Commit', sql=sql_tvm)
            log.write(f'Delete result: {result}')
        return
    
    showinfo = showinfo.json()
    sql_episodes = f"update episodes " \
                f"set episodestatus = '{showinfo['status']}', " \
                f"premiered = '{showinfo['premiered']}', " \
                f"language = '{showinfo['language']}', " \
                f"thetvdb = '{showinfo['externals']['thetvdb']}', " \
                f"imdb = '{showinfo['externals']['imdb']}' " \
                f"where `showid` = {showid}"
    sql_episodes = sql_episodes.replace("'None'", 'NULL').replace('None', 'NULL')
    result = db.execute_sql(sqltype='Commit', sql=sql_episodes)
    if not result:
        log.write(f'Error when updating show {showid} {result}', 0)


def func_update_episodes(episodes):
    if not episodes:
        if vli > 0:
            log.write(f'Something wrong with getting the episodes to update {episodes}', 0)
    elif len(episodes) == 0 and vli > 1:
        log.write(f'No episodes found in the DB', 2)
    else:
        for show in episodes:
            func_update_the_show(show[0], show[1])


def func_update_the_show(showid, showname):
    if vli > 2:
        log.write(f'Updating show {showid}, {showname}', 3)
    func_get_tvmaze_show_info(showid)


def main():
    func_get_cli()
    func_update_episodes(func_get_the_episodes())


if __name__ == '__main__':
    vli = 0
    episodes_to_update = []
    db = mariaDB()
    sql = ''
    log = logging(caller='episodes Update', filename='episodesUpdate')
    log.start()
    
    main()
    
    db.close()
    log.end()

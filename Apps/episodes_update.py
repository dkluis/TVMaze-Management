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
  -h --help             episode this screen
  --vl=<vlevel>         Level of verbosity
                          1 = Warnings & Errors Only, 2 = High Level Info,
                          3 = Medium Level Info, 4 = Low Level Info, 5 = all [default: 5]
  -r                    restart at epiid
  -t                    try updating only epiid
  -a                    all episodes
"""

from docopt import docopt

from Libraries import execute_tvm_request, mariaDB, logging, tvmaze_apis


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
        sql = 'select epiid from episodes order by epiid desc'
    elif options['-t']:
        sql = f'select epiid from episodes where epiid = {options["<epiid>"]}'
    elif options['-r']:
        sql = f'select epiid from episodes where epiid <= {options["<epiid>"]} order by epiid desc'
    else:
        log.write(f"No known - parameter given, try episodes_update.py -h", 0)
        quit()


def func_get_the_episodes():
    episodes = db.execute_sql(sqltype='Fetch', sql=sql)
    return episodes


def func_get_tvmaze_episode_info(epiid):
    epiinfo = execute_tvm_request(f'{tvmaze_apis.episode_info}{epiid}',
                                  timeout=(20, 10), return_err=True, log_file='Episodes_Update')
    if not epiinfo:
        log.write(f'Error with API call {epiinfo}', 0)
        return
    if 'Error Code:' in epiinfo:
        log.write(f'This episode gives an error: {epiid}')
        if "404" in epiinfo:
            log.write(f'Now Deleting: {epiid}')
            sql_tvm = f'delete from episodes where `epiid` = {epiid}'
            result = db.execute_sql(sqltype='Commit', sql=sql_tvm)
            log.write(f'Delete result: {result}')
        return
    
    epiinfo = epiinfo.json()
    if epiinfo['airdate'] == '':
        airdate = None
    else:
        airdate = epiinfo['airdate']
    name = str(epiinfo['name']).replace('"', "").replace("'", "")
    sql_episodes = f"update episodes " \
                   f"set epiname = '{name}', " \
                   f"airdate = '{airdate}', " \
                   f"url = '{epiinfo['url']}', " \
                   f"season = '{epiinfo['season']}', " \
                   f"episode = '{epiinfo['number']}' " \
                   f"where `epiid` = {epiid}"
    sql_episodes = sql_episodes.replace("'None'", 'NULL').replace('None', 'NULL')
    result = db.execute_sql(sqltype='Commit', sql=sql_episodes)
    if not result:
        log.write(f'Error when updating episode {epiid} {result}', 0)


def func_update_episodes(episodes):
    if not episodes:
        if vli > 0:
            log.write(f'Something wrong with getting the episodes to update {episodes}', 0)
    elif len(episodes) == 0 and vli > 1:
        log.write(f'No episodes found in the DB', 2)
    else:
        for episode in episodes:
            func_update_the_episode(episode[0])


def func_update_the_episode(epiid):
    if vli > 2:
        log.write(f'Updating episode {epiid}', 3)
    func_get_tvmaze_episode_info(epiid)


def main():
    func_get_cli()
    func_update_episodes(func_get_the_episodes())


if __name__ == '__main__':
    vli = 0
    episodes_to_update = []
    sql = ''
    log = logging(caller='Episodes Update', filename='Episodes_Update')
    log.start()
    db = mariaDB(caller=log.caller, filename=log.filename, vli=vli)
    
    main()
    
    log.end()

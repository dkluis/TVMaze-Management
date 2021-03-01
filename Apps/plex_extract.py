"""

plex_extract.py   The App that runs on the Plex Server Machine and extracts the relevant Plex data needed
                  by TVM-Management.  Currently only the episodes that Plex has marked as watched.

Usage:
  plex_extract.py -a [--vl=<vlevel>]
  plex_extract.py -p [-w] [--vl=<vlevel>]
  plex_extract.py -h | --help
  plex_extract.py --version

Options:
  -a             Extract all watched episodes from Plex otherwise only the ones since yesterday,
  -w             Write the Plex_Watched_Episodes.txt file to the Data directory
  -p             Update the TVM DB directly
  -h --help      Show this screen
  --vl=<vlevel>  Level of verbosity
                 1 = Warnings & Errors Only, 2 = High Level Info, 3 = Medium Level Info, 4 = Low Level Info, 5 = All
                 [default: 1]
  --version      Show version

"""

from docopt import docopt
from datetime import date

from Libraries import execute_sqlite, mariaDB, config, execute_tvm_request, fix_showname, logging, \
     tvmaze_apis, check_vli


class sdb_info:
    data = '/Users/dick/Library/Application Support/Plex Media Server/Plug-in Support/Databases' \
           '/com.plexapp.plugins.library.db'


class log_file:
    def __init__(self):
        config_info = config()
        wetxt = f'{config_info.log}Plex_Watched_Episodes.log'
        try:
            self.we = open(wetxt, "w")
        except IOError as error:
            log.write(f'Error Opening the txt file {error}', 0)
            db.close()
            quit()
    
    def save(self, info):
        self.we.write(info)
    
    def end(self):
        self.we.close()


def func_get_plex_watched_episodes():
    if process_all:
        if vli > 1:
            log.write(f'Getting all Plex Watched Episodes', 2)
        sqlw = f"select grandparent_title, parent_index, `index`, viewed_at " \
               f"from metadata_item_views " \
               f"where parent_index > 0 and metadata_type = 4 and account_id = 1 " \
               f"order by grandparent_title, parent_index, `index`"
    else:
        if vli > 1:
            log.write(f'Getting Plex Watched Episodes since yesterday', 2)
        sqlw = f"select grandparent_title, parent_index, `index`, viewed_at " \
               f"from metadata_item_views " \
               f"where parent_index > 0 and metadata_type = 4 and viewed_at > date('now', '-1 day') " \
               f"and account_id = 1 " \
               f"order by grandparent_title, parent_index, `index`"
    
    episodes = execute_sqlite(sqltype='Fetch', sql=sqlw)
    log.write(f'Found {len(episodes)} episodes to process')
    return episodes


def func_find_episode(showid, season, episode):
    sql = f'select showid, epiname, airdate, mystatus_date, mystatus, epiid from episodes ' \
          f'where showid = {showid} and season = {season} and episode = {episode}'
    result = db.execute_sql(sqltype='Fetch', sql=sql)
    return result


def func_narrow_down_showids(showids, season, episode):
    valid_shows = []
    for rec in showids:
        showid = rec[0]
        result = func_find_episode(showid, season, episode)
        if result:
            valid_shows.append(result)
    if len(valid_shows) == 0:
        return []
    found_shows_with_epis = []
    for show in valid_shows:
        if show[0][4] == 'Downloaded' or show[0][4] is None:
            found_shows_with_epis.append(show[0][0])
    return found_shows_with_epis


def func_update_episode_and_tvm(epi_showid, epi_season, epi_episode, epi_watched_date, fixed_showname):
    epi_to_update = func_find_episode(epi_showid, epi_season, epi_episode)
    if not epi_to_update:
        return False
    if epi_to_update[0][4] == 'Watched':
        if vli > 3:
            log.write(f'Episode Already Watched before "{fixed_showname}"'
                      f' {epi_season}, {epi_episode} with name {epi_to_update[0][1]}', 4)
        return False
    result = update_tvmaze_episode_status(epiid=epi_to_update[0][5], upd_date=epi_to_update[0][3])
    if not result:
        log.write(f'Update did not work on TVM with {epi_showid}, {epi_season}, {epi_episode}, {epi_watched_date}, '
                  f'{fixed_showname}', 0)
        return False
    log.write(f'Updated TVM with {epi_showid}, {epi_season}, {epi_episode}, {epi_watched_date}, {fixed_showname}')
    return True


def update_tvmaze_episode_status(epiid, upd_date):
    if vli > 1:
        log.write(f'Update TVM Episode Status: {epiid}, {upd_date}', 2)
    baseurl = tvmaze_apis.get_episodes_status + '/' + str(epiid)
    if upd_date:
        epoch_date = int(upd_date.strftime("%s"))
    else:
        epoch_date = int(date.today().strftime("%s"))
    data = {"marked_at": epoch_date, "type": 0}
    response = execute_tvm_request(baseurl, data=data, req_type='put', code=True, log_ind=do_log)
    return response


def func_update_plex(episodes):
    no_updates = 0
    for episode in episodes:
        epi_showname = episode[0]
        epi_season = episode[1]
        epi_episode = episode[2]
        epi_watched_date = episode[3]
        fixed_showname = fix_showname(epi_showname)
        sql = f'select showid from shows ' \
              f'where (showname = "{fixed_showname}" or alt_showname = "{fixed_showname}") ' \
              f'and status = "Followed"'
        result = db.execute_sql(sqltype='Fetch', sql=sql)
        if not result:
            if vli > 3:
                log.write(f'Watched Showid not Found for "{fixed_showname}" {episode}', 4)
            continue
        if len(result) > 1:
            log.write(f'More than 1 Showid Found for "{fixed_showname}" {episode} with result {result}', 2)
            found_sh = func_narrow_down_showids(result, epi_season, epi_episode)
            if not found_sh or len(found_sh) > 1:
                log.write(f'Could not determine the right show "{fixed_showname}" {episode}')
                found_show = []
            else:
                found_show = found_sh[0]
        else:
            found_show = result[0][0]
        if not found_show:
            continue
        success = func_update_episode_and_tvm(found_show, epi_season, epi_episode, epi_watched_date, fixed_showname)
        if success:
            no_updates += 1
    
    return no_updates


def func_write_the_log_file(episodes):
    ew = 0
    lf = log_file()
    for episode in episodes:
        f1 = str(episode[0]).replace(',', '')
        f2 = episode[1]
        f3 = episode[2]
        f4 = episode[3]
        watched = (f1, f2, f3, f4)
        lf.save(f'{str(watched).strip()}\n')
        ew += 1
        if vli > 2:
            log.write(f'Processed {episode}', 3)
    lf.end()
    return ew


''' Main Program'''
''' Get Options'''
log = logging(caller='Plex Extract', filename='Process')
log.start()

options = docopt(__doc__, version='Plex Extract Release 0.1')
vli = check_vli(options, log)
if vli > 2:
    do_log = True
else:
    do_log = False
    
db = mariaDB(caller=log.caller, filename=log.filename, vli=vli)
    
process_all = False
write_watched = True
update_plex = False

if options['-a']:
    process_all = True
    write_watched = True
if options['-w']:
    write_watched = True
if options['-p']:
    update_plex = True
    if not options['-w']:
        write_watched = False

'''Get Plex Watched Episodes'''
watched_episodes = func_get_plex_watched_episodes()
if not watched_episodes:
    log.write(f'Reading Plex DB while trying to get the watched episodes {watched_episodes}', 0)
    db.close()
    quit()

'''Process the watched episodes'''
written = 0
updated = 0
if write_watched:
    written = func_write_the_log_file(watched_episodes)
if update_plex or process_all:
    updated = func_update_plex(watched_episodes)

'''End of Program'''
if vli > 1:
    log.write(f'Updated Plex Episodes {updated} and written {written} to the log', 2)

db.close()
log.end()
quit()

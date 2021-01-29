"""

plex_tvm_update.py The App that handles all transmission generated files (or directories) by processing the
                transmission log and archiving it.  And updating TVMaze that the show or movie has been acquired.

Usage:
  plex_tvm_update.py    [--vl=<vlevel>] [<to_process>]
  plex_tvm_update.py    -h | --help
  plex_tvm_update.py    --version

Options:
  <to_process>   The transmission download to process.  If not provided the program will read the transmission log as
                   the input for what media files acquired to process.
  -h --help      Show this screen
  --vl=<vlevel>  Level of verbosity
                   1 = Warnings & Errors Only, 2 = High Level Info,
                   3 = Medium Level Info, 4 = Low Level Info, 5 = All [default: 1]
  --version      Show version.

"""

import os
import shutil
import time

from docopt import docopt

from Libraries import config
from Libraries import execute_sql
from Libraries import logging
from Libraries import process_download_name, update_tvmaze_episode_status


def gather_all_key_info():
    px_extensions = execute_sql(sqltype='Fetch', sql='SELECT info FROM key_values where `key` = "plexexts"')[0][0]
    px_extensions = str(px_extensions).split(',')
    px_prefs = execute_sql(sqltype='Fetch', sql='SELECT info FROM key_values where `key` = "plexprefs"')[0][0]
    px_prefs = str(px_prefs).split(',')
    px_source_dir = execute_sql(sqltype='Fetch', sql='SELECT info FROM key_values where `key` = "plexsd"')[0][0]
    px_movie_dir = execute_sql(sqltype='Fetch', sql='SELECT info FROM key_values where `key` = "plexmovd"')[0][0]
    px_show_dir = execute_sql(sqltype='Fetch', sql='SELECT info FROM key_values where `key` = "plextvd1"')[0][0]
    px_kids_show_dir = execute_sql(sqltype='Fetch', sql='SELECT info FROM key_values where `key` = "plextvd2"')[0][0]
    px_kids_shows = execute_sql(sqltype='Fetch', sql='SELECT info FROM key_values where `key` = "plextvd2selections"')
    px_kids_shows = str(px_kids_shows[0][0]).split(',')
    px_do_not_move = execute_sql(sqltype='Fetch', sql='SELECT info FROM key_values where `key` = "plexdonotmove"')
    px_do_not_move = str(px_do_not_move[0][0]).split(',')
    px_processed_dir = execute_sql(sqltype='Fetch', sql='SELECT info FROM key_values where `key` = "plexprocessed"')
    px_processed_dir = str(px_processed_dir[0][0]).split(',')[0]
    px_trash_dir = execute_sql(sqltype='Fetch', sql='SELECT info FROM key_values where `key` = "plextrash"')
    px_trash_dir = str(px_trash_dir[0][0]).split(',')[0]
    return px_extensions, px_prefs, px_source_dir, px_movie_dir, px_show_dir, px_kids_show_dir, px_kids_shows, \
        px_do_not_move, px_processed_dir, px_trash_dir


def get_all_tors_to_update():
    tors = []
    try:
        transmissions_in = open(transmission_log, 'r')
    except IOError as er:
        log.write(f'Transmission file did not exist: {er}')
        return tors
    
    try:
        transmissions_archive = open(transmission_archive_log, 'a+')
    except IOError as er:
        log.write(f'Transmission archive would not open with error {er}')
        exit(1)
    
    for tor in transmissions_in:
        if 'Transmission Started' in tor:
            continue
        if len(tor) < 5:
            continue
        transmissions_archive.write(f'{time.strftime("%D %T")} > {tor}')
        tors.append(tor[:-1])
    transmissions_in.close()
    try:
        transmissions_in = open(transmission_log, 'w')
    except IOError as er:
        log.write(f'Transmission file did not exist: {er}')
        return tors
    transmissions_in.close()
    transmissions_archive.close()
    return tors


def check_exist(file_dir):
    check = str(plex_source_dir + file_dir).lower()
    if vli > 3:
        log.write(f'Check File and Directory for: {check}', 4)
    ch_path = os.path.exists(check)
    ch_isdir = os.path.isdir(check)
    return ch_path, ch_isdir


def transform_season_string(season_in):
    if isinstance(season_in, int):
        return season_in
    if 'season' in str(season_in).lower():
        return int(str(season_in).lower().split('season')[1].replace(' ', ''))
    if 's' in str(season_in).lower():
        return int(str(season_in).lower().split('s')[1].replace(' ', ''))
    log.write(f'Should not happen {season_in}', 99)


def update_tvmaze_with_downloaded_episodes(epis):
    for epi in epis:
        update_tvmaze_episode_status(epi, log, vli)
    return


def check_for_kids(showname):
    for kids_show in plex_kids_shows:
        if kids_show in showname:
            return plex_kids_show_dir
    return plex_show_dir


def move_to_plex(tv_show, file_name, direct, name, season):
    if vli > 3:
        log.write(f'Moving to plex {file_name} and it is a directory: {direct} and it is tv-show: {tv_show}', 4)
    if tv_show:
        to_directory = f'{check_for_kids(name)}{name}/Season {season}/'
    else:
        to_directory = plex_movie_dir

    if not os.path.exists(to_directory):
        try:
            os.makedirs(to_directory)
        except IOError as er:
            log.write(f'Creating Directory {to_directory} did not work {er}')
            quit(1)

    if not direct:
        shutil.move(f'{plex_source_dir}{file_name}', f'{to_directory}{file_name}')
        if vli > 1:
            log.write(f'Moved {file_name} to {to_directory}', 2)
    else:
        all_files = os.listdir(f'{plex_source_dir}/{file_name}')
        for file in all_files:
            for ext in plex_extensions:
                if ext == file[-3:]:
                    shutil.move(f'{plex_source_dir}/{file_name}/{file}', f'{to_directory}')
                    if vli > 1:
                        log.write(f'Moved {file} to {to_directory}', 2)
                    break
        if os.path.exists(f'{plex_source_dir}/{file_name}'):
            shutil.move(f'{plex_source_dir}/{file_name}', f'{plex_trash_dir}')
    return


'''
Main Program start
'''
log = logging(caller='Plex TVM Update', filename='Process')
log.start()

options = docopt(__doc__, version='Plex TVM Update Release 1.0')
vli = int(options['--vl'])
if vli > 5 or vli < 1:
    log.write(f"{time.strftime('%D %T')} Plex TVM Update: Unknown Verbosity level of {vli}, try plex_extract.py -h", 0)
    quit()
elif vli >= 1:
    log.write(f'Verbosity level is set to: {options["--vl"]}', 2)
    
config_info = config()
transmission_log = config_info.log + 'Transmission.log'
transmission_archive_log = config_info.log + 'Transmissions_Processed.log'

if options['<to_process>']:
    downloads = [options['<to_process>']]
    cli = True
else:
    cli = False
    downloads = get_all_tors_to_update()

if len(downloads) == 0:
    log.write(f'Nothing to Process in the transmission log')
    log.end()
    quit()

if vli > 1:
    log.write(f'Number of Downloads: {len(downloads)}', 2)

if not cli:
    reset = open(transmission_log, 'w')
    reset.close()

key_info = gather_all_key_info()
plex_extensions = key_info[0]
plex_prefs = key_info[1]
plex_source_dir = key_info[2]
plex_movie_dir = key_info[3]
plex_show_dir = key_info[4]
plex_kids_show_dir = key_info[5]
plex_kids_shows = key_info[6]
plex_do_not_move = key_info[7]
plex_processed_dir = key_info[8]
plex_trash_dir = key_info[9]

for download in downloads:
    seas = 0
    full_tor_name = download
    check_result = check_exist(full_tor_name)
    if not check_result[0]:
        log.write(f'Download does not exist: {full_tor_name}', 9)
        log.end()
        quit(1)
        
    directory = check_result[1]
    processed_info = process_download_name(full_tor_name)
    seas = processed_info['season']
    if processed_info['is_tvshow']:
        all_episodes = []
        if not processed_info['whole_season']:
            all_episodes.append(processed_info['episodeid'])
        else:
            sql = f'select epiid from episodes where showid = {processed_info["showid"]} and ' \
                  f'season = {seas}'
            episodes = execute_sql(sql=sql, sqltype='Fetch')
            if len(episodes) != 0:
                for episode in episodes:
                    all_episodes.append(episode[0])
        log.write(f'Processing TV Show {processed_info["real_showname"]} with {len(all_episodes)} episodes')
        move_to_plex(True, full_tor_name, directory, processed_info['real_showname'], seas)
        update_tvmaze_with_downloaded_episodes(all_episodes)
    else:
        log.write(f'Processing Movie {full_tor_name}')
        move_to_plex(False, full_tor_name, directory, '', '')
        log.write(f'Processing Movie {full_tor_name}')
    
log.end()
quit()

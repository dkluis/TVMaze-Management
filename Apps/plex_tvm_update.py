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

from time import strftime
from docopt import docopt

from Libraries import execute_tvm_request, read_secrets
from Libraries import execute_sql
from Libraries import fix_showname
from Libraries import logging, date
from Libraries import determine_directory, process_download_name


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
        log.write(f'Transmission archive would not open')
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


def update_tvmaze_episode_status(epiid):
    status_sql = f'select epiid, mystatus from episodes where epiid = {epiid}'
    result = execute_sql(sql=status_sql, sqltype='Fetch')[0]
    if result[1] == 'Downloaded' or result[1] == 'Watched':
        log.write(f'This episode {epiid} has already been update with "{result[1]}"')
        return
    if vli > 2:
        log.write(f"Updating TVMaze for: {epiid}", 3)
    baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(epiid)
    epoch_date = int(date.today().strftime("%s"))
    data = {"marked_at": epoch_date, "type": 1}
    execute_tvm_request(baseurl, data=data, req_type='put', code=True, log=True)
    return


def check_exist(file_dir):
    check = str(plex_source_dir + file_dir).lower()
    if vli > 3:
        log.write(f'Check File Dir with {check}')
    ch_path = os.path.exists(check)
    ch_isdir = os.path.isdir(check)
    return ch_path, ch_isdir


def check_file_ext(file):
    if vli > 3:
        log.write(f'Check File Ext {file}')
    for ext in plex_extensions:
        if vli > 3:
            log.write(f'Check File Ext: {ext} with {file[-3:]}')
        if file[-3:] == ext:
            return True
    return False


def check_destination(sn, m):
    if m:
        dd = plex_movie_dir
    else:
        dd = plex_show_dir
        for ps in plex_kids_shows:
            if vli > 3:
                log.write(f'ps = {ps} and sn = {sn}')
            if ps.lower() in sn[0].lower():
                dd = plex_kids_show_dir
                break
    return dd


def check_file_ignore(fi):
    if vli > 3:
        log.write(f'Starting to check {fi} type {type(fi)}with all of {plex_do_not_move}, '
                  f'type {type(plex_do_not_move)}')
    for ign in plex_do_not_move:
        if vli > 3:
            log.write(f'Checking for {ign}, type {type(ign)}')
        if ign in str(fi.lower()):
            return True
    return False


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
        update_tvmaze_episode_status(epi)
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
        to_directory = f'{check_for_kids(name)}{name}/season {season}/'
    else:
        to_directory = plex_movie_dir

    if not direct:
        shutil.move(f'{plex_source_dir}{file_name}', f'{to_directory}{file_name}')
    # else:
    #    loop through the file in directory and check for media extensions
    #    delete the directory after all media files have moved
    
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
    
secrets = read_secrets()
transmission_log = secrets['prod_logs'] + 'Transmission.log'
transmission_archive_log = secrets['prod_logs'] + 'Transmissions_Processed.log'

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

'''
def old_for_loop():
    edl = []  # Shows / Movies
    fedl = []  # Files
    ndl = []  #
    if vli > 2:
        log.write(f'Processing download {dl}', 3)
    dl_check = check_exist(dl)
    dl_exist = dl_check[0]
    dl_dir = ''
    if dl_exist:
        dl_dir = dl_check[1]
    if not dl_exist:
        log.write(f'Transmission input "{plex_source_dir + dl}" does not exist ')
        continue
    else:
        if vli > 2:
            log.write(f'Transmission input "{plex_source_dir + dl}" exist and directory is {dl_dir}', 3)
        dl = plex_source_dir + dl
        edl.append(dl)
        if not dl_dir:
            file_to_process = check_file_ext(dl)
            if file_to_process:
                fedl.append(dl)
            else:
                log.write(f'No File found with the right extension {dl}:  {plex_extensions}')
        else:
            if vli > 2:
                log.write(f'Do the directory process and find all files', 3)
            dirfiles = os.listdir(dl)
            if vli > 2:
                log.write(f'All files to process {dirfiles}', 3)
            for df in dirfiles:
                dfn = dl + '/' + df
                dfe = check_file_ext(dfn)
                if vli > 3:
                    log.write(f'Checked {dfn} and result is {dfe}', 4)
                if dfe:
                    ignore = check_file_ignore(df)
                    if not ignore:
                        fedl.append(df)
        if vli > 3:
            log.write(f'Working on edl {edl}, with fedl {fedl}', 4)
        if len(fedl) == 0:
            log.write(f'Found no video files to move for {dl}')
            if os.path.exists(dl):
                t = strftime(" %Y-%m-%d-%I-%M-%S")
                log.write(f'Moving to Trash {dl}')
                try:
                    shutil.move(dl, f'{plex_trash_dir}/{dl + t}')
                except OSError as err:
                    log.write(f'Deleted directly instead {dl}')
                    shutil.rmtree(d)
            continue
        else:
            d = str(dl).replace(' ', '.')
            dc = cleanup_name(d)
            if vli > 3:
                log.write(f'Cleaned Name "{dc}"')
            ds_tmp = find_showname(dc)
            ds = shorten_showname(ds_tmp)
            if vli > 3:
                log.write(f'Find Showname output: {ds}', 4)
            if not ds[0]:
                movie = True
                fn = str(d).split('/')
                fn = fn[len(fn) - 1]
                du = plex_movie_dir + fn
            else:
                movie = False
                de = find_showid(ds[0])
                if vli > 3:
                    log.write(f'Showid is {de}', 4)
                dest_dir = check_destination(ds, movie)
                du = dest_dir + str(ds[0]).title() + '/Season ' + str(ds[2]) + '/'
            for f in edl:
                skip = False
                if vli > 3:
                    log.write(f'Processing F: {f}', 4)
                for e in fedl:
                    if vli > 4:
                        log.write(f'Processing E: {e}', 4)
                    if not dl_dir:
                        sf = f
                    else:
                        sf = f + '/' + e
                    if movie:
                        if "season" in str(sf).lower():
                            log.write(f'This might not be a movie it has the string "season" embedded --> {sf}')
                            skip = True
                        elif "part" in str(sf).lower():
                            log.write(f'This might not be a movie it has the string "part" embedded --> {sf}')
                            skip = True
                        if dl_dir:
                            if vli > 3:
                                log.write(f'Movie with Directory working on du {du} and e {e} and f {f}')
                            fn = str(e).split('/')
                            fn = fn[len(fn) - 1]
                            to = plex_movie_dir + fn
                        else:
                            fn = str(d).split('/')
                            fn = fn[len(fn) - 1]
                            to = plex_movie_dir + fn
                        if not skip:
                            if vli > 1:
                                log.write(f'Move the movie to ------> {to}', 2)
                            os.rename(rf'{f}', rf'{to}')
                        if dl_dir:
                            chd = dl
                        else:
                            chd = False
                    else:
                        fn = str(e).split('/')
                        fn = fn[len(fn) - 1]
                        if not os.path.exists(du):
                            if vli > 2:
                                log.write(f'Creating directory {du}', 3)
                            os.makedirs(du)
                        to = du + fn
                        # ToDo - clean the suffixes of the filename via the key_values
                        to = str(to).replace('[eztv.re]', '').replace('[eztv.io]', '')
                        if vli > 1:
                            log.write(f'Move the episode to ------> {to}', 2)
                        os.rename(rf'{sf}', rf'{to}')
                        chd = d
            if not chd:
                pass
            elif os.path.exists(chd):
                if skip:
                    if vli > 2:
                        log.write(f'Moved {d} to {plex_processed_dir}', 3)
                    shutil.move(d, plex_processed_dir)
                else:
                    t = strftime(" %Y-%m-%d-%I-%M-%S")
                    if vli > 2:
                        log.write(f'Moved to Trash {d + t}', 3)
                    try:
                        shutil.move(d, f'{plex_trash_dir}/{d + t}')
                    except OSError as err:
                        log.write(f'Deleted directly instead {d}')
                        os.removedirs(d)
            if not movie:
                if vli > 2:
                    log.write(f'Starting the process to Update TVMaze download statuses for show {d}', 3)
                update_tvmaze(ds, de)

log.end()
quit()
'''

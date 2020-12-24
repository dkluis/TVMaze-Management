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


def get_all_episodes_to_update():
    ttps = []
    try:
        transmissions_in = open(transmission_log, 'r')
    except IOError as er:
        log.write(f'Transmission file did not exist: {er}')
        return ttps
    
    try:
        transmissions_archive = open(transmission_archive_log, 'a+')
    except IOError as er:
        log.write(f'Transmission archive would not open')
        exit(1)
    
    for ttp in transmissions_in:
        if 'Transmission Started' in ttp:
            continue
        if len(ttp) < 5:
            continue
        transmissions_archive.write(f'{time.strftime("%D %T")} > {ttp}')
        ttps.append(ttp[:-1])
    
    transmissions_in.close()
    try:
        transmissions_in = open(transmission_log, 'w')
    except IOError as er:
        log.write(f'Transmission file did not exist: {er}')
        return ttps
    transmissions_in.close()
    transmissions_archive.close()
    return ttps


def find_showname(download):
    showinfo = str(download).split(".")
    showname = ""
    seasonfound = False
    seasonstr = ""
    dots = "first"
    for info in showinfo:
        # log.write(info[0], info[1], type(info[1]))
        if len(info) < 2:
            if dots == "first":
                # log.write('First', info)
                showname = showname + " " + info
                dots = "second"
            else:
                showname = showname + "." + info
        else:
            if dots == "second":
                showname = showname + "."
                dots = "done"
            if "s" in info[0].lower() and info[1].isdigit():
                seasonfound = True
                seasonstr = info
            if seasonfound:
                break
            else:
                showname = showname + " " + info
    
    if not seasonfound:
        return False, showinfo
    showname = str(showname[1:]).replace('..', '.')
    season = seasonstr.lower().split('e')
    seasonnum = int(season[0].lower().replace("s", ""))
    if "e" in seasonstr.lower():
        episodestr = True
        episodenum = int(str(season[1]).lower().replace('e', ''))
    else:
        episodenum = None
        episodestr = False
    return showname, seasonstr, seasonnum, episodestr, episodenum


def find_showid(asn):
    if vli > 3:
        log.write(f'Find Show ID via alt_showname: {asn}')
    result = execute_sql(sqltype='Fetch', sql=f"SELECT showid FROM shows "
                                              f"WHERE alt_showname like '{asn}' AND status = 'Followed'")
    if len(result) < 1:
        if vli > 3:
            log.write(f"{time.strftime('%D %T')} Plex TVM Update: Show not found: ---> ", "'" + asn + "'")
        if str(asn[len(asn) - 4:]).isnumeric():
            result = execute_sql(sqltype='Fetch', sql=f"SELECT showid FROM shows "
                                                      f"WHERE alt_showname like '{asn[:-5]}' AND status = 'Followed'")
            if len(result) < 1:
                if vli > 3:
                    log.write(f"{time.strftime('%D %T')} Plex TVM Update: "
                              f"Show without last 4 characters not found: ---> ", "'" + asn[:-5] + "'")
                pass
            else:
                if vli > 3:
                    log.write(f"{time.strftime('%D %T')} Plex TVM Update: "
                              f"Show without last 4 characters found: ---> ", "'" + asn[:-5] + "'")
                return result[0][0]
        return False
    return result[0][0]


def find_epiid(si, s, e, is_epi):
    if is_epi and e == 0:
        result = execute_sql(sqltype='Fetch', sql=f'SELECT * FROM episodes '
                                                  f'WHERE showid = {si} AND season = {s} AND episode is NULL')
    elif is_epi:
        result = execute_sql(sqltype='Fetch', sql=f'SELECT * FROM episodes '
                                                  f'WHERE showid = {si} AND season = {s} AND episode = {e}')
    else:
        result = execute_sql(sqltype='Fetch', sql=f'SELECT * FROM  episodes '
                                                  f'WHERE showid = {si} AND season = {s}')
    if len(result) < 1:
        return False
    else:
        if result[0][7] == 'Watched':
            if is_epi:
                if vli > 3:
                    log.write(f''
                              f'Episodes of {si} for season {s} were watched before')
            else:
                if vli > 3:
                    log.write(f''
                              f'Episode of {si} for season {s} and episode {2} was watched before')
            return False
    return result


def update_tvmaze_episode_status(epiid):
    if vli > 2:
        log.write(f"{time.strftime('%D %T')} Plex TVM Update: Updating", epiid)
    baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(epiid)
    epoch_date = int(date.today().strftime("%s"))
    data = {"marked_at": epoch_date, "type": 1}
    response = execute_tvm_request(baseurl, data=data, req_type='put', code=True, log=True)
    return response


def check_exist(file_dir):
    check = str(plex_source_dir + file_dir).lower()
    if vli > 3:
        log.write(f'Check File Dir with {check}')
    ch_path = os.path.exists(check)
    ch_isdir = os.path.isdir(check)
    # log.write(f'Check Exist: {ch_path}, {ch_isdir}')
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


def cleanup_name(dl):
    sf = str(dl).split('/')
    fn = sf[len(sf) - 1]
    for plex_pref in plex_prefs:
        plex_pref = plex_pref.lower()
        fn = fn.lower()
        if plex_pref in fn:
            fn = str(fn).replace(plex_pref, "").replace(' ', '.')
            return fn
    return fn


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


def update_tvmaze(showinfo, found_showid):
    if vli > 1:
        log.write(f''
                  f'Starting to update TVMaze episodes for {showinfo} with Show ID {found_showid}')
    showname = showinfo[0]
    showepisode = showinfo[1]
    season = showinfo[2]
    is_episode = showinfo[3]
    episode = showinfo[4]
    if found_showid:
        found_epiid = find_epiid(found_showid, season, episode, is_episode)
        if not found_epiid:
            log.write(f"{time.strftime('%D %T')} Plex TVM Update: "
                      f"Did not find '{str(showname).title()}' with episode {showepisode} in TVMaze")
        elif is_episode and len(found_epiid) == 1:
            update_tvmaze_episode_status(found_epiid[0][0])
            log.write(f"{time.strftime('%D %T')} Plex TVM Update: Updated Show {str(showname).title()}, "
                      f"episode {showepisode} as download in TVMaze")
        else:
            for epi in found_epiid:
                update_tvmaze_episode_status(epi[0])
                log.write(f"{time.strftime('%D %T')} Plex TVM Update: "
                          f"Updated TVMaze as download for {epi[2]}, Season {epi[4]}, Episode {epi[5]}")


def shorten_showname(info):
    """
    ShowNames can include suffix with years and country codes, they should not be used when creating
    directories for plex.

    :param info:   contains tuple:  Showname, season-episode, etc, etc) only the Showname is needed
    :return:       same tuple:      With the Showname shortened
    """
    shortened_showname = fix_showname(info[0])
    if not shortened_showname:
        shortened_showname = info[0]
    result = (shortened_showname, info[1], info[2], info[3], info[4])
    return result


'''
Main Program start
'''
log = logging(caller='Plex TVM Update', filename='Process')
log.open()
log.close()
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
    download = [options['<to_process>']]
    cli = True
else:
    cli = False
    download = get_all_episodes_to_update()

if len(download) == 0:
    log.write(f'Nothing to Process in the transmission log')
    log.end()
    quit()

if vli > 4:
    log.write(f'Download = {download}', 5)

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

for dl in download:
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

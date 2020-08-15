
"""

transmission.py The App that handles all transmission generated files (or directories) by processing the
                transmission log and archiving it.  And updatign TVMaze that the show or movie has been acquired.

Usage:
  transmission.py [--vl=<vlevel>] [<to_process>]
  transmission.py -h | --help
  transmission.py --version

Options:
  -h --help      Show this screen
  --vl=<vlevel>  Level of verbosity (a = All, i = Informational, w = Warnings only) [default: w]
  --version      Show version.

"""

from db_lib import execute_sql
from tvm_api_lib import execute_tvm_request
import os
import shutil

from datetime import date
from time import strftime
from docopt import docopt


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
    return px_extensions, px_prefs, px_source_dir, px_movie_dir, px_show_dir, px_kids_show_dir, \
           px_kids_shows, px_do_not_move, px_processed_dir, px_trash_dir


def get_all_episodes_to_update():
    ttps = []
    try:
        transmissions = open('/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/Transmission.log')
    except IOError as er:
        if vli:
            print(f'Transmission file did not exist: {er}')
        return ttps
    
    for ttp in transmissions:
        if 'Transmission Started' in ttp:
            continue
        if len(ttp) < 5:
            continue
        ttps.append(ttp[:-1])
    return ttps


def find_showname(download):
    showinfo = str(download).split(".")
    showname = ""
    seasonfound = False
    seasonstr = ""
    dots = "first"
    for info in showinfo:
        # print(info[0], info[1], type(info[1]))
        if len(info) < 2:
            if dots == "first":
                # print('First', info)
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
    if vli:
        print(f'Find Show ID via alt_showname: {asn}')
    result = execute_sql(sqltype='Fetch', sql=f"SELECT showid FROM shows "
                                              f"WHERE alt_showname like '{asn}' AND status = 'Followed'")
    if len(result) < 1:
        if vli:
            print("Show not found: ---> ", "'" + asn + "'")
        if str(asn[len(asn) - 4:]).isnumeric():
            result = execute_sql(sqltype='Fetch', sql=f"SELECT showid FROM shows "
                                                      f"WHERE alt_showname like '{asn[:-5]}' AND status = 'Followed'")
            if len(result) < 1:
                if vli:
                    print("Show without last 4 characters not found: ---> ", "'" + asn[:-5] + "'")
                pass
            else:
                if vli:
                    print("Show without last 4 characters found: ---> ", "'" + asn[:-5] + "'")
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
                print(f'Episodes of {si} for season {s} were watched before')
            else:
                print(f'Episode of {si} for season {s} and episode {2} was watched before')      
            return False
    return result


def update_tvmaze_episode_status(epiid):
    if vli:
        print("Updating", epiid)
    baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(epiid)
    epoch_date = int(date.today().strftime("%s"))
    data = {"marked_at": epoch_date, "type": 1}
    response = execute_tvm_request(baseurl, data=data, req_type='put', code=True)
    return response


def check_exist(file_dir):
    check = str(plex_source_dir + file_dir).lower()
    if vli:
        print(f'Check File Dir with {check}')
    ch_path = os.path.exists(check)
    ch_isdir = os.path.isdir(check)
    # print(f'Check Exist: {ch_path}, {ch_isdir}')
    return ch_path, ch_isdir


def check_file_ext(file):
    if vli:
        print(f'Check File Ext {file}')
    for ext in plex_extensions:
        if vli:
            print(f'Check File Ext: {ext} with {file[-3:]}')
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
            if vli:
                print(f'ps = {ps} and sn = {sn}')
            if ps.lower() in sn[0].lower():
                dd = plex_kids_show_dir
                break
    return dd


def check_file_ignore(fi):
    if vli:
        print(f'Starting to check {fi} type {type(fi)}with all of {plex_do_not_move}, type {type(plex_do_not_move)}')
    for ign in plex_do_not_move:
        if vli:
            print(f'Checking for {ign}, type {type(ign)}')
        if ign in str(fi.lower()):
            return True
    return False


def update_tvmaze(showinfo, found_showid):
    print(f'Starting to update TVMaze episodes for {showinfo} with Show ID {found_showid}')
    showname = showinfo[0]
    showepisode = showinfo[1]
    season = showinfo[2]
    is_episode = showinfo[3]
    episode = showinfo[4]
    if found_showid:
        found_epiid = find_epiid(found_showid, season, episode, is_episode)
        if not found_epiid:
            print(f"Did not find '{str(showname).title()}' with episode {showepisode} in TVMaze")
        elif is_episode and len(found_epiid) == 1:
            update_tvmaze_episode_status(found_epiid[0][0])
            print(f"Updated Show '{str(showname).title()}', episode {showepisode} as downloaded in TVMaze")
        else:
            for epi in found_epiid:
                update_tvmaze_episode_status(epi[0])
                print(f"Updated TVMaze as downloaded for {epi[2]}, Season {epi[4]}, Episode {epi[5]}")


'''
Main Program start
'''

options = docopt(__doc__, version='Transmission Release 0.9.5')
vli = False
vlw = True
if options['--vl'].lower() == 'a':
    vli = True
elif options['--vl'].lower() == 'i':
    vli = True
if vli:
    print(f'verbosity levels Informational {vli} and Warnings {vlw}')
    print(options)
if options['<to_process>']:
    download = [options['<to_process>']]
    cli = True
else:
    cli = False
    download = get_all_episodes_to_update()
    
if len(download) == 0:
    print(f'Nothing to Process in the transmission log')
    quit()

if vli:
    print(f'Download = {download}')

if not cli:
    t = strftime("%Y-%m-%d-%I-%M-%S ")
    os.replace(r'/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/Transmission.log',
               rf'/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/Archived/{t}Transmission.log')

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
    if vli:
        print(f'Processing download {dl}')
    dl_check = check_exist(dl)
    dl_exist = dl_check[0]
    if dl_exist:
        dl_dir = dl_check[1]
    if not dl_exist:
        print(f'Transmission input "{plex_source_dir + dl}" does not exist ')
        continue
    else:
        if vli:
            print(f'Transmission input "{plex_source_dir + dl}" exist and directory is {dl_dir} ')
        dl = plex_source_dir + dl
        edl.append(dl)
        if not dl_dir:
            file_to_process = check_file_ext(dl)
            if file_to_process:
                fedl.append(dl)
            else:
                print(f'No File found with the right extension {dl}:  {plex_extensions}')
        else:
            if vli:
                print(f'Do the directory process and find all files')
            dirfiles = os.listdir(dl)
            if vli:
                print(f'All files to process {dirfiles}')
            for df in dirfiles:
                dfn = dl + '/' + df
                dfe = check_file_ext(dfn)
                if vli:
                    print(f'Checked {dfn} and result is {dfe}')
                if dfe:
                    ignore = check_file_ignore(df)
                    if not ignore:
                        fedl.append(df)
        if vli:
            print(f'Working on edl {edl} \n, with fedl {fedl}')
        if len(fedl) == 0:
            print(f'Found no video files to move for {dl}')
            if os.path.exists(dl):
                t = strftime(" %Y-%m-%d-%I-%M-%S")
                print(f'Moving to Trash {dl}')
                try:
                    shutil.move(dl, f'{plex_trash_dir}/{dl + t}')
                except OSError as err:
                    print(f'Deleted directly instead {dl}')
                    shutil.rm(d)
            continue
        else:
            d = str(dl).replace(' ', '.')
            dc = cleanup_name(d)
            if vli:
                print(f'Cleaned Name "{dc}"')
            ds = find_showname(dc)
            if vli:
                print(f'Find Showname output: {ds}')
            if not ds[0]:
                movie = True
                fn = str(d).split('/')
                fn = fn[len(fn) - 1]
                du = plex_movie_dir + fn
            else:
                movie = False
                de = find_showid(ds[0])
                if vli:
                    print(f'Showid is {de}')
                dest_dir = check_destination(ds, movie)
                du = dest_dir + str(ds[0]).title() + '/Season ' + str(ds[2]) + '/'
            for f in edl:
                skip = False
                if vli:
                    print(f'Processing F: {f}')
                for e in fedl:
                    if vli:
                        print(f'Processing E: {e}')
                    if not dl_dir:
                        sf = f
                    else:
                        sf = f + '/' + e
                    if movie:
                        if "season" in str(sf).lower():
                            print(f'This might not be a movie it has the string "season" embedded --> {sf}')
                            skip = True
                        elif "part" in str(sf).lower():
                            print(f'This might not be a movie it has the string "part" embedded --> {sf}')
                            skip = True
                        if dl_dir:
                            if vli:
                                print(f'Movie with Directory working on du {du} and e {e} and f {f}')
                            fn = str(e).split('/')
                            fn = fn[len(fn) - 1]
                            to = plex_movie_dir + fn
                        else:
                            fn = str(d).split('/')
                            fn = fn[len(fn) - 1]
                            to = plex_movie_dir + fn
                        if not skip:
                            print(f'Move the movie {f} to ------> {to}')
                            os.rename(rf'{f}', rf'{to}')
                        if dl_dir:
                            chd = dl
                        else:
                            chd = False
                    else:
                        fn = str(e).split('/')
                        fn = fn[len(fn) - 1]
                        if not os.path.exists(du):
                            print(f'Creating directory {du}')
                            os.makedirs(du)
                        to = du + fn
                        print(f'Move the episode {sf} to ------> {to}')
                        os.rename(rf'{sf}', rf'{to}')
                        chd = d
            if not chd:
                pass
            elif os.path.exists(chd):
                if skip:
                    print(f'Moved {d} to {plex_processed_dir}')
                    shutil.move(d, plex_processed_dir)
                else:
                    t = strftime(" %Y-%m-%d-%I-%M-%S")
                    print(f'Moved to Trash {d + t}')
                    try:
                        shutil.move(d, f'{plex_trash_dir}/{d + t}')
                    except OSError as err:
                        print(f'Deleted directly instead {d}')
                        shutil.rmtree(d)
            if not movie:
                print(f'Starting the process to Update TVMaze download statuses for show {d}')
                update_tvmaze(ds, de)

quit()

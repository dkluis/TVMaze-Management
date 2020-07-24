from db_lib import execute_sql
from tvm_api_lib import execute_tvm_request
import os

import sys
from datetime import date
from time import strftime


def get_all_episodes_to_update():
    ttps = []
    try:
        transmissions = open('/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/Transmission.log')
    except IOError as err:
        # print(f'Transmission file did not exist: {err}')
        return ttps
    
    for ttp in transmissions:
        if ' Swift ' in ttp:
            continue
        if len(ttp) < 5:
            continue
        ttps.append(ttp[:-1])
    return ttps


def get_cli_args():
    clis = sys.argv
    if len(clis) < 2:
        # print('No download info provided in the command line')
        return False
    return clis[1]


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
    showname = showname[1:]
    season = seasonstr.lower().split('e')
    seasonnum = int(season[0].lower().replace("s", ""))
    if "e" in seasonstr.lower():
        episodestr = True
        episodenum = str(season[1]).lower().replace('e', '')
    else:
        episodenum = None
        episodestr = False
    return showname, seasonstr, seasonnum, episodestr, episodenum


def find_showid(asn):
    # print(f'Find Show ID via alt_showname: {asn}')
    result = execute_sql(sqltype='Fetch', sql=f"SELECT showid FROM shows "
                                              f"WHERE alt_showname like '{asn}' AND status = 'Followed'")
    if len(result) < 1:
        print("Show not found: ---> ", "'" + showname + "'")
        if str(showname[len(showname) - 4:]).isnumeric():
            result = execute_sql(sqltype='Fetch', sql=f"SELECT showid FROM shows "
                                                      f"WHERE alt_showname like '{asn[:-5]}' AND status = 'Followed'")
            if len(result) < 1:
                print("Show without last 4 characters not found: ---> ", "'" + showname[:-5] + "'")
            else:
                print("Show without last 4 characters found: ---> ", "'" + showname[:-5] + "'")
                return result[0][0]
        return False
    return result[0][0]


def find_epiid(si, s, e, i_s):
    if i_s:
        result = execute_sql(sqltype='Fetch', sql=f'SELECT * FROM  episodes '
                                                  f'WHERE showid = {si} AND season = {s} AND episode = {e}')
        if len(result) < 1:
            # print("Episode not found: ---> ", "'" + showname + "'")
            return False
        else:
            # ToDo figure out if this episode has been watched before
            if result[0][7] == 'Watched':
                print(f'Episode of {si} for season {s} and episde {e} was watched before')
                return False
    else:
        result = execute_sql(sqltype='Fetch', sql=f'SELECT * FROM  episodes '
                                                  f'WHERE showid = {si} AND season = {s}')
        if len(result) < 1:
            # print("Episode not found: ---> ", "'" + showname + "'")
            if result[0][7] == 'Watched':
                print(f'Episodes of {si} for season {s} were watched before')
                return False
            return False
    return result


def update_tvmaze_episode_status(epiid):
    # print("Updating", epiid)
    baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(epiid)
    epoch_date = int(date.today().strftime("%s"))
    data = {"marked_at": epoch_date, "type": 1}
    response = execute_tvm_request(baseurl, data=data, req_type='put', code=True)
    return response


'''
Main Program start
'''
# print(f'Main Program started')
download = get_cli_args()
cli = True
if not download:
    # print(f'Now processing the transmission log')
    cli = False
    download = get_all_episodes_to_update()
    if len(download) == 0:
        print(f'Nothing to Process in the transmission log')
        quit()


plexprefs = execute_sql(sqltype='Fetch', sql="SELECT info FROM key_values WHERE `key` = 'plexprefs'")
plexprefs = str(plexprefs[0]).split(',')

ndl = []

if cli:
    ndl.append(download)
else:
    for dl in download:
        for plexpref in plexprefs:
            plexpref = plexpref.lower()
            dl = dl.lower()
            if plexpref in dl:
                ndl.append(str(dl).replace(plexpref, "").replace(' ', '.'))
                break
            else:
                continue
        ndl.append(str(dl).replace(' ', '.'))
        
    if len(ndl) == 0:
        print(f'Nothing to process: NDL = {ndl} and downloads are: {download}')

for dl in ndl:
    showinfo = find_showname(dl)
    # print(f'Processing Showinfo {showinfo}')
    if not showinfo[0]:
        print(f"This is likely a movie {dl}")
    else:
        showname = showinfo[0]
        showepisode = showinfo[1]
        season = showinfo[2]
        is_episode = showinfo[3]
        episode = showinfo[4]
        
        # print("Looking for:", showname, season, episode, is_episode)
        found_showid = find_showid(showname)
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
                    print(f"Updated TVMaze as downloaded for {epi[2]}, Season {epi[5]}, Episode {epi[6]}")
                    
if not cli:
    t = strftime("%U-%a-at-%X")
    os.replace(r'/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/Transmission.log',
               rf'/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/Archived/Transmission - {t}.log')

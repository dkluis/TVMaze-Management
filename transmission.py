from db_lib import *
from tvm_api_lib import *

import sys
import time
from datetime import date


def get_cli_args():
    clis = sys.argv
    if len(clis) < 2:
        print('Need to get the download input')
        quit()
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
    result = execute_sql(sqltype='Fetch', sql=f"SELECT showid FROM shows "
                                              f"WHERE alt_showname like '{asn}' AND status = 'Followed'")
    if len(result) < 1:
        # print("Show not found: ---> ", "'" + showname + "'")
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
        result = execute_sql(sqltype='Fetch', sql=f'SELECT * FROM  episodes '
                                                  f'WHERE showid = {si} AND season = {s}')
        if len(result) < 1:
            # print("Episode not found: ---> ", "'" + showname + "'")
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
# print("Start TVM Episode Update")
download = get_cli_args()
# print(f'Download {download}')
showinfo = find_showname(download)
print(f'Showinfo {showinfo}')
if not showinfo[0]:
    print(f"This is likely a movie {download}")
    quit()

showname = showinfo[0]
showepisode = showinfo[1]
season = showinfo[2]
is_episode = showinfo[3]
episode = showinfo[4]

# print("Looking for:", showname, season, episode, is_episode)
found_showid = find_showid(showname)
if not found_showid:
    print(f"Did not find {showname} in TVMaze", showname)
else:
    found_epiid = find_epiid(found_showid, season, episode, is_episode)
    if not found_epiid:
        print(f"Did not find {showname} with episode {showepisode} in TVMaze")
    elif is_episode and len(found_epiid) == 1:
        update_tvmaze_episode_status(found_epiid[0][0])
        print(f"Updated Show {showname}, episode {showepisode} as downloaded in TVMaze")
    else:
        for epi in found_epiid:
            update_tvmaze_episode_status(epi[0])
            print(f"Updated TVMaze as downloaded for {epi[2]}, Season {epi[5]}, Episode {epi[6]}")


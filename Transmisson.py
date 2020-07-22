import sqlite3
import sys
import time
from datetime import date

import requests

tvm_db = sqlite3.connect("data/TVMAZE.db")
tvm_cur = tvm_db.cursor()


def get_cli_args():
    clis = sys.argv
    showinfo = str(clis[1]).split(".")
    # print(clis[1], dl_info)
    showname = ""
    seasonfound = False
    seasonstr = ""
    dots = "first"
    for info in showinfo:
        # print(info[0], info[1], type(info[1]))
        if len(info) < 2:
            if dots == "first":
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
    try:
        tvm_cur.execute("SELECT showid FROM alt_showname "
                        "WHERE torrent_showname = ? COLLATE NOCASE AND followed = 'Followed'", (asn,))
        result = tvm_cur.fetchall()
        if len(result) < 1:
            # print("Show not found: ---> ", "'" + showname + "'")
            return False
    except sqlite3.IntegrityError as er:
        print("Error: ", er)
        return False
    except sqlite3.Error as er:
        print("Tried to read(showid): ", er)
        return False
    return result[0][0]


def find_epiid(si, s, e, i_s):
    if i_s:
        try:
            tvm_cur.execute('SELECT * FROM  eps_by_show '
                            'WHERE showid = ? AND '
                            'season = ? AND '
                            'episode = ?', (si, s, e,))
            result = tvm_cur.fetchall()
            if len(result) < 1:
                # print("Episode not found: ---> ", "'" + showname + "'")
                return False
        except sqlite3.IntegrityError as er:
            print("Error: ", er)
            return False
        except sqlite3.Error as er:
            print("Tried to read: ", er)
            return False
    else:
        try:
            tvm_cur.execute('SELECT * FROM  eps_by_show '
                            'WHERE showid = ? AND '
                            'season = ?', (si, s,))
            result = tvm_cur.fetchall()
            if len(result) < 1:
                # print("Episode not found: ---> ", "'" + showname + "'")
                return False
        except sqlite3.IntegrityError as er:
            print("Error: ", er)
            return False
        except sqlite3.Error as er:
            print("Tried to read: ", er)
            return False
    return result


def update_tvmaze_episode_status(epiid):
    # print("Updating", epiid)
    baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(epiid)
    headers = {'Authorization': 'Basic RGlja0tsdWlzOlRUSFlfQ2hIeUF5SU1fV1ZZRmUwcDhrWTkxTkE1WUNH'}
    epoch_date = int(date.today().strftime("%s"))
    data = {"marked_at": epoch_date, "type": 1}
    time.sleep(1)
    response = requests.put(baseurl, headers=headers, data=data)
    if response.status_code != 200:
        print("Error: ", response)
        quit()
    return


'''
Main Program start
'''
# print("Start TVM Episode Update")
showinfo = get_cli_args()
# print(dl_info)
showname = showinfo[0]
showepisode = showinfo[1]
season = showinfo[2]
is_episode = showinfo[3]
episode = showinfo[4]
# print("Looking for:", showname, season, episode, is_episode)
found_showid = find_showid(showname)
if not found_showid:
    print("Did not find the Show in TVMaze", showname)
else:
    found_epiid = find_epiid(found_showid, season, episode, is_episode)
    if not found_epiid:
        print("Did not find the episode in TVMaze", showname, showepisode)
    elif is_episode and len(found_epiid) == 1:
        update_tvmaze_episode_status(found_epiid[0][0])
        print("Updated TVMaze: ", showname, "--->", showepisode)
    else:
        for epi in found_epiid:
            update_tvmaze_episode_status(epi[0])
            print("Updated TVMaze:", epi[2], "Season:", epi[5], "Episode:", epi[6])

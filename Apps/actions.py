import os
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup as Soup
import re

from terminal_lib import check_cli_args, term_codes
from db_lib import *
from tvm_lib import def_downloader, date_delta
from tvm_api_lib import *


def get_cli_args():
    tlc = ["-h", "-b", "-d", "-r"]
    flc = check_cli_args(tlc)
    if flc['-h']:
        print("CLI Options are: -h (Help), -r (Review new shows), -d (Download episodes or -b (Both")
        quit()
    elif flc['-b']:
        return "Both"
    elif flc['-d']:
        return 'Download'
    elif flc['-r']:
        return 'Review'
    return 'Both'


def update_show_status(showid, status):
    if status == "Skipped":
        dl = None
    elif status == "Followed":
        dl = def_downloader.dl
    elif status == 'Undecided':
        d = datetime.today() + timedelta(days=14)
        dl = str(d)[:10]
    else:
        status == "SHIT)(^%"
        dl = "SHIT)(^%"
        quit("SHIT)(^%")
    if not dl:
        sql = f'UPDATE shows SET status = "{status}", download = NULL WHERE `showid` = {showid}'
    else:
        sql = f'UPDATE shows SET status = "{status}", download = "{dl}" WHERE `showid` = {showid}'
    result = execute_sql(sqltype='Commit', sql=sql)
    if not result:
        print(f'Error updating show status {result}')
    return


def update_tvmaze_followed_shows(showid):
    api = 'https://api.tvmaze.com/v1/user/follows/shows/' + str(showid)
    response = execute_tvm_request(api=api, code=True, req_type='put')
    return


def update_tvmaze_episode_status(epiid):
    api = tvm_apis.update_episode_status + str(epiid)
    headers = {'Authorization': 'Basic RGlja0tsdWlzOlRUSFlfQ2hIeUF5SU1fV1ZZRmUwcDhrWTkxTkE1WUNH'}
    epoch_date = int(date.today().strftime("%s"))
    data = {"marked_at": epoch_date, "type": 1}
    response = requests.put(api, headers=headers, data=data)
    if response.status_code != 200:
        print(f"Update TVMaze Episode Status: Error: {response} for episode: {api}")
        return False
    return True


def validate_requirements(filename, container, showname):
    res1 = '1080p'
    res2 = '720p'
    res3 = '480p'
    codex = '264'
    cont1 = "mkv"
    cont2 = "mp4"
    priority = 1
    if res1 in filename:
        priority = priority + 40
    elif res2 in filename:
        priority = priority + 30
    elif res3 in filename:
        priority += 20
    else:
        priority = priority - 40
    if codex in filename:
        priority = priority + 100
    if container and cont1 in filename:
        priority = priority + 10
    elif container and cont2 in filename:
        priority = priority + 5
    if 'proper' or 'repack' in filename:
        priority = priority + 10
    if showname:
        if showname.lower() not in filename.replace('.', ' ')[:len(showname)].lower():
            priority = 0
        else:
            if 's' not in filename.replace('.', ' ').lower()[len(showname) + 1]:
                # print(f'Validate Requirement: Filename character to compare is '
                #       f'{filename.replace(".", " ").lower()[len(showname) + 1]} '
                #       f'with Showname {showname} and Filename {filename}')
                priority = 0
    # print(f'Validate Requirement - Showname: {showname}, Priority: {priority}, Filename: {filename}')
    return priority


def eztv_download(imdb_id, eztv_epi_name):
    eztv_show = imdb_id
    eztv_url = execute_sql(sqltype='Fetch',
                           sql='SELECT link_prefix FROM download_options where `providername` = "eztvAPI"')[0][0] \
               + eztv_show
    # eztv_url = 'https://eztv.io/api/get-torrents?imdb_id=' + str(eztv_show)
    time.sleep(1)
    eztv_data = requests.get(eztv_url).json()
    eztv_count = eztv_data['torrents_count']
    if eztv_count == 0:
        return False, eztv_url
    eztv_epis = eztv_data['torrents']
    download_options = []
    for eztv_epi in eztv_epis:
        filename = str(eztv_epi['filename']).lower()
        tor_url = eztv_epi['torrent_url']
        mag_url = eztv_epi['magnet_url']
        size = eztv_epi['size_bytes']
        if eztv_epi_name in filename:
            result = validate_requirements(filename, True, False)
            if result > 100:
                download_options.append((result, size, filename, tor_url, mag_url))
    if len(download_options) > 0:
        download_options.sort(reverse=True)
        for do in download_options:
            command_str = 'open -a transmission ' + do[4]
            os.system(command_str)
            break
        return True, eztv_url
    else:
        return False, eztv_url


def rarbg_api_download(show, seas):
    dl_info = execute_sql(sqltype='Fetch', sql=f'SELECT * from download_options WHERE `providername` = "rarbgAPI"')[0]
    main_link = f"{dl_info[1]}{show} {seas}{dl_info[2]}"
    main_request = execute_tvm_request(api=main_link, req_type='get').json()
    if 'No results found' in str(main_request):
        return False, main_link
    records = main_request['torrent_results']
    dl_options = []
    for record in records:
        name = record['title']
        magnet = record['download']
        seeders = record['seeders']
        size = record['size']
        prio = validate_requirements(name, True, show)
        if prio > 100:
            dl_options.append((prio, size, seeders, name, magnet))
    if len(dl_options) > 0:
        dl_options.sort(reverse=True)
        for dlo in dl_options:
            print(f'First in sort is: {dlo[3]}')
            command_str = 'open -a transmission ' + dlo[4]
            os.system(command_str)
            return True, main_link
    else:
        return False, main_link


def piratebay_download(show, seas):
    api = 'https://piratebay.bid/s/?q=' + str(show).replace(' ', '+') + '+' + seas
    piratebay_data = execute_tvm_request(api=api, timeout=(20, 20))
    if not piratebay_data:
        return False, api
    piratebay_page = Soup(piratebay_data.content, 'html.parser')
    piratebay_table = piratebay_page.findAll('table', {'id': 'searchResult'})
    # print(f'Piratebay Download: piratebay_table {piratebay_table}')
    if len(piratebay_table) == 0:
        print("No table found")
        return False, api
    piratebay_table = piratebay_table[0]
    pb_table = piratebay_table.findAll('tr')
    piratebay_titles = []
    magnet_link = ''
    size = 0
    for pb_table_rec in pb_table:
        # print(f'Piratebay Download: pb_table_rec: {pb_table_rec}')
        cl_dl = pb_table_rec.findAll('a', {'class': 'detLink'})
        showname = ''
        showl = ''
        shownamel = ''
        shownamenp = ''
        for cl_dl_rec in cl_dl:
            # print(f'Piratebay Download: cl-dl_rec: {cl_dl_rec}')
            showname = (cl_dl_rec['title'])
            showl = show.lower().replace(" ", ".")
            shownamel = showname.lower()
            shownamenp = shownamel.replace('+', '.')
            # print(f'Piratebay Download: showl ---> {showl}, shownamel ---> {shownamel}, shownamenp --> {shownamenp}')
        if showl.replace('.', ' ') in shownamel or showl in shownamenp:
            show_refs = pb_table_rec.findAll('a', {'href': re.compile("^magnet:")})
            for ref in show_refs:
                # print(f'Piratebay Download: ref: {ref}')
                magnet_link = str(ref['href']).split("&dn")
                # print(f'Piratebay Download: magnet_link: {magnet_link}')
                magnet_link = magnet_link[0]
                # print(f'Piratebay Download: magnet_link[0]: {magnet_link}')
                infos = pb_table_rec.findAll('font', {'class': 'detDesc'})
                for info in infos:
                    sub_info = str(info).split('<font class="detDesc">')
                    sub_info = sub_info[1].split(', ULed by')
                    sub_info = sub_info[0].replace('Uploaded ', '').replace(' Size ', '')
                    sub_info = sub_info.split(',')
                    # e1 = sub_info[0]
                    size = str(sub_info[1]).replace('\xa0', '')
                    if 'MiB' in size:
                        size = str(size).split('MiB')
                        size_multiplier = 1
                    elif 'GiB' in size:
                        size = str(size).split('GiB')
                        size_multiplier = 1000
                    else:
                        size_multiplier = 0
                    size = float(size[0]) * size_multiplier
                    size = str(size).zfill(8)
        showname = showname.replace('Details for ', '')
        prio = validate_requirements(showname, False, show)
        if prio > 100:
            piratebay_titles.append((showname, magnet_link, size, prio))
    piratebay_titles.sort(key=lambda x: str(x[3]), reverse=True)
    # print(f'Piratebay Download: Titles: {piratebay_titles}')
    if len(piratebay_titles) > 0:
        command_str = 'open -a transmission ' + piratebay_titles[0][1]
        os.system(command_str)
        return True, api
    else:
        return False, api


def magnetdl_download(show, seas):
    main_link_pre = '''http://www.magnetdl.com/search/?m=1&q="'''
    main_link_suf = '"'
    main_link = main_link_pre + show.replace(' ', '+') + '+' + seas + main_link_suf
    main_request = execute_tvm_request(api=main_link, req_type='get')
    print(main_link, main_request)
    if not main_request:
        return False, main_link
    titles = main_request['torrent_results']
    dl_options = []
    for title in titles:
        name = title['title']
        magnet = title['download']
        seeders = title['seeders']
        size = title['size']
        prio = validate_requirements(name, False, show)
        if prio > 100:
            dl_options.append((prio, size, seeders, name, magnet))
    if len(dl_options) > 0:
        dl_options.sort(reverse=True)
        for do in dl_options:
            command_str = 'open -a transmission ' + do[4]
            os.system(command_str)
            return True, main_link
    else:
        return False, main_link


def get_episodes_to_download():
    todownload = execute_sql(sqltype='Fetch', sql=tvm_views.eps_to_download)
    if not todownload:
        print(f'No episodes to download {todownload}')
    return todownload


def get_downloadAPIs():
    results = execute_sql(sqltype='Fetch', sql="SELECT * from download_options")
    if not results:
        print(f'Error getting the download_options {results}')
    return results


def get_shows_to_review():
    showstoreview = execute_sql(sqltype='Fetch', sql=tvm_views.shows_to_review)
    return showstoreview


def find_dl_info(dl, dlapis):
    for find_dl in dlapis:
        if find_dl[0] == dl:
            return find_dl
    return False


def process_new_shows():
    newshows = get_shows_to_review()
    print("TVM_Action_List ---> Processing New Shows to Review:", len(newshows))
    # Process all the new shows to review
    if not newshows:
        return
    print(f'\033[1m', "                                                                       "
                      "                                                  Shows To Evaluate", f'\033[0m')
    request = "[s,S,u,D,f,F]"
    print("{: <1} {: <50} {: <80} {: <12} {: <16} "
          "{: <12} {: <15} {: <12} {: <24} {: <16} {: <1}".format(f'\033[1m',
                                                                  'Show Name:', 'TVMaze Link:', 'Type:', 'Show Status:',
                                                                  'Premiered:',
                                                                  'Language:', 'Length:', 'Network:', 'Country:',
                                                                  "Option:",
                                                                  f'\033[0m'))
    if len(newshows) != 0:
        for newshow in newshows:
            if not newshow[5]:
                premiered = " "
            else:
                premiered = newshow[5]
            if not newshow[6]:
                language = " "
            else:
                language = newshow[6]
            if not newshow[7]:
                length = " "
            else:
                length = newshow[7]
            if not newshow[8]:
                network = "Unknown"
            else:
                network = newshow[8]
            if not newshow[9]:
                country = "Unknown"
            else:
                country = newshow[9]
            print("{: <1} "
                  "{: <50} {: <80} {: <12} {: <16} {: <12} "
                  "{: <15} {: <12} {: <24} {: <15} {: <1} {: <6}  "
                  "{: <1}".format(
                f'\033[0m',
                newshow[1], newshow[2], newshow[3], newshow[4], premiered,
                language, length, network, country, f'\033[1m', request,
                f'\033[0m'), end=":")
            command_str = 'open -a safari ' + newshow[2]
            os.system(command_str)
            ans = input(" ").lower()
            if ans == "s":
                answer = "Skipped"
            elif ans == "u":
                answer = "Undecided"
            elif ans == "f":
                answer = "Followed"
                update_tvmaze_followed_shows(newshow[0])
            else:
                continue
            update_show_status(newshow[0], answer)
    print()


def do_season_process(epi_tdl):
    if epi_tdl[4] is None:
        s = '0'
    else:
        s = str(epi_tdl[4])
    if epi_tdl[5] is None:
        e = '0'
    else:
        e = str(epi_tdl[5])
    season = "S" + str(s).zfill(2)
    episode = "S" + str(s).zfill(2) + "E" + str(e).zfill(2)
    if e == '1':
        whole_season = True
    else:
        whole_season = False
    return season, episode, whole_season


def format_download_call(epi_tdl, sore):
    downloader = find_dl_info(epi_tdl[10], downloadAPIs)
    showname = str(epi_tdl[11]).replace(" ", downloader[3])
    if downloader[2]:
        link = downloader[1] + showname + downloader[3] + sore + downloader[2]
    else:
        link = downloader[1] + showname + downloader[3] + sore
    return link, downloader[0]


def do_api_process(epi_tdl, req):
    formatted_call = format_download_call(epi_tdl, req)
    if formatted_call[1] == 'rarbgAPI':
        result = rarbg_api_download(epi_tdl[11], req)
    elif formatted_call[1] == 'eztvAPI':
        result = eztv_download(epi_tdl[12], req)
    elif formatted_call[1] == 'magnetdl_new':
        result = magnetdl_download(epi_tdl[11], req)
    elif formatted_call[1] == 'piratebay':
        result = piratebay_download(epi_tdl[11], req)
    else:
        result = False, 'No Link Yet'
    return result, formatted_call


def display_status(processed, epi_to_download, do_text, season):
    if processed[1][1] not in ('eztvAPI', 'rarbgAPI', 'piratebay'):
        do_text = f' ---> Show managed by {processed[1][1]}'
    else:
        do_text = do_text + f" ---> {processed[1][1]}"
    tvmaze = "https://www.tvmaze.com/shows/" + str(epi_to_download[1]) + do_text
    print("{: <1} {: <50} {: <10} "
          "{: <14} {: <120} {: <30}".format(f'\033[0m',
                                            '"' + str(epi_to_download[11][0:48]) + '"', season,
                                            str(epi_to_download[6]), str(processed[1][0]), tvmaze))


def process_the_episodes_to_download():
    episodes_to_download = get_episodes_to_download()
    
    print("TVM_Action_List ---> Episodes to Download:", len(episodes_to_download))
    # process the episodes that need to be downloading
    print()
    print(f'\033[1m', "                                                                     "
                      "                                                    Shows To Download", f'\033[0m')
    print("{: <1} {: <50} {: <10} {: <14} "
          "{: <120} {: <30} {: <1}".format(f'\033[1m',
                                           "Shown Name: ", "Season:", "Airdate:",
                                           "Torrent Link:", "TVMaze Link:", f'\033[0m'))
    # message_txt = "TVM "
    downloaded_show = ''
    season_dled = False
    for epi_to_download in episodes_to_download:
        hour_now = int(str(datetime.now())[11:13])
        # print(f'Episode {epi_to_download[3]}, with time {hour_now} and date {date_delta("Now", -1)}')
        if epi_to_download[6] == date_delta('Now', -1) and hour_now < 6:
            print(f'Skipping {epi_to_download[3]} because of air date is {epi_to_download[6]} '
                  f'and time {str(hour_now)} is before 6am')
            continue
        season_info = do_season_process(epi_to_download)
        do_text = " ---> Not Downloading"
        season = season_info[1]
        if season_info[2]:
            # print('First Process the whole season request')
            # print(f'Whole season -> {epi_to_download[2]}, Season Info {season_info}')
            processed = do_api_process(epi_to_download, season_info[0])
            # print(f'Whole Season Processed is {processed}')
            if processed[0][0]:
                print(f'Whole Season Processed is {processed}')
                downloaded_show = epi_to_download[11]
                do_text = f" ---> Whole Season downloading "
                season = season_info[0]
                season_dled = True
                display_status(processed, epi_to_download, do_text, season)
                epis = execute_sql(sqltype='Fetch', sql=f'SELECT epiid '
                                                        f'FROM episodes '
                                                        f'WHERE showid = {epi_to_download[1]} AND '
                                                        f'season = {epi_to_download[4]}')
                if len(epis) == 0:
                    print(f'Process the Epi(s) to Download: '
                          f'No episodes found while they should exist for show {epi_to_download[1]}')
                for epi in epis:
                    print(f'Process The Epi(s) to download: {epi[0]}')
                    update_tvmaze_episode_status(epi[0])
                continue
            else:
                display_status(processed, epi_to_download, do_text, season_info[0])
                downloaded_show = ''
                # print('If Whole Season is not downloading try the first episode of the season')
                processed = do_api_process(epi_to_download, season_info[1])
                if processed[0][0]:
                    do_text = " ---> Episode now downloading "
                    season = season_info[1]
                    update_tvmaze_episode_status(epi_to_download[0])
                display_status(processed, epi_to_download, do_text, season)
                continue
        if downloaded_show != epi_to_download[11]:
            season_dled = False
        if season_dled:
            # print('Skip episodes if the request show season is downloading')
            # season = season_info[1]
            # display_status(processed, epi_to_download, do_text, season)
            continue
        # print('Otherwise do a normal episode download try')
        processed = do_api_process(epi_to_download, season_info[1])
        if processed[0][0]:
            do_text = " ---> Episode now downloading "
            season = season_info[1]
            update_tvmaze_episode_status(epi_to_download[0])
        downloaded_show = ''
        display_status(processed, epi_to_download, do_text, season)


'''
    Main program
    First get all the supporting lists we use
'''
downloadAPIs = get_downloadAPIs()
if not downloadAPIs:
    print(f"Main Program: Error getting Download Options: {downloadAPIs}")
    quit()
process = get_cli_args()
print(term_codes.cl_scr)
# Process the data
if process == "Both":
    process_new_shows()
    process_the_episodes_to_download()
elif process == "Review":
    process_new_shows()
elif process == "Download":
    process_the_episodes_to_download()
print()

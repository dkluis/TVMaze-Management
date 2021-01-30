"""

actions.py   The App that handles all actions for reviewing new shows and for downloading episodes based on the
             episode air dates, future will be a manual request for an episode

Usage:
  actions.py -d [--vl=<vlevel>]
  actions.py -h | --help
  actions.py --version

Options:
  -h --help      Show this screen
  -d             Download all outstanding Episodes
  --vl=<vlevel>  Level of verbosity
                   1 = Warnings & Errors Only, 2 = High Level Info,
                   3 = Medium Level Info, 4 = Low Level Info, 5 = All  [default: 1]
  --version      Show version.

"""


from bs4 import BeautifulSoup as Soup
from docopt import docopt

from Libraries import mariaDB, tvm_views, os, datetime, timedelta
from Libraries import def_downloader, date_delta, re
from Libraries import execute_tvm_request, tvmaze_apis, date
from Libraries import logging


def update_show_status(showid, status):
    dl = None
    if status == "Skipped":
        dl = None
    elif status == "Followed":
        dl = def_downloader.dl
    elif status == 'Undecided':
        d = datetime.today() + timedelta(days=14)
        dl = str(d)[:10]
    if not dl:
        sql = f'UPDATE shows SET status = "{status}", download = NULL WHERE `showid` = {showid}'
    else:
        sql = f'UPDATE shows SET status = "{status}", download = "{dl}" WHERE `showid` = {showid}'
    result = db.execute_sql(sqltype='Commit', sql=sql)
    if not result:
        log.write(f'Error updating show status {result}', 0)
    return


def update_tvmaze_followed_shows(showid):
    api = tvmaze_apis.update_followed_shows = str(showid)
    response = execute_tvm_request(api=api, code=True, req_type='put')
    return response


def update_tvmaze_episode_status(epiid):
    api = tvmaze_apis.update_episode_status + str(epiid)
    epoch_date = int(date.today().strftime("%s"))
    data = {"marked_at": epoch_date, "type": 1}
    response = execute_tvm_request(api=api, req_type='put', code=True, data=data, err=True)
    if not response:
        return False
    return True


def validate_requirements(filename, extension, epi_no, showname, base):
    if vli > 2:
        log.write(f'Starting to validate for {filename}, --> {showname}, --> {epi_no}, and {extension}', 3)
    res1 = '1080p'
    res2 = '720p'
    res3 = '480p'
    codex = '264'
    codex2 = '265'
    cont1 = "mkv"
    cont2 = "mp4"
    cont3 = 'avi'
    priority = base
    if res1 in filename.lower():
        priority = priority + 40
    elif res2 in filename.lower():
        priority = priority + 30
    elif res3 in filename.lower():
        priority += 20
    else:
        priority = priority - 40
    if codex in filename.lower():
        priority = priority + 100
    elif codex2 in filename.lower():
        priority = priority + 110
    if extension:
        if cont1 in filename.lower():
            priority = priority + 15
        elif cont2 in filename.lower():
            priority = priority + 10
        elif cont3 in filename.lower():
            priority = priority + 5
    if 'proper' in filename.lower():
        priority = priority + 10
    elif 'repack' in filename.lower():
        priority += 10
    if showname:
        if vli > 2:
            log.write(f'''Checking showname {showname.replace(' ', '.').lower()} > {filename}.lower()''', 3)
        if showname.replace(' ', '.').lower() != filename[0:len(showname)].lower():
            priority = 0
        else:
            if str(epi_no.lower() + ".") not in filename.lower():
                priority = 1
    if vli > 2:
        log.write(f'Validated Requirement - Showname: {showname.replace(" ", ".").lower()} and got Priority: '
                  f'{priority}, Filename: {filename.lower()} and Season {epi_no}', 3)
    return priority


def get_eztv_api_options(imdb_id, seas, showname):
    download_options = []
    if not imdb_id:
        return download_options
    eztv_show = imdb_id
    eztv_url = db.execute_sql(sqltype='Fetch',
                              sql='SELECT link_prefix FROM download_options '
                                  'where `providername` = "eztvAPI"')[0][0] + eztv_show[2:]
    eztv_req_result = execute_tvm_request(api=eztv_url, timeout=(20, 20), err=False)
    if not eztv_req_result:
        return download_options
    eztv_data = eztv_req_result.json()
    if vli > 2:
        log.write(f'Actions: Checking eztvAPi url: {eztv_url}', 3)
    eztv_count = eztv_data['torrents_count']
    if eztv_count == 0:
        return download_options
    eztv_epis = eztv_data['torrents']
    for eztv_epi in eztv_epis:
        filename = str(eztv_epi['filename']).lower()
        mag_url = eztv_epi['magnet_url']
        size = float(eztv_epi['size_bytes']) / 1000000
        size = int(size)
        size = str(size).zfill(6)
        prio = validate_requirements(filename, True, seas, showname, 10)
        if vli > 2:
            log.write(f'Checking filename eztvAPI {filename} with {seas} got prio {prio}', 3)
        if prio > 100:
            download_options.append((prio, filename, mag_url, size, 'eztvAPI'))
    return download_options


def get_eztv_options(show, seas):
    eztv_titles = []
    api = db.execute_sql(sqltype='Fetch',
                         sql='SELECT link_prefix FROM download_options '
                             'where `providername` = "eztv"')[0][0] + show + '-' + seas
    eztv_data = execute_tvm_request(api=api, timeout=(20, 20), err=False)
    if not eztv_data:
        return eztv_titles
    eztv_page = Soup(eztv_data.content, 'html.parser')
    eztv_table = eztv_page.findAll('a', {'class': 'magnet'})
    if len(eztv_table) == 0:
        return eztv_titles
    dloptions = []
    for rec in eztv_table:
        if show.lower() in str(rec).lower() and seas.lower() in str(rec).lower():
            dloptions.append(f"***{rec}***")
    if len(dloptions) == 0:
        return dloptions
    for dlo in dloptions:
        size = 0
        split1 = str(dlo).split('href="')[1]
        magnet_link = str(split1).split('" rel=')[0]
        split1 = str(magnet_link).split(';dn=')[1]
        showname = str(split1).split('%')[0]
        if ' (' in str(dlo):
            split1 = str(dlo).split(' (')[1]
            sizeraw = str(split1).split(') ')[0]
            s = sizeraw.split(' ')
            if s[1] == 'MB':
                size = float(s[0])
                size = int(size)
                size = str(size).zfill(6)
            elif s[1] == 'GB':
                size = float(s[0]) * 1000
                size = int(size)
        size = str(size).zfill(6)
        if vli > 2:
            log.write(f"{dlo} \n Validating {showname}, True, {seas}, {show} ", 3)
        prio = validate_requirements(showname, True, seas, show, 10)
        if vli > 2:
            log.write(f'Prio returned {prio} for {showname}', 3)
        if prio > 100:
            prio = prio - 5
            eztv_titles.append((prio, showname, magnet_link, size, 'eztv'))
    return eztv_titles


def get_rarbg_api_options(show, seas):
    dl_options = []
    dl_info = db.execute_sql(sqltype='Fetch', sql=f'SELECT * from download_options '
                                                  f'WHERE `providername` = "rarbgAPI"')[0]
    main_link = f"{dl_info[1]}{show} {seas}{dl_info[2]}"
    main_request = execute_tvm_request(api=main_link, req_type='get')
    if main_request:
        main_request = main_request.json()
    else:
        return dl_options
    if f'No results found' in str(main_request):
        return dl_options
    if vli > 4:
        log.write(f'Found main_request {main_request}', 5)
    records = main_request['torrent_results']
    for record in records:
        name = record['title']
        magnet = record['download']
        size = str(int(record['size'] / 1000000)).zfill(6)
        prio = validate_requirements(name, True, seas, show, 20)
        if prio > 100:
            dl_options.append((prio, name, magnet, size, 'rarbgAPI'))
    return dl_options


def get_piratebay_api_options(show, seas):
    piratebay_titles = []
    api = 'https://piratebay.bid/s/?q=' + str(show).replace(' ', '+') + '+' + seas
    piratebay_data = execute_tvm_request(api=api, timeout=(20, 20))
    if not piratebay_data:
        return piratebay_titles
    piratebay_page = Soup(piratebay_data.content, 'html.parser')
    piratebay_table = piratebay_page.findAll('table', {'id': 'searchResult'})
    if len(piratebay_table) == 0:
        return piratebay_titles
    piratebay_table = piratebay_table[0]
    pb_table = piratebay_table.findAll('tr')
    magnet_link = ''
    size = 0
    for pb_table_rec in pb_table:
        cl_dl = pb_table_rec.findAll('a', {'class': 'detLink'})
        showname = ''
        showl = ''
        shownamel = ''
        shownamenp = ''
        for cl_dl_rec in cl_dl:
            showname = (cl_dl_rec['title'])
            showl = show.lower().replace(" ", ".")
            shownamel = showname.lower()
            shownamenp = shownamel.replace('+', '.')
        if showl.replace('.', ' ') in shownamel or showl in shownamenp:
            show_refs = pb_table_rec.findAll('a', {'href': re.compile("^magnet:")})
            for ref in show_refs:
                magnet_link = str(ref['href'])
                infos = pb_table_rec.findAll('font', {'class': 'detDesc'})
                for info in infos:
                    sub_info = str(info).split('<font class="detDesc">')
                    sub_info = sub_info[1].split(', ULed by')
                    sub_info = sub_info[0].replace('Uploaded ', '').replace(' Size ', '')
                    sub_info = sub_info.split(',')
                    size = str(sub_info[1]).replace('\xa0', '')
                    if 'MiB' in size:
                        size = str(size).split('MiB')
                        size_multiplier = 1
                    elif 'GiB' in size:
                        size = str(size).split('GiB')
                        size_multiplier = 1000
                    else:
                        size_multiplier = 0
                    sizem = float(size[0]) * size_multiplier
                    sizem = int(sizem)
                    size = str(sizem).zfill(6)
        showname = showname.replace('Details for ', '')
        prio = validate_requirements(showname, False, seas, show, 15)
        if prio > 100:
            piratebay_titles.append((prio, showname, magnet_link, size, 'piratebay'))
    return piratebay_titles


def get_episodes_to_download():
    todownload = db.execute_sql(sqltype='Fetch', sql=tvm_views.eps_to_download)
    if not todownload:
        if vli > 2:
            log.write(f'No episodes to download {todownload}', 3)
    return todownload


def get_download_apis():
    results = db.execute_sql(sqltype='Fetch', sql="SELECT * from download_options")
    if not results:
        log.write(f'Error getting the download_options {results}', 0)
    return results


def get_shows_to_review():
    showstoreview = db.execute_sql(sqltype='Fetch', sql=tvm_views.shows_to_review)
    return showstoreview


def find_dl_info(dl, dlapis):
    for find_dl in dlapis:
        if find_dl[0] == dl:
            return find_dl
    return False


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


def format_download_call(epi_tdl, sore, api):
    downloader = find_dl_info(api, download_apis)
    showname = str(epi_tdl[11]).replace(" ", downloader[3])
    if downloader[2]:
        link = downloader[1] + showname + downloader[3] + sore + downloader[2]
    else:
        link = downloader[1] + showname + downloader[3] + sore
    return link, downloader[0]


def do_api_process(epi_tdl, req):
    formatted_call = format_download_call(epi_tdl, req, epi_tdl[10])
    if formatted_call[1] == 'Multi':
        dler = 'Multi'
        dl_options_rarbg_api = get_rarbg_api_options(epi_tdl[11], req)
        dl_options_piratebay = get_piratebay_api_options(epi_tdl[11], req)
        dl_options_eztv_api = get_eztv_api_options(epi_tdl[12], req, epi_tdl[11])
        dl_options_eztv = get_eztv_options(epi_tdl[11], req)
        dl_options = dl_options_rarbg_api + dl_options_piratebay + dl_options_eztv_api + dl_options_eztv
    elif formatted_call[1] == 'rarbgAPI':
        dl_options = get_rarbg_api_options(epi_tdl[11], req)
        dler = 'rarbgAPI'
    elif formatted_call[1] == 'eztvAPI':
        dl_options = get_eztv_api_options(epi_tdl[12], req, epi_tdl[11])
        dler = 'eztvAPI'
    elif formatted_call[1] == 'piratebay':
        dl_options = get_piratebay_api_options(epi_tdl[11], req)
        dler = 'piratebay'
    elif formatted_call[1] == 'ShowRSS':
        return False, 'RSS link via Catch', 'ShowRSS'
    else:
        return False, 'No Link', 'No activated download provider'
    if formatted_call[1] == 'Multi':
        main_link = f'Formatted call is Multi ---> {formatted_call[0]}'
    else:
        main_link = formatted_call[0]
    sdl_options = sorted(dl_options, key=lambda x: [x[0], x[3]], reverse=True)
    if len(sdl_options) == 0:
        return False, main_link, dler
    else:
        for sdl_o in sdl_options:
            if vli > 2:
                log.write(f'The Options are {sdl_o[0]}, {sdl_o[3]}, {sdl_o[1]}, {sdl_o[4]}', 3)
        for dlo in sdl_options:
            if vli > 2:
                log.write(f'Selected Option = {dlo[0]}, {dlo[3]}, {dlo[1]}, {dlo[4]}', 3)
            command_str = f'''open -a transmission '{dlo[2]}' '''
            os.system(command_str)
            return True, main_link, dler


def display_status(processed, epi_to_download, do_text, season):
    if processed[2] not in ('eztvAPI', 'rarbgAPI', 'piratebay', 'Multi'):
        return
    log.write(f'Showname: {epi_to_download[11][0:50]} > Episode: {season} > Status: {do_text}')
    

def process_the_episodes_to_download():
    episodes_to_download = get_episodes_to_download()
    if vli > 1:
        log.write(f"Episodes to Download: {len(episodes_to_download)}", 2)
    if len(episodes_to_download) == 0:
        return

    downloaded_show = ''
    season_dled = False
    for epi_to_download in episodes_to_download:
        hour_now = int(str(datetime.now())[11:13])
        if epi_to_download[6] == date_delta('Now', -1) and hour_now < 6:
            if vli > 2:
                log.write(f'Skipping {epi_to_download[3]} because of air date is {epi_to_download[6]} '
                          f'and time {str(hour_now)} is before 6am', 3)
            continue
        season_info = do_season_process(epi_to_download)
        do_text = " ---> Not Downloading"
        season = season_info[1]
        if season_info[2]:
            processed = do_api_process(epi_to_download, season_info[0])
            if vli > 2:
                log.write(f'Whole Season Processed is {processed}', 3)
            if processed[0]:
                if vli > 2:
                    log.write(f'Whole Season Processed is {processed}', 3)
                downloaded_show = epi_to_download[11]
                do_text = f" ---> Whole Season downloading "
                season = season_info[0]
                season_dled = True
                display_status(processed, epi_to_download, do_text, season)
                epis = db.execute_sql(sqltype='Fetch', sql=f'SELECT epiid '
                                                        f'FROM episodes '
                                                        f'WHERE showid = {epi_to_download[1]} AND '
                                                        f'season = {epi_to_download[4]}')
                if len(epis) == 0:
                    log.write(f'Process the Epi(s) to Download: '
                              f'No episodes found while they should exist for show {epi_to_download[1]}')
                for epi in epis:
                    log.write(f'Process The Epi(s) to download: {epi[0]}')
                    update_tvmaze_episode_status(epi[0])
                continue
            else:
                display_status(processed, epi_to_download, do_text, season_info[0])
                downloaded_show = ''
                if vli > 2:
                    log.write('If Whole Season is not downloading try the first episode of the season', 3)
                processed = do_api_process(epi_to_download, season_info[1])
                if processed[0]:
                    do_text = " ---> Episode now downloading "
                    season = season_info[1]
                    update_tvmaze_episode_status(epi_to_download[0])
                display_status(processed, epi_to_download, do_text, season)
                continue
        if downloaded_show != epi_to_download[11]:
            season_dled = False
        if season_dled:

            continue
        processed = do_api_process(epi_to_download, season_info[1])
        if processed[0]:
            do_text = " ---> Episode now downloading "
            season = season_info[1]
            update_tvmaze_episode_status(epi_to_download[0])
        downloaded_show = ''
        display_status(processed, epi_to_download, do_text, season)


'''
    Main program
    First get all the supporting lists we use
'''
log = logging(caller='Actions', filename='Process')
log.start()
options = docopt(__doc__, version='Statistics Release 1.0')
vli = int(options['--vl'])
if vli > 5 or vli < 1:
    log.write(f"Unknown Verbosity level of {vli}, try actions.py -h", 0)
    quit()
elif vli > 1:
    log.write(f'Verbosity level is set to: {options["--vl"]}', 2)

db = mariaDB(caller=log.caller, filename=log.filename, vli=vli)

download_apis = get_download_apis()
if not download_apis:
    log.write(f"Error getting Download Options: {download_apis}", 0)
    db.close()
    log.end()
    quit()

if options['-d']:
    process_the_episodes_to_download()

db.close()
log.end()
quit()

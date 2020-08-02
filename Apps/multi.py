from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup as Soup
import re

from terminal_lib import check_cli_args, term_codes
from db_lib import *
from tvm_lib import def_downloader, date_delta
from tvm_api_lib import *


def get_downloadAPIs():
    results = execute_sql(sqltype='Fetch', sql="SELECT * from download_options")
    if not results:
        print(f'Error getting the download_options {results}')
    return results


downloadAPIs = get_downloadAPIs()


def find_dl_info(dl, dlapis):
    for find_dl in dlapis:
        if find_dl[0] == dl:
            return find_dl
    return False


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


def get_rarbg_api_options(show, seas):
    dl_options = []
    dl_info = execute_sql(sqltype='Fetch', sql=f'SELECT * from download_options WHERE `providername` = "rarbgAPI"')[0]
    main_link = f"{dl_info[1]}{show} {seas}{dl_info[2]}"
    main_request = execute_tvm_request(api=main_link, req_type='get').json()
    if 'No results found' in str(main_request):
        return dl_options
    records = main_request['torrent_results']
    for record in records:
        name = record['title']
        magnet = record['download']
        seeders = record['seeders']
        size = str(int(record['size'] / 1000000)).zfill(6)
        prio = validate_requirements(name, True, show)
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
                    sizem = float(size[0]) * size_multiplier
                    sizem = int(sizem)
                    size = str(sizem).zfill(6)
        showname = showname.replace('Details for ', '')
        prio = validate_requirements(showname, False, show)
        if prio > 100:
            piratebay_titles.append((prio, showname, magnet_link, size, 'piratebay'))
    return piratebay_titles


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


def format_download_call(epi_tdl, sore, api):
    downloader = find_dl_info(api, downloadAPIs)
    showname = str(epi_tdl[11]).replace(" ", downloader[3])
    if downloader[2]:
        link = downloader[1] + showname + downloader[3] + sore + downloader[2]
    else:
        link = downloader[1] + showname + downloader[3] + sore
    return link, downloader[0]


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


def do_api_process(epi_tdl, req):
    formatted_call = format_download_call(epi_tdl, req, 'piratebay')
    dl_options_rarbg_api = get_rarbg_api_options(epi_tdl[11], req)
    dl_options_piratebay = get_piratebay_api_options(epi_tdl[11], req)
    dl_options = dl_options_rarbg_api + dl_options_piratebay
    sdl_options = sorted(dl_options, key=lambda x: [x[0], x[3]], reverse=True)
    if len(sdl_options) == 0:
        return False, formatted_call
    else:
        for dlo in sdl_options:
            print(f'Selected Option = {dlo[0]}, {dlo[3]}, {dlo[1]}, {dlo[4]}')
            return dlo, "Found via the Multi-Search"
    
    '''
    if formatted_call[1] == 'rarbgAPI':
        dl_options = get_rarbg_api_options(epi_tdl[11], req)
    elif formatted_call[1] == 'eztvAPI':
        result = eztv_download(epi_tdl[12], req)
    elif formatted_call[1] == 'magnetdl_new':
        result = magnetdl_download(epi_tdl[11], req)
    elif formatted_call[1] == 'piratebay':
        result = piratebay_download(epi_tdl[11], req)
    else:
        result = False, 'No Link Yet'
    return dl_options, formatted_call
    '''
    

def get_episodes_to_download():
    todownload = execute_sql(sqltype='Fetch', sql=tvm_views.eps_to_download)
    if not todownload:
        print(f'No episodes to download {todownload}')
    return todownload


episodes_to_download = get_episodes_to_download()
# print(f'Episodes to Download {episodes_to_download}')
for epi in episodes_to_download:
    print(f'Epi to Download {epi[3]}')
epi_to_download = episodes_to_download[0]
season_info = do_season_process(epi_to_download)
print(f'Season Info for 1st Episodes to download {season_info}')
if season_info[2]:
    seas = season_info[0]
else:
    seas = season_info[1]
processed = do_api_process(epi_to_download, seas)
print(processed)
if processed[0]:
    formatted_call = format_download_call(epi_to_download, seas, processed[4])
    print(f'Magnet for the episode to download {processed[2]} found with URL {formatted_call[0]}')
    command_str = 'open -a transmission ' + processed[2]
    os.system(command_str)
else:
    print(f'Nothing found via {processed[1][0]}')

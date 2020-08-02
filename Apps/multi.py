from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup as Soup
import re

from terminal_lib import check_cli_args, term_codes
from db_lib import *
from tvm_lib import def_downloader, date_delta
from tvm_api_lib import *

episodes_to_download = get_episodes_to_download()
# print(f'Episodes to Download {episodes_to_download}')
for epi_to_download in episodes_to_download:
    print(f'Epi to Download {epi_to_download[11]}')
    # epi_to_download = episodes_to_download[0]
    season_info = do_season_process(epi_to_download)
    # print(f'Season Info for 1st Episodes to download {season_info}')
    if season_info[2]:
        seas = season_info[0]
    else:
        seas = season_info[1]
    processed = do_api_process(epi_to_download, seas)
    # print(processed[0])
    # print(processed[1])
    if processed[0]:
        # formatted_call = format_download_call(epi_to_download, seas, processed[1][1])
        # print(f'Magnet for the episode to download found with URL {formatted_call[0]}')
        command_str = 'open -a transmission ' + processed[0][2]
        os.system(command_str)
    else:
        print(f'Nothing found')

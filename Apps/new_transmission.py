"""

transmission.py The App that handles all transmission generated files (or directories) by processing the
                transmission log and archiving it.  And updating TVMaze that the show or movie has been acquired.

Usage:
  transmission.py [--vl=<vlevel>] [<to_process>]
  transmission.py -h | --help
  transmission.py --version

Options:
  -h --help      Show this screen
  --vl=<vlevel>  Level of verbosity (a = All, i = Informational, w = Warnings only) [default: w]
  --version      Show version.

"""

from docopt import docopt
import time

from Libraries.tvm_functions import process_download_name
from Libraries.tvm_apis import update_tvmaze_episode_status
from Libraries.tvm_db import execute_sql


def get_all_episodes_to_update():
    ttps = []
    try:
        transmissions = open('/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/Transmission.log')
    except IOError as err:
        if vli:
            print(f'{time.strftime("%D %T")} Transmission: Transmission file did not exist: {err}')
        return ttps
    
    for ttp in transmissions:
        if ' Transmission ' in ttp:
            continue
        if len(ttp) < 5:
            continue
        ttps.append(ttp[:-1])
    return ttps


'''
Main Program start
'''

options = docopt(__doc__, version='Transmission Release 2.0.0')
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
    download = options['<to_process>']
    cli = True
else:
    cli = False
    download = get_all_episodes_to_update()
    if len(download) == 0:
        print(f'{time.strftime("%D %T")} Transmission: Nothing to Process in the transmission log')
        quit()

if vli:
    print(f'Download = {download}')

download = 'www.scenetime.com.Lost.S02E02.1080p.HULU.WEBRip.DDP5.1.x264-SH3LBY[rartv]'
epi_info = process_download_name(download)
if epi_info['is_tvshow'] and epi_info['episodeid'] != 0:
    sql = f'select mystatus from episodes where epiid = {epi_info["episodeid"]}'
    result = execute_sql(sqltype='Fetch', sql=sql)[0][0]
    if not result:
        print(f'{time.strftime("%D %T")} Transmission: TVMaze Episode needs updating {epi_info["episodeid"]}')
        result = update_tvmaze_episode_status(epi_info['episodeid'], 1)
    else:
        print(f'{time.strftime("%D %T")} Transmission: Episode {epi_info} already had the status "{result}"')
else:
    print(f'{time.strftime("%D %T")} Transmission: Did not find a valid episode id {epi_info}')

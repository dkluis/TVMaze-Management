"""

shows_update.py    The App that update all followed shows with the latest tvmaze information

Usage:
  shows_update.py [--vl=<vlevel>]
  shows_update.py -h | --help
  shows_update.py --version

Options:
  -h --help             Show this screen
  --vl=<vlevel>         Level of verbosity
                          1 = Warnings & Errors Only, 2 = High Level Info,
                          3 = Medium Level Info, 4 = Low Level Info [default: 0]
"""

from tvm_api_lib import *
from db_lib import *
from tvm_lib import def_downloader

from timeit import default_timer as timer
from datetime import datetime, date
from docopt import docopt


def func_get_cli():
    global vli
    options = docopt(__doc__, version='Shows Release 1.0')
    vli = int(options['--vl'])
    if vli > 4 or vli < 0:
        print(f"{time.strftime('%D %T')} Shows: Unknown Verbosity level of {vli}, try plex_extract.py -h")
        quit()
    elif vli > 1:
        print(f'{time.strftime("%D %T")} Shows: Verbosity level is set to: {options["--vl"]}')
        

def func_get_the_shows():
    sql = f'select showid from shows where status = "Followed"'
    shows = execute_sql(sqltype='Fetch', sql=sql)
    return shows


def func_get_tvmaze_show_info(showid):
    showinfo = execute_tvm_request(f'http://api.tvmaze.com/shows/{showid}')
    showinfo = showinfo.json()
    sql = f"update shows " \
          f"set showstatus = '{showinfo['status']}', " \
          f"premiered = '{showinfo['premiered']}', " \
          f"language = '{showinfo['language']}', " \
          f"thetvdb = '{showinfo['externals']['thetvdb']}', " \
          f"imdb = '{showinfo['externals']['imdb']}' " \
          f"where `showid` = {showid}"
    sql = sql.replace('None', 'NULL')
    result = execute_sql(sqltype='Commit', sql=sql)
    if not result:
        print(f'Error when updating show {showid} {result}')


def func_update_shows(shows):
    global vli
    if not shows:
        if vli > 0:
            print(f'Something wrong with getting the shows to update {shows}')
    elif len(shows) == 0 and vli > 1:
        print(f'No shows found in the DB')
    else:
        for show in shows:
            func_update_the_show(show[0])
            
            
def func_update_the_show(showid):
    if vli > 2:
        print(f'Updating show {showid}')
    func_get_tvmaze_show_info(showid)
    

def main():
    func_get_cli()
    print(vli)
    if vli > 1:
        print(f'{time.strftime("%D %T")} Update Shows >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Started')
    func_update_shows(func_get_the_shows())
    if vli > 1:
        print(f'{time.strftime("%D %T")} Update Shows >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Finished')
    

if __name__ == '__main__':
    vli = 0
    shows_to_update = []
    main()

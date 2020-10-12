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
                          3 = Medium Level Info, 4 = Low Level Info, 5 = all [default: 1]
"""

from Libraries.tvm_apis import *
from Libraries.tvm_functions import paths
from Libraries.tvm_db import *

from docopt import docopt


def func_get_cli():
    global vli
    options = docopt(__doc__, version='Shows Release 1.0')
    vli = int(options['--vl'])
    if vli > 5 or vli < 0:
        print(f"{time.strftime('%D %T')} Shows: Unknown Verbosity level of {vli}, try plex_extract.py -h", flush=True)
        quit()
    elif vli > 1:
        print(f'{time.strftime("%D %T")} Shows: Verbosity level is set to: {options["--vl"]}', flush=True)
    paths_info = paths('Prod')
    print(paths_info.shows_update, flush=True)
    

def func_get_the_shows():
    sql = f'select showid, showname from shows where status = "Followed"'
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
        print(f'Error when updating show {showid} {result}', flush=True)


def func_update_shows(shows):
    global vli
    if not shows:
        if vli > 0:
            print(f'Something wrong with getting the shows to update {shows}', flush=True)
    elif len(shows) == 0 and vli > 1:
        print(f'No shows found in the DB')
    else:
        for show in shows:
            func_update_the_show(show[0], show[1])
            
            
def func_update_the_show(showid, showname):
    if vli > 2:
        print(f'Updating show {showid}, {showname}', flush=True)
    func_get_tvmaze_show_info(showid)
    time.sleep(1)
    

def main():
    func_get_cli()
    print(vli)
    if vli > 1:
        print(f'{time.strftime("%D %T")} '
              f'Update Shows >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Started', flush=True)
    func_update_shows(func_get_the_shows())
    if vli > 1:
        print(f'{time.strftime("%D %T")} '
              f'Update Shows >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Finished', flush=True)
    
    
if __name__ == '__main__':
    vli = 0
    shows_to_update = []
    main()
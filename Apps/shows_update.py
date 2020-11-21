"""

shows_update.py    The App that update all followed shows with the latest tvmaze information

Usage:
  shows_update.py -f [--vl=<vlevel>]
  shows_update.py -o [--vl=<vlevel>]
  shows_update.py -a [--vl=<vlevel]
  shows_update.py -t <showid> [--vl=<vlevel]
  shows_update.py -r <showid> [--vl=<vlevel]
  shows_update.py -h | --help
  shows_update.py --version

Options:
  -h --help             Show this screen
  --vl=<vlevel>         Level of verbosity
                          1 = Warnings & Errors Only, 2 = High Level Info,
                          3 = Medium Level Info, 4 = Low Level Info, 5 = all [default: 5]
  -r                    restart at showid
  -t                    try updating only showid
  -a                    all shows
  -f                    only the followed shows
  -o                    all non-followed shows
"""

from docopt import docopt

from Libraries.tvm_apis import *
from Libraries.tvm_db import *
from Libraries.tvm_functions import paths


def func_get_cli():
    global vli
    global sql
    options = docopt(__doc__, version='Update Shows Release 2.0')
    vli = int(options['--vl'])
    if vli > 5 or vli < 0:
        print(f"{time.strftime('%D %T')} Update Shows: Unknown Verbosity level of {vli}, try plex_extract.py -h",
              flush=True)
        quit()
    elif vli > 1:
        print(f'{time.strftime("%D %T")} Update Shows: Verbosity level is set to: {options["--vl"]}', flush=True)
    
    if options['-a']:
        sql = 'select showid, showname from shows'
    elif options['-f']:
        sql = 'select showid, showname from shows where status = "Followed"'
    elif options['-o']:
        sql = 'select showid, showname from shows where status != "Followed"'
    elif options['-t']:
        sql = f'select showid, showname from shows where showid = {options["<showid>"]}'
    elif options['-r']:
        sql = f'select showid, showname from shows where showid >= {options["<showid>"]}'
    else:
        print(f"{time.strftime('%D %T')} Shows: No known - parameter given, try plex_extract.py -h", flush=True)
        quit(1)
    paths_info = paths('Prod')
    print(paths_info.shows_update, flush=True)


def func_get_the_shows():
    shows = execute_sql(sqltype='Fetch', sql=sql)
    return shows


def func_get_tvmaze_show_info(showid):
    showinfo = execute_tvm_request(f'http://api.tvmaze.com/shows/{showid}', timeout=(20, 10), return_err=True)
    if not showinfo:
        print(f'Error with API call {showinfo}')
        return
    if 'Error Code:' in showinfo:
        print(f'{time.strftime("%D %T")}'
              f'This show gives an error: {showid} {showinfo} ', flush=True)
        if "404" in showinfo:
            print(f'Now Deleting:', showid)
            sql = f'delete from shows where `showid` = {showid}'
            result = execute_sql(sqltype='Commit', sql=sql)
            print(f'Delete result:', result)
        return
    
    showinfo = showinfo.json()
    sql = f"update shows " \
          f"set showstatus = '{showinfo['status']}', " \
          f"premiered = '{showinfo['premiered']}', " \
          f"language = '{showinfo['language']}', " \
          f"thetvdb = '{showinfo['externals']['thetvdb']}', " \
          f"imdb = '{showinfo['externals']['imdb']}' " \
          f"where `showid` = {showid}"
    sql = sql.replace("'None'", 'NULL').replace('None', 'NULL')
    result = execute_sql(sqltype='Commit', sql=sql)
    if not result:
        print(f'{time.strftime("%D %T")} Error when updating show {showid} {result}', flush=True)


def func_update_shows(shows):
    global vli
    if not shows:
        if vli > 0:
            print(f'{time.strftime("%D %T")} Something wrong with getting the shows to update {shows}', flush=True)
    elif len(shows) == 0 and vli > 1:
        print(f'{time.strftime("%D %T")} No shows found in the DB', flush=True)
    else:
        for show in shows:
            func_update_the_show(show[0], show[1])


def func_update_the_show(showid, showname):
    if vli > 2:
        print(f'{time.strftime("%D %T")} Updating show {showid}, {showname}', flush=True)
    func_get_tvmaze_show_info(showid)
    # time.sleep(1)


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

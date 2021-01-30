"""

shows_update.py    The App that update all shows with the latest tvmaze information

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

from Libraries import execute_tvm_request, mariaDB, logging


def func_get_cli():
    global vli
    global sql
    options = docopt(__doc__, version='Update Shows Release 2.0')
    vli = int(options['--vl'])
    if vli > 5 or vli < 0:
        log.write(f"Unknown Verbosity level of {vli}, try plex_extract.py -h", 0)
        db.close()
        quit()
    elif vli > 1:
        log.write(f'Verbosity level is set to: {options["--vl"]}', 2)
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
        log.write(f"No known - parameter given, try plex_extract.py -h", 0)
        db.close()
        quit()


def func_get_the_shows():
    shows = db.execute_sql(sqltype='Fetch', sql=sql)
    return shows


def func_get_tvmaze_show_info(showid):
    showinfo = execute_tvm_request(f'http://api.tvmaze.com/shows/{showid}', timeout=(20, 10), return_err=True)
    if not showinfo:
        log.write(f'Error with API call {showinfo}', 0)
        return
    if 'Error Code:' in showinfo:
        log.write(f'This show gives an error: {showid} {showinfo}')
        if "404" in showinfo:
            log.write(f'Now Deleting: {showid}')
            sql_tvm = f'delete from shows where `showid` = {showid}'
            result = db.execute_sql(sqltype='Commit', sql=sql_tvm)
            log.write(f'Delete result: {result}')
        return
    
    showinfo = showinfo.json()
    sql_shows = f"update shows " \
                f"set showstatus = '{showinfo['status']}', " \
                f"premiered = '{showinfo['premiered']}', " \
                f"language = '{showinfo['language']}', " \
                f"thetvdb = '{showinfo['externals']['thetvdb']}', " \
                f"imdb = '{showinfo['externals']['imdb']}' " \
                f"where `showid` = {showid}"
    result = db.execute_sql(sqltype='Commit', sql=sql_shows)
    if not result:
        log.write(f'Error when updating show {showid} {result}', 0)


def func_update_shows(shows):
    if not shows:
        if vli > 0:
            log.write(f'Something wrong with getting the shows to update {shows}', 0)
    elif len(shows) == 0 and vli > 1:
        log.write(f'No shows found in the DB', 2)
    else:
        for show in shows:
            func_update_the_show(show[0], show[1])


def func_update_the_show(showid, showname):
    if vli > 1:
        log.write(f'Updating show {showid}, {showname}', 2)
    func_get_tvmaze_show_info(showid)


def main():
    func_get_cli()
    func_update_shows(func_get_the_shows())


if __name__ == '__main__':
    vli = 0
    shows_to_update = []
    
    log = logging(caller='Shows Update', filename='Shows_Update')
    log.start()
    
    db = mariaDB(caller=log.caller, filename=log.filename, vli=vli)
    sql = ''
    
    main()
    
    db.close()
    log.end()

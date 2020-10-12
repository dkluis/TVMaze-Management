import mariadb
import sqlite3
from sqlalchemy import create_engine
import sys
import os


class mdbi:
    def __init__(self, h, d):
        check = os.getcwd()
        if 'Pycharm' in check:
            prod = False
        else:
            prod = True
        if h == '':
            if 'SharedFolders' in check:
                self.host = '192.168.42.68'
            else:
                self.host = 'localhost'
        else:
            self.host = h
        self.user = 'dick'
        self.password = 'Sandy3942'
        if d == '':
            if prod:
                self.db = 'TVMazeDB'
            else:
                self.db = 'Test-TVM-DB'
        else:
            self.db = d


def connect_mdb(h='', d='', err=True):
    mdb_info = mdbi(h, d)
    try:
        mdb = mariadb.connect(
            host=mdb_info.host,
            user=mdb_info.user,
            password=mdb_info.password,
            database=mdb_info.db)
    except mariadb.Error as e:
        if err:
            print(f"Connect MDB: Error connecting to MariaDB Platform: {e}", flush=True)
            print('--------------------------------------------------------------------------', flush=True)
            sys.exit(1)
    mcur = mdb.cursor()
    mdict = {'mdb': mdb,
             'mcursor': mcur}
    return mdict


def close_mdb(mdb):
    mdb.close()


def connect_pd():
    mdb_info = mdbi('', '')
    sql_alchemy = f'mysql://{mdb_info.user}:{mdb_info.password}@{mdb_info.host}/{mdb_info.db}'
    mdbe = create_engine(sql_alchemy)
    return mdbe


def execute_sql(con='', db='', cur='', batch='', h='', d='', sqltype='', sql=''):
    mdb_info = mdbi(h, d)
    if h == '':
        h = mdb_info.host
    if d == '':
        d = mdb_info.db
    if con != "Y":
        tvm = connect_mdb(mdb_info.host, mdb_info.db)
        tvmcur = tvm['mcursor']
        tvmdb = tvm['mdb']
    else:
        tvmcur = cur
        tvmdb = db
    
    if sqltype == 'Commit':
        try:
            tvmcur.execute(sql)
            if batch != "Y":
                tvmdb.commit()
        except mariadb.Error as er:
            print('Execute SQL (Commit) Database Error: ', d, er, sql, flush=True)
            print('----------------------------------------------------------------------')
            if con != 'Y':
                close_mdb(tvmdb)
            return False, er
        if con != 'Y':
            close_mdb(tvmdb)
        return True
    elif sqltype == "Fetch":
        try:
            tvmcur.execute(sql)
            result = tvmcur.fetchall()
        except mariadb.Error as er:
            print('Execute SQL (Fetch) Database Error: ', d, er, sql, flush=True)
            print('----------------------------------------------------------------------', flush=True)
            if con != 'Y':
                close_mdb(tvmdb)
            return False, er
        if con != 'Y':
            close_mdb(tvmdb)
        return result
    else:
        return False, 'Not implemented yet'



class sdb_info:
    check = os.getcwd()
    if 'Pycharm' in check:
        data = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/Plex DB/com.plexapp.plugins.library.db'
    else:
        data = '/Users/dick/PycharmProjects/TVMaze/Data/TVMaze.db'
    

def connect_sdb():
    sdb = sqlite3.connect(sdb_info.data)
    scur = sdb.cursor()
    sdict = {'sdb': sdb,
             'scursor': scur}
    return sdict


def close_sdb(sdb):
    sdb.close()


def execute_sqlite(sqltype='', sql=''):
    sdb = connect_sdb()
    sdbcur = sdb['scursor']
    sdbdb = sdb['sdb']
    if sqltype == 'Commit':
        try:
            sdbcur.execute(sql)
            sdbdb.commit()
        except sqlite3.Error as er:
            print('Commit Database Error: ', er, sql)
            print('----------------------------------------------------------------------')
            close_sdb(sdbdb)
            return False, er
        close_sdb(sdbdb)
        return True
    elif sqltype == "Fetch":
        try:
            sdbcur.execute(sql)
            result = sdbcur.fetchall()
        except sqlite3.Error as er:
            print('Execute SQL Database Error: ', er, sql)
            print('----------------------------------------------------------------------')
            close_sdb(sdbdb)
            return False, er
        close_sdb(sdbdb)
        return result
    else:
        return False, 'Not implemented yet'


def create_db_sql(db):
    return 'CREATE DATABASE ' + db


class create_tb_key_values:
    sql = "CREATE TABLE `key_values` " \
          "(`key` varchar(25) NOT NULL, " \
          "`info` varchar(375) DEFAULT NULL, " \
          "`comments` varchar(125) DEFAULT NULL, " \
          "UNIQUE KEY `key_values_UN` (`key`)) " \
          "ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='TVMaze internal key info';"
    fill = "INSERT INTO key_values (`key`,info,comments) VALUES " \
           "('def_dl','piratebay','The default downloader to assign to newly followed shows')," \
           "('email','YOUR GMAIL ADDRESS','your gmail email address')," \
           "('emailpas','YOUR-EMAIL-PASSWORD','your gmail password')," \
           "('minput_x','11','Line where the menu input is displayed:  Calc is mtop + minput_x')," \
           "('mmenu_2y','65','Second Column of Menu items')," \
           "('mmenu_3y','110','Third Column of Menu items')," \
           "('mmenu_y','10','First Column of Menu items')," \
           "('mstatus_x','2','Line where the Status is displayed:  Calc is minput_x + mstatus_x')," \
           "('mstatus_y','18','Column where the status messasges are displayed')," \
           "('msub_screen_x','2','Number of line to skip for sub_screen processing')," \
           "('mtop','2','Top line where the Menu starts')," \
           "('plexdonotmove','sample.mkv,sample.mp4,sample.avi,sample.wmv,rarbg.mp4,rarbg.mkv,rarbg.avi,rarbg.wmv'," \
           "'Downloaded files that should not go to Plex')," \
           "('plexexts','mkv,mp4,mv4,avi,wmv,srt','Media extension to process')," \
           "('plexmovd','/Volumes/HD-Data-CA-Server/PlexMedia/Movies/','Movies Main Directory')," \
           "('plexmovstr','720p,1080p,dvdscr,web-dl,web-,bluray,x264,dts-hd,acc-rarbg,solar,h264,hdtv,rarbg,-sparks," \
           "-lucidtv','Eliminate these string from the movie name')," \
           "('plexprefs','www.torrenting.org  -  ,www.torrenting.org - ,www.Torrenting.org       " \
           ",www.torrenting.org.," \
           "from [ www.torrenting.me ] -,[ www.torrenting.com ] -,www.Torrenting.com  -  ,www.torrenting.com -," \
           "www.torrenting.com,www.torrenting.me -,www.torrenting.me,www.scenetime.com  -,www.scenetime.com - ," \
           "www.scenetime.com -,www.scenetime.com,www.speed.cd - ,www.speed.cd,xxxxxxxxx'," \
           "'Prefixes to ignore for show or movies names')," \
           "('plexprocessed'," \
           "'/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/TransmissionFiles/Processed/'" \
           ",'Directory where the Plex Processor put undetermined downloads')," \
           "('plexsd','/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/TransmissionFiles/'," \
           "'Download Source Directory')," \
           "('plextrash','/Users/dick/.Trash/','The Trash Directory')," \
           "('plextvd1','/Volumes/HD-Data-CA-Server/PlexMedia/TV Shows/','TV Shows Main Direcotory')," \
           "('plextvd2','/Volumes/HD-Data-CA-Server/PlexMedia/Kids/TV Shows/','Second directory to store tv shows " \
           "(for the grandkids)')," \
           "('plextvd2selections','Doc Mcstuffins,Elena Of Avalor,Mickey And The Roadster Racers,Sofia The First," \
           "Tangled The Series,Star Wars Resistance,Avengers Assemble,Star Wars The Clone Wars'," \
           "'The different shows to store separate for the grandkids')," \
           "('sms','8138189195@tmomail.net','You cell phone providers email adress to get you text messages')," \
           "('tvmheader','{''Authorization'': ''Basic YOUR-TVMAZE-API-ACCESS-TOKEN''}'," \
           "'tvmaze private key:  Use Dashboard to pick up password and use Premiun API testing to login in and get " \
           "authorization key');"


class create_tb_dls:
    sql = "CREATE TABLE `download_options` (`providername` varchar(15) DEFAULT NULL," \
          " `link_prefix` varchar(75) DEFAULT NULL," \
          " `suffixlink` varchar(50) DEFAULT NULL," \
          " `searchchar` varchar(5) DEFAULT NULL," \
          " UNIQUE KEY `download_options_UN` (`providername`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='TVMaze Downloader Info'"
    fill = [
        "INSERT INTO download_options (`providername`,link_prefix,suffixlink,searchchar) VALUES "
        "('rarbgAPI','Auto via RARBG API  --> ',NULL,' ');",
        "INSERT INTO download_options (`providername`,link_prefix,suffixlink,searchchar) VALUES "
        "('magnetdl','https://www.magnetdl.com/','/','-');",
        "INSERT INTO download_options (`providername`,link_prefix,suffixlink,searchchar) VALUES "
        "('torrentfunk','https://www.torrentfunk.com/television/torrents/','.html','-');",
        "INSERT INTO download_options (`providername`,link_prefix,suffixlink,searchchar) VALUES "
        "('ShowRSS','Auto via ShowRSS    --> ',NULL,' ');",
        "INSERT INTO download_options (`providername`,link_prefix,suffixlink,searchchar) VALUES "
        "('eztvAPI','Auto via Eztv''s API --> ',NULL,' ');",
        "INSERT INTO download_options (`providername`,link_prefix,suffixlink,searchchar) VALUES "
        "('rarbg','https://rarbg.to/torrents.php?search=',NULL,'+');",
        "INSERT INTO download_options (`providername`,link_prefix,suffixlink,searchchar) VALUES "
        "(NULL,'No Link associated',NULL,' ');",
        "INSERT INTO download_options (`providername`,link_prefix,suffixlink,searchchar) VALUES "
        "('rarbgmirror','--https://rarbgmirror.org/torrents.php?search=',NULL,'+');",
        "INSERT INTO download_options (`providername`,link_prefix,suffixlink,searchchar) VALUES "
        "('eztv','https://eztv.io/search/',NULL,'-');",
        "INSERT INTO download_options (`providername`,link_prefix,suffixlink,searchchar) VALUES "
        "('Skip','Still Following but not downloading',NULL,NULL);"
    ]


class create_tb_shows:
    sql = "CREATE TABLE `shows` (`showid` bigint(10) UNSIGNED NOT NULL ," \
          " `showname` varchar(100) DEFAULT NULL," \
          " `url` varchar(130) DEFAULT NULL," \
          " `type` varchar(20) DEFAULT NULL," \
          " `showstatus` varchar(25) DEFAULT NULL," \
          " `premiered` varchar(10) DEFAULT NULL," \
          " `language` varchar(20) DEFAULT NULL," \
          " `runtime` integer(3) unsigned DEFAULT NULL," \
          " `network` varchar(50) DEFAULT NULL," \
          " `country` varchar(50) DEFAULT NULL," \
          " `tvrage` varchar(15) DEFAULT NULL," \
          " `thetvdb` varchar(15) DEFAULT NULL," \
          " `imdb` varchar(15) DEFAULT NULL," \
          " `tvmaze_updated` bigint(15) DEFAULT NULL," \
          " `tvmaze_upd_date` date DEFAULT NULL," \
          " `status` varchar(15) DEFAULT NULL," \
          " `download` varchar(15) DEFAULT NULL," \
          " `record_updated` date DEFAULT NULL," \
          " `alt_showname` varchar(100) DEFAULT NULL," \
          " `alt_sn_override` varchar(5) DEFAULT NULL," \
          " `eps_count` integer(4) unsigned default NULL," \
          " `eps_updated` date default NULL," \
          " UNIQUE KEY `shows_UN` (`showid`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='ALL TVMaze Supported TV Shows'"


class create_tb_eps_by_show:
    sql = "CREATE TABLE `episodes` (`epiid` bigint(10) UNSIGNED NOT NULL ," \
          " `showid` bigint(10) UNSIGNED NOT NULL," \
          " `showname` varchar(100) DEFAULT NULL," \
          " `epiname` varchar(130) DEFAULT NULL," \
          " `url` varchar(175) DEFAULT NULL," \
          " `season` int(3) UNSIGNED DEFAULT NULL," \
          " `episode` int(4) UNSIGNED DEFAULT NULL," \
          " `airdate` date DEFAULT NULL," \
          " `mystatus` varchar(20) DEFAULT NULL," \
          " `mystatus_updated` date DEFAULT NULL," \
          " `rec_updated` date DEFAULT NULL," \
          " UNIQUE KEY `episodes_UN` (`epiid`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='TVMaze All episodes for all followed TV Shows'"


class create_tb_statistics:
    sql = "CREATE TABLE statistics (`statepoch` bigint(15) UNSIGNED PRIMARY KEY NOT NULL, " \
          "`statdate` datetime, " \
          "`tvmshows` integer DEFAULT NULL, " \
          "`myshows` integer DEFAULT NULL, " \
          "`myshowsended` integer DEFAULT NULL, " \
          "`myshowstbd` integer DEFAULT NULL, " \
          "`myshowsrunning` integer DEFAULT NULL, " \
          "`myshowsindevelopment` integer DEFAULT NULL, " \
          "`myepisodes` integer DEFAULT NULL, " \
          "`myepisodeswatched` integer DEFAULT NULL, " \
          "`myepisodestowatch` integer DEFAULT NULL, " \
          "`myepisodesskipped` integer DEFAULT NULL, " \
          "`myepisodestodownloaded` integer DEFAULT NULL, " \
          "`myepisodesannounced` integer DEFAULT NULL, " \
          "`statrecind` varchar(15) NOT NULL, " \
          "`nodownloader` integer DEFAULT NULL, " \
          "`rarbgapi` integer DEFAULT NULL, " \
          "`rarbg` integer DEFAULT NULL, " \
          "`rarbgmirror` integer DEFAULT NULL, " \
          "`showrss` integer DEFAULT NULL, " \
          "`skipmode` integer DEFAULT NULL, " \
          "`eztvapi` integer DEFAULT NULL, " \
          "`eztv` integer DEFAULT NULL, " \
          "`magnetdl` integer DEFAULT NULL, " \
          "`torrentfunk` integer DEFAULT NULL, " \
          " UNIQUE KEY `statistic_UN` (`statepoch`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='TVMaze Statistic'"


def tables(db, tbl=''):
    if tbl == '':
        return f"select distinct table_name from information_schema.columns " \
               f"where table_schema = '{db}' order by table_name;"
    else:
        return f"select column_name, ordinal_position from information_schema.columns " \
               f"where table_schema = '{db}' and table_name = '{tbl}';"


class tvm_views:
    shows_to_review = "SELECT * " \
                      "FROM shows " \
                      "WHERE (status = 'New' AND record_updated <= CURRENT_DATE) OR " \
                      "(status = 'Undecided' and download <= CURRENT_DATE);"
    shows_to_review_tvmaze = "SELECT showid, showname, network, language, type, showstatus, status, premiered, " \
                             "download, imdb, thetvdb " \
                             "FROM shows " \
                             "WHERE (status = 'New' AND record_updated <= CURRENT_DATE) OR " \
                             "(status = 'Undecided' and download <= CURRENT_DATE) " \
                             "ORDER by download, showid;"
    shows_to_review_count = "SELECT count(*) " \
                             "FROM shows " \
                             "WHERE (status = 'New' AND record_updated <= CURRENT_DATE) OR " \
                             "(status = 'Undecided' and download <= CURRENT_DATE) " \
                             "ORDER by download, showid;"
    eps_to_download = "SELECT e.*, s.download, s.alt_showname, s.imdb FROM episodes e " \
                      "JOIN shows s on e.showid = s.showid " \
                      "WHERE mystatus is NULL and airdate is not NULL and airdate <= subdate(current_date, 1) " \
                      "and download != 'Skip' " \
                      "ORDER BY showid, season, episode;"
    eps_to_check = "SELECT e.*, s.download, s.showname FROM episodes e " \
                   "JOIN shows s on e.showid = s.showid " \
                   "WHERE s.status = 'Followed' " \
                   "and s.download = 'Skip' " \
                   "and e.mystatus is NULL " \
                   "ORDER BY s.showid, e.season, e.episode;"


class stat_views:
    download_options = "SELECT statdate, nodownloader, rarbg, rarbgapi, rarbgmirror, showrss, skipmode, eztv, " \
                       "eztvapi, magnetdl, torrentfunk " \
                       "FROM statistics " \
                       "WHERE statrecind = 'download_options' " \
                       "ORDER BY statepoch;"
    stats = "SELECT * FROM statistics " \
            "WHERE statrecind = 'TVMaze' " \
            "ORDER BY statepoch;"
    shows = "SELECT statdate, tvmshows, myshows, myshowsended, myshowstbd, myshowsrunning, myshowsindevelopment " \
            "FROM statistics " \
            "WHERE statrecind = 'TVMaze' " \
            "ORDER BY statepoch;"
    episodes = "SELECT statdate, myepisodes, myepisodestowatch, myepisodesskipped, myepisodestodownloaded, " \
               "myepisodesannounced, myepisodeswatched " \
               "FROM statistics " \
               "WHERE statrecind = 'TVMaze' " \
               "ORDER BY statepoch;"
    count_stats = "SELECT count(*) FROM statistics"
    count_all_shows = "SELECT COUNT(*) from shows"
    count_my_shows = "SELECT COUNT(*) from shows where status = 'Followed'"
    count_my_shows_running = "SELECT COUNT(*) from shows where showstatus = 'Running' and status = 'Followed'"
    count_my_shows_ended = "SELECT COUNT(*) from shows where showstatus = 'Ended' and status = 'Followed'"
    count_my_shows_in_limbo = "SELECT COUNT(*) from shows where showstatus = 'To Be Determined' and status = 'Followed'"
    count_my_shows_in_development = "SELECT COUNT(*) from shows " \
                                    "where showstatus = 'In Development' and status = 'Followed'"
    count_all_shows_skipped = "SELECT COUNT(*) from shows where showstatus = 'Skipped' and status = 'Followed'"
    count_my_episodes = "SELECT COUNT(*) from episodes"
    count_my_episodes_watched = "SELECT COUNT(*) from episodes where mystatus = 'Watched'"
    count_my_episodes_to_watch = "SELECT COUNT(*) from episodes where mystatus = 'Downloaded'"
    count_my_episodes_skipped = "SELECT COUNT(*) from episodes where mystatus = 'Skipped'"
    count_my_episodes_future = "SELECT COUNT(*) from episodes where mystatus is null"
    count_my_episodes_to_download = "SELECT count(*) FROM episodes e " \
                                    "JOIN shows s on e.showid = s.showid " \
                                    "WHERE mystatus is NULL and airdate is not NULL and airdate <= current_date " \
                                    "and s. download != 'Skip';"


class std_sql:
    followed_shows = "SELECT showid FROM shows WHERE status = 'Followed' ORDER BY showid"
    episodes = "SELECT epiid FROM episodes WHERE mystatus IS NOT NULL ORDER BY epiid"


def generate_update_sql(table, where, **kwargs):
    sql = f'UPDATE {table} set '
    first = True
    for key, value in kwargs.items():
        if value is None:
            value = 'NULL'
        if type(value) == str:
            if key != 'where_clause' \
                    and value != 'NULL' \
                    and value != 'current_date' \
                    and "date" not in key:
                value = f'"{value}"'
        if not first:
            sql = sql + f", "
        sql = sql + f"{key}={value}"
        first = False
    sql = f"{sql} WHERE {where}"
    return sql


def process_value(value):
    v0 = value[0]
    v1 = value[1]
    if str(v0).lower() == 'quotes':
        if '"' in v1:
            v1 = str(v1).replace('"', "'")
        v1 = f'"{str(v1)}"'
    elif str(v0).lower() == 'none':
        v1 = 'NULL'
    return v1


def generate_insert_sql(primary, table, **kwargs):
    sqlval = ''
    for key, value in kwargs.items():
        new_value = process_value(value)
        sqlval = sqlval + f"{new_value},"
    sql = f"INSERT INTO {table} VALUES ({primary},{sqlval[:-1]})"
    return sql


def get_tvmaze_info(key):
    sql = f"SELECT info from key_values WHERE `key` = {key} "
    info = execute_sql(sqltype='Fetch', sql=sql)
    if not info:
        return False
    else:
        info = info[0][0]
    return info


def find_new_shows():
    info = execute_sql(sqltype='Fetch', sql=tvm_views.shows_to_review)
    return info


def get_download_options(html=False):
    if not html:
        download_options = execute_sql(sqltype='Fetch', sql="SELECT * from download_options ")
    else:
        download_options = execute_sql(sqltype='Fetch', sql="SELECT * from download_options "
                                                            "where link_prefix like 'http%' ")
    return download_options


class num_list:
    new_list = find_new_shows()
    num_newshows = len(new_list)


def count_by_download_options():
    rarbg_api = execute_sql(sqltype='Fetch',
                            sql="SELECT COUNT(*) from shows WHERE download = 'rarbgAPI' AND status = 'Followed'")
    rarbg = execute_sql(sqltype='Fetch',
                        sql="SELECT COUNT(*) from shows WHERE download = 'rarbg' AND status = 'Followed'")
    rarbgmirror = execute_sql(sqltype='Fetch',
                              sql="SELECT COUNT(*) from shows WHERE download = 'rarbgmirror' AND status = 'Followed'")
    showrss = execute_sql(sqltype='Fetch',
                          sql="SELECT COUNT(*) from shows WHERE download = 'ShowRSS' AND status = 'Followed'")
    eztv_api = execute_sql(sqltype='Fetch',
                           sql="SELECT COUNT(*) from shows WHERE download = 'eztvAPI' AND status = 'Followed'")
    no_dl = execute_sql(sqltype='Fetch',
                        sql="SELECT COUNT(*) from shows WHERE download is NULL AND status = 'Followed'")
    skip = execute_sql(sqltype='Fetch',
                       sql="SELECT COUNT(*) from shows WHERE download = 'Skip' AND status = 'Followed'")
    eztv = execute_sql(sqltype='Fetch',
                       sql="SELECT COUNT(*) from shows WHERE download = 'eztv' AND status = 'Followed'")
    magnetdl = execute_sql(sqltype='Fetch',
                           sql="SELECT COUNT(*) from shows WHERE download = 'magnetdl' AND status = 'Followed'")
    torrentfunk = execute_sql(sqltype='Fetch',
                              sql="SELECT COUNT(*) from shows WHERE download = 'torrentfunk' AND status = 'Followed'")
    piratebay = execute_sql(sqltype='Fetch',
                            sql="SELECT COUNT(*) from shows WHERE download = 'piratebay' AND status = 'Followed'")
    multi = execute_sql(sqltype='Fetch',
                        sql="SELECT COUNT(*) from shows WHERE download = 'Multi' AND status = 'Followed'")
    value = (no_dl[0][0], rarbg_api[0][0], rarbg[0][0], rarbgmirror[0][0], showrss[0][0], skip[0][0],
             eztv_api[0][0], eztv[0][0], magnetdl[0][0], torrentfunk[0][0], piratebay[0][0], multi[0][0])
    return value



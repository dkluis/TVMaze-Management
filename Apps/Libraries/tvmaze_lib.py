import sqlite3
import sys
import re
import os
import time
import ast
from datetime import datetime, timedelta, date
from timeit import default_timer as timer

import requests
import mariadb

from dearpygui.core import log_info, does_item_exist, add_input_text, add_same_line, add_button, add_separator, \
    add_table, get_value, set_table_data
from dearpygui.simple import window

"""
    Logging Library for TVM-Management
"""


class logging:
    def __init__(self, env=False, caller='Unknown', filename='Unknown'):
        """
        :param env      Anything but 'Prod' (is default) will put the log file in the test environment mode
                          All paths come from the key_values in the DB
        :param caller   The program opening the log file
        :param filename The filename to use

        :function open
        """
        if not env:
            if 'Pycharm' in os.getcwd():
                env = 'Test'
            else:
                env = 'Prod'
        
        secret = ''
        try:
            secret = open('/Users/dick/.tvmaze/config', 'r')
        except IOError as err:
            print('TVMaze config is not found at /Users/dick/.tvmaze/config with error', err)
            quit()
        conf = ast.literal_eval(secret.read())
        if env == 'Prod':
            lp = conf['prod_logs']
        else:
            lp = conf['tst_logs']
        if 'SharedFolders' in os.getcwd():
            lp = str(lp).replace('HD-Data-CA-Server', 'SharedFolders')

        if len(caller) < 15:
            spaces = '               '
            needed = 15 - len(caller)
            caller = caller + spaces[:needed]
        self.caller = caller
        
        self.log_path = lp
        self.logfile = open(f'.{self.caller}', "+a")
        self.logfile.close()
        
        self.filename = filename
        self.file_status = False
        self.content = []
        self.started = 0
        self.ended = 0
        self.elapsed = 0
    
    def open(self, mode='a+', read=False):
        """
                    Open the log file
        :param mode:    The open mode for the file, default = a+
        :param read:    Also put contents into: log file .content
        """
        try:
            self.logfile = open(f'{self.log_path}{self.filename}.log', mode)
        except IOError as error:
            self.logfile = open(f'{self.log_path}{self.filename}.log', 'w+')
            self.write(f'Created the log file {self.filename} due to open error: {error}', 0)
            self.logfile.close()
            self.logfile = open(f'{self.log_path}{self.filename}.log', mode)
        self.file_status = True
        if read:
            self.read()
    
    def close(self):
        """
                    Close the file
        """
        if self.file_status:
            self.logfile.close()
            self.file_status = False
    
    def write(self, message='', level=1, read=False):
        """
                    Write the message to the log file
        :param message:     Text to be written
        :param level:       Information Level Indicator
        :param read:        Also read file into log file .content
        """
        message = f"{self.caller} > Level {level} > {time.strftime('%D %T')} > {message}\n"
        if not self.file_status:
            self.open(mode='a+')
            self.logfile.write(message)
            self.close()
        else:
            self.logfile.write(message)
        if read:
            self.read()
    
    def empty(self):
        """
                    Empty the log file
        :return:
        """
        if self.file_status:
            self.close()
        self.logfile = open(f'{self.log_path}{self.filename}.log', 'w+')
        self.close()
        self.file_status = False
    
    def read(self):
        """
                    Read the whole log file
                    Info is in the .content list
        return:     Log File content
        """
        self.close()
        self.open(mode='r+')
        self.content = self.logfile.readlines()
        self.close()
        return self.content
    
    def start(self):
        """
            Record Start time
        """
        self.started = timer()
        self.write('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    
    def end(self):
        """
            Record End time
        """
        try:
            os.remove(f'.{self.caller}')
        except os.error as er:
            print(f'Error Delete the .temp file {self.caller} with error: {er}')
            
        self.ended = timer()
        self.elapsed = self.ended - self.started
        self.write(f'{self.caller} Elapsed Time is:s {round(self.elapsed, 3)} seconds')
        self.write('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')


def check_vli(ops: dict, log_it: logging):
    vl = int(ops['--vl'])
    if vl > 5 or vl < 1:
        log_it.write(f"Unknown Verbosity level of {vl}, try actions.py -h", 0)
        quit()
    elif vl > 1:
        log_it.write(f'Verbosity level is set to: {vl}', 2)
    return vl


'''
        All TVM-APIs Library
'''


class tvmaze_apis:
    """
    Predefined TVMaze APIs used
    """
    get_shows_by_page = 'http://api.tvmaze.com/shows?page='
    get_updated_shows = 'http://api.tvmaze.com/updates/shows'
    get_episodes_by_show_pre = 'http://api.tvmaze.com/shows/'
    get_episodes_by_show_suf = '/episodes?specials=1'
    get_episodes_status = 'https://api.tvmaze.com/v1/user/episodes'
    get_followed_shows_embed_info = 'https://api.tvmaze.com/v1/user/follows/shows?embed=show'
    update_followed_shows = 'https://api.tvmaze.com/v1/user/follows/shows'
    get_followed_shows = 'https://api.tvmaze.com/v1/user/follows/shows'
    update_episode_status = 'https://api.tvmaze.com/v1/user/episodes/'
    episode_info = 'http://api.tvmaze.com/episodes/'


def execute_tvm_request(api, req_type='get', data='', err=True, return_err=False, sleep=1.25, code=False, redirect=5,
                        timeout=(10, 5), log_ind=False, log_file='Process'):
    """
    Call TVMaze APIs

    :param api:         The TVMaze API to call
    :param data:        Some APIs (the put) can requirement data
    :param err:         If True: generates an error on any none 200 response code for the request
    :param return_err:  if True: return 'Error Code {http: response.status_code}, instead of False
    :param sleep:       Wait time between API calls [Default: 1.25 seconds]
    :param code:        Some API require a token because they are premium API
    :param req_type:    get, put, delete [Default: get]
    :param redirect:    Number of redirects allowed
    :param timeout:     Initial time-out limit and call time-out limit [Default: 10 and 5 seconds]
    :param log_ind:     Write to the log_file
    :param log_file:    Log Filename
    :return:            Resulting json if successful for get or HTTPS result or False if unsuccessful
    """
    
    time.sleep(sleep)
    session = requests.Session()
    session.max_redirects = redirect
    header_info = ''
    logfile = logging(caller='TVM Request', filename=log_file)
    if code:
        tvm_auth = get_tvmaze_info('tvm_api_auth')
        header_info = {'Authorization': tvm_auth}
    try:
        if req_type == 'get':
            if code:
                response = session.get(api,
                                       headers=header_info,
                                       timeout=timeout)
            else:
                response = session.get(api,
                                       headers={
                                           'User-Agent':
                                               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 '
                                               '(KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'},
                                       timeout=timeout)
        elif req_type == 'put':
            if code:
                response = session.put(api,
                                       headers=header_info,
                                       timeout=timeout,
                                       data=data)
            else:
                response = session.put(api, timeout=timeout)
        elif req_type == 'delete':
            if code:
                response = session.delete(api,
                                          headers=header_info,
                                          timeout=timeout)
            else:
                response = session.delete(api, timeout=timeout)
        else:
            logfile.write("Unknown Request type", 0)
            return False
    except requests.exceptions.Timeout:
        logfile.write(f'Request timed out for: {api}', 0)
        return False
    except requests.exceptions.RequestException as er:
        logfile.write(f'Request exception: {er} for: {api}, header {header_info}, code {code}, data {data}', 0)
        return False
    if response.status_code != 200:
        if err:
            logfile.write(f"Error response: {response} for api call: {api}, header {header_info}, code {code}, "
                          f"data {data}", 0)
            if return_err:
                return f'Error Code: {response.status_code}'
            else:
                return False
    if log_ind:
        logfile.write(f'API {api} with {data} Response is: {response.status_code}: {response.content}', 9)
    return response


'''
    All TVM-DB Library
'''


class config:
    def __init__(self):
        """
            Config is the routine to read 'secrets' from the configuration file so that they are never visible
            or hard-coded in the source files

        """
        secret = ''
        try:
            secret = open(f'{os.path.expanduser("~")}/.tvmaze/config', 'r')
        except IOError as err:
            print(f'TVMaze config is not found at .tvmaze/config with error {err}')
            quit()
        secrets = ast.literal_eval(secret.read())
        self.host_network = secrets['host_network']
        self.host_local = secrets['host_local']
        self.db_admin = secrets['db_admin']
        self.db_password = secrets['db_password']
        self.db_prod = secrets['db_prod']
        self.db_test = secrets['db_test']
        self.user_admin = secrets['user_admin']
        self.user_password = secrets['user_password']
        self.log_prod = secrets['prod_logs']
        self.log_test = secrets['tst_logs']
        self.log = ''
        if secrets['remote'] == 'Yes':
            self.remote = True
        else:
            self.remote = False
        self.host = ''
        self.check_host()
        self.db = ''
        self.check_db()
        secret.close()
    
    def check_host(self):
        """
            Set the db host to Network access or localhost access
        """
        check = os.getcwd()
        if 'SharedFolders' in check or self.remote:
            self.host = self.host_network
        else:
            self.host = self.host_local
    
    def check_db(self):
        """
            Set the DB to Production or Test
        """
        check = os.getcwd()
        if 'Pycharm' in check:
            self.db = self.db_test
            self.log = self.log_test
        else:
            self.db = self.db_prod
            self.log = self.log_prod


class mariaDB:
    def __init__(self, h='', d='', batch=False, caller='Lib mariaDB', filename='Process', vli=0):
        """
            mariaDB handles the DB activities for the mariadb DB of TVM-Management

        :param h:       manually assign a host
        :param d:       manually assign Production or Testing DB
        :param batch:   Default False, which mean a commit after all executes of sql with require a commit
                        True, mean that commits are postpone until a commit is trigger or when the DB is closed
        """
        self.__log = logging(caller=caller, filename=filename)
        conf = config()
        if h != '':
            self.__host = h
        else:
            self.__host = conf.host
        if vli > 2:
            self.__log.write(f'Host is setup as {self.__host}', 3)
        self.__user = conf.db_admin
        self.__password = conf.db_password
        self.__user_admin = conf.user_admin
        self.__user_password = conf.user_password
        if d != '':
            self.__db = d
        else:
            self.__db = conf.db
        self.__batch = batch
        self.__vli = vli
        
        # self.__connection = None
        # self.__cursor = None
        self.__active = False
        self.open()
        
        self.fields = []
        self.data_dict = []
    
    def open(self):
        if self.__active:
            return
        try:
            self.__connection = mariadb.connect(
                host=self.__host,
                user=self.__user,
                password=self.__password,
                database=self.__db)
        except mariadb.Error as err:
            if err:
                self.__log.write(f"Connect {self.__db}: Error connecting to MariaDB Platform: {err} "
                                 f"for host {self.__host}", 0)
                self.__log.write('--------------------------------------------------------------------------')
                sys.exit(1)
        self.__cursor = self.__connection.cursor()
        self.__active = True
    
    def close(self):
        if self.__active:
            if self.__batch:
                self.commit()
            self.__connection.close()
            self.__active = False
    
    def commit(self):
        """
            Execute a commit for outstanding transactions
        """
        if self.__active:
            self.__connection.commit()
    
    def execute_sql(self, sql='', sqltype='Fetch', data_dict=False, dd_id=False, field_list=list):
        """
                Execute SQL
        :param sql:         The SQL to execute
        :param sqltype:     Default if 'Fetch' other option is 'Commit'
        :param data_dict:   Default False, True create a dictionary out of the result of a fetch
        :param field_list:  The list of fields to be returned in the dict.  The lib will try to figure out the
                                field array itself but for joins you need the list to be passed in.
        :param dd_id:       Default False, True adds and id number for every row of data returned in the data_dict
        :return:            True, False or the result or data_dict set from a fetch
        """
        if not self.__active:
            self.open()
        sql = sql.replace("'None'", 'NULL').replace('None', 'NULL')
        if sqltype == 'Commit':
            try:
                self.__cursor.execute(sql)
                if not self.__batch:
                    self.__connection.commit()
            except mariadb.Error as er:
                self.__log.write(f'Execute SQL (Commit) Database Error: {self.__db}, {er}, {sql}', 0)
                self.__log.write('----------------------------------------------------------------------')
                return False, er
            if self.__vli > 2:
                self.__log.write(f'Executed SQL: {sql} with result {True}')
            return True
        elif sqltype == "Fetch":
            try:
                self.__cursor.execute(sql)
                result = self.__cursor.fetchall()
            except mariadb.Error as er:
                self.__log.write(f'Execute SQL (Fetch) Database Error: {self.__db}, {er}, {sql}', 0)
                self.__log.write(f'----------------------------------------------------------------------')
                return False, er
            if data_dict and len(result) > 0:
                if field_list:
                    self.fields = field_list
                else:
                    self.__extract_fields(sql)
                self.__data_as_dict(result, dd_id)
                if self.__vli > 2:
                    self.__log.write(f'Executed SQL: {sql} with DD -> {len(result)}')
                return self.data_dict
            else:
                if self.__vli > 2:
                    self.__log.write(f'Executed SQL: {sql} with -> {len(result)}')
                return result
        else:
            return False, 'Not implemented yet'
    
    def __extract_fields(self, sql):
        """
            Extract the fields from the sql
        :param sql:     The sql
        :return:        List of Fields (also self.fields)
        """
        sr = sql.lower().replace('select ', '').replace("`", "")
        sp = sr.lower().split(' from')[0]
        st = ''
        if sp == '*':
            sf = sql.lower().split('from ')
            if len(sf) == 2:
                st = str(sf[1]).lower()
            fields_sql = f"SHOW COLUMNS FROM {st}"
            self.__cursor.execute(fields_sql)
            columns = self.__cursor.fetchall()
            self.fields = []
            for column in columns:
                self.fields.append(column[0])
            return self.fields
        else:
            fields = sp.split(", ")
            for field in fields:
                self.fields.append(field)
            return self.fields
    
    def __data_as_dict(self, result, idx_id=False):
        """
            Returns the data as a dictionary (with or without and index in front of every row
        :param  result:     The Data to be processed
        :param  idx_id:     Default False, otherwise it adds and numbered ID to the dict
        :return:
        """
        if len(self.fields) != len(result[0]):
            self.__log.write(f'The length {len(self.fields)} of the data array does not match '
                             f'the length {len(result)} of the field array', 0)
            self.data_dict = []
            return
        response = ''
        id_idx = 1
        for rec in result:
            if idx_id:
                row = "{" + f'''"id": "{id_idx}", '''
                id_idx += 1
            else:
                row = "{"
            f_idx = 0
            for field in self.fields:
                row += f'''"{field}": "{str(rec[f_idx]).replace('"', '~~')}", '''
                f_idx += 1
            response = response + row[:-2] + "},"
        response = "[" + response[:-1] + "]"
        self.data_dict = ast.literal_eval(response)
        return


class mdbi:
    def __init__(self, h, d):
        config_info = config()
        if h == '':
            self.host = config_info.host
        else:
            self.host = h
        self.user = config_info.db_admin
        self.password = config_info.db_password
        if d == '':
            self.db = config_info.db
        else:
            self.db = d
        self.admin = config_info.user_admin
        self.admin_password = config_info.user_password


class sdb_info:
    check = os.getcwd()
    data = '/Users/dick/Library/Application Support/Plex Media Server/Plug-in Support/Databases/' \
           'com.plexapp.plugins.library.db'


def connect_sdb():
    sdb = sqlite3.connect(sdb_info.data)
    scur = sdb.cursor()
    sdict = {'sdb': sdb,
             'scursor': scur}
    return sdict


def close_sdb(sdb):
    sdb.close()


def execute_sqlite(sqltype='', sql=''):
    log_sqllite = logging(caller='Lib execute_sqlite', filename='Process')
    sdb = connect_sdb()
    sdbcur = sdb['scursor']
    sdbdb = sdb['sdb']
    if sqltype == 'Commit':
        try:
            sdbcur.execute(sql)
            sdbdb.commit()
        except sqlite3.Error as er:
            log_sqllite.write(f'Commit Database Error: {er}, {sql}')
            log_sqllite.write('----------------------------------------------------------------------')
            close_sdb(sdbdb)
            return False, er
        close_sdb(sdbdb)
        return True
    elif sqltype == "Fetch":
        try:
            sdbcur.execute(sql)
            result = sdbcur.fetchall()
        except sqlite3.Error as er:
            log_sqllite.write(f'Fetch Database Error: {er}, {sql}')
            log_sqllite.write('----------------------------------------------------------------------')
            close_sdb(sdbdb)
            return False, er
        close_sdb(sdbdb)
        return result
    else:
        return False, 'Not implemented yet'
   

def tables(db, tbl=''):
    if tbl == '':
        return f"select distinct table_name from information_schema.columns " \
               f"where table_schema = '{db}' order by table_name;"
    else:
        return f"select column_name, ordinal_position from information_schema.columns " \
               f"where table_schema = '{db}' and table_name = '{tbl}';"


class db_schema:
    def __init__(self, database='', table=''):
        self.databases = f"show databases"
        self.tables = f"show tables from {database}"
        self.columns = f"show columns from {table}"


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
                            "(status = 'Undecided' and record_updated >= tvmaze_upd_date) " \
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
    db = mariaDB()
    sql = f"SELECT info from key_values WHERE `key` = '{key}' "
    result = db.execute_sql(sqltype='Fetch', sql=sql)
    if not result:
        return False
    else:
        info = result[0][0]
    return info


'''
def find_new_shows():
    db = mariaDB()
    info = db.execute_sql(sqltype='Fetch', sql=tvm_views.shows_to_review)
    return info



def get_download_options(html=False):
    db = mariaDB()
    if not html:
        download_options = db.execute_sql(sqltype='Fetch', sql="SELECT * from download_options ")
    else:
        download_options = db.execute_sql(sqltype='Fetch', sql="SELECT * from download_options "
                                                               "where link_prefix like 'http%' ")
    return download_options


class num_list:
    new_list = find_new_shows()
    num_newshows = len(new_list)
'''


class shows:
    field_list = [
        'showid',
        'showname',
        'url',
        'type',
        'showstatus',
        'premiered',
        'language',
        'runtime',
        'network',
        'country',
        'tvrage',
        'thetvdb',
        'imdb',
        'tvmaze_updated',
        'tvmaze_upd_date',
        'status',
        'download',
        'record_updated',
        'alt_showname',
        'alt_sn_override',
        'eps_count',
        'eps_updated'
    ]
    
    
'''  TVM-DPG Library  '''


def window_crud_maintenance(sender, data):
    log_info(f'Function: CRUD Maintenance Window, {sender}, {data}')
    if does_item_exist(f'{data}##window'):
        log_info(f'Already exist {data}##window')
        pass
    else:
        if data == 'Key Values':
            table_headers = ['Key', 'Value', 'Comment']
        elif data == 'Plex Shows':
            table_headers = ['Show Name', 'Show Id', 'Cleaned Show Name']
        elif data == 'Plex Episodes':
            table_headers = ['Show Name', 'Season', 'Episode', 'Date Watched', 'TVM Updated', 'TVM Update Status']
        else:
            table_headers = ['Unknown']
        with window(name=f'{data}##window', width=2130, height=650, x_pos=5, y_pos=45):
            add_input_text(name=f'{data}_input', no_spaces=True, multiline=False, decimal=False, label=data, width=200)
            add_same_line(spacing=10)
            add_button(name=f'Search##{data}', callback=func_crud_search, callback_data=data)
            if data == 'Key Values' or data == 'Plex Shows':
                add_same_line(spacing=10)
                add_button(name=f"Add New##{data}")
            add_same_line(spacing=10)
            add_button(name=f"Edit##{data}")
            if data == 'Key Values':
                add_same_line(spacing=10)
                add_button(name=f"Delete##{data}")
            add_same_line(spacing=10)
            add_button(name=f"Clear##{data}", callback=func_crud_clear, callback_data=f'Table##{data}')
            add_separator(name=f'##{data}SEP1')
            add_table(name=f'Table##{data}', headers=table_headers)
            add_separator(name=f'##{data}SEP1')


def func_crud_add(sender, data):
    log_info(f'Add CRUD {sender}, {data}')
    pass


def func_crud_clear(sender, data):
    log_info(f'Emptying Table {sender}, {data}')
    func_fill_a_table(data, [])


def func_crud_edit(sender, data):
    log_info(f'Edit CRUD {sender}, {data}')
    pass


def func_crud_delete(sender, data):
    log_info(f'DELETE CRUD {sender}, {data}')
    pass


def func_crud_search(sender, data):
    db = mariaDB()
    log_info(f'Searching CRUD {sender}, {data}')
    key = get_value(f'{data}_input')
    if data == 'Key Values':
        sql = f"select * from key_values where `key` like '%{key}%' order by `key`"
    elif data == 'Plex Shows':
        sql = f"select * from TVMazeDB.plex_shows where showname like '%{key}%' " \
              f"order by `showid`, 'cleaned_showname'"
    elif data == 'Plex Episodes':
        sql = f"select * from TVMazeDB.plex_episodes where showname like '%{key}%' " \
              f"order by `showname`, 'season', `episode`"
    else:
        sql = f'Should not happen, sql is ""'
    
    result = db.execute_sql(sqltype='Fetch', sql=sql)
    func_fill_a_table(f'Table##{data}', result)


def func_fill_a_table(table_name, data):
    table = []
    for rec in data:
        table_row = []
        for field in rec:
            table_row.append(str(field).replace('None', ''))
        table.append(table_row)
    set_table_data(table_name, table)


'''  TVM-Functions Library  '''

# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText


def get_today(tp='human', fmt='full'):
    """
    Function to get today in human or epoch form.

    :param tp:      'human' or 'system' are the options
    :param fmt:     for 'human' -> 'full' return the full datetime.now otherwise only the date portion
    :return:        false if the tp param is not 'human' or 'system'
    """
    now = datetime.now()
    if tp == 'human':
        if fmt == 'full':
            return now
        else:
            return str(now)[:10]
    elif tp == 'system':
        return time.mktime(now.timetuple())
    else:
        return False


def date_delta(d='Now', delta=0):
    """
            Function to get a date back with plus or minus a number of date.
            If 'Now' today's date is the basis, otherwise you have to feed in 'yyyy-mm-dd'

    :param d:       'now' or date
    :param delta:   plus or minus integer in days
    :return:        'yyyy-mm-dd'
    """
    if d == 'Now':
        dn = date.today()
    else:
        if type(d) is datetime:
            dn = d
        else:
            dn = date(int(d[:4]), int(d[5:7]), int(d[8:]))
    nd = dn + timedelta(days=delta)
    return str(nd)[:10]


'''
def send_txt_message(message):
    email = get_tvmaze_info('email')
    pas = get_tvmaze_info('emailpas')
    sms_gateway = get_tvmaze_info('sms')
    # The server we use to send emails in our case it will be gmail but every email provider has a different smtp
    # and port is also provided by the email provider.
    smtp = "smtp.gmail.com"
    port = 587
    server = smtplib.SMTP(smtp, port)
    server.starttls()
    server.login(email, pas)
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = sms_gateway
    msg['Subject'] = "TVMaze Show Download Notification\n"
    body = message
    msg.attach(MIMEText(body, 'plain'))
    sms = msg.as_string()
    server.sendmail(email, sms_gateway, sms)
    server.quit()
'''


def eliminate_prefixes(name):
    """
                Function to eliminate show and movie prefixes from the name.
                Prefixes are retrieved from the key-values table
    :param name:  Full name to be cleaned up
    :return:    cleaned name without any prefixes
    """
    db = mariaDB()
    plexprefs = db.execute_sql(sqltype='Fetch', sql="SELECT info FROM key_values WHERE `key` = 'plexprefs'")[0]
    plexprefs = str(plexprefs).replace('(', '').replace(')', '').replace("'", "").split(',')
    for plexpref in plexprefs:
        if plexpref in name:
            name_no_pref = name.replace(plexpref, '')
            return name_no_pref
    return name


'''
def determine_directory(name):
    """
                    Function to determine if a name indicate a directory or an individual file
    :param name:    Full name of the directory or file
    :return:        Bool True is directory, File is False
    """
    db = mariaDB()
    plexexts = db.execute_sql(sqltype='Fetch', sql="SELECT info FROM key_values WHERE `key` = 'plexexts'")[0]
    plexexts = str(plexexts).replace('(', '').replace(')', '').replace("'", "").split(',')
    for plexext in plexexts:
        if plexext in name:
            return False
        return True
'''


def fix_showname(sn):
    """
    Function to make the actual showname into a showname without special characters and suffixes

    :param sn:  showname to be transformed
    :return:    transformed (cleaned up) showname (used for searching for show names)
    """
    sn = sn.replace(" : ", " ").replace("vs.", "vs").replace("'", "").replace(":", '').replace("&", "and")
    sn = sn.replace('"', '').replace(",", "")
    if sn[-1:] == " ":
        sn = sn[:-1]
    lsix = sn[-6:]
    if lsix[0] == "(" and lsix[5] == ")":
        sn = sn[:-7]
    lfour = sn[-4:]
    if lfour.lower() == "(us)":
        sn = sn[:-5]
    if lfour.isnumeric():
        sn = sn[:-5]
    ltree = sn[-3:]
    if ltree.lower() == " us":
        sn = sn[:-3]
    sn = sn.strip()
    return sn


def process_download_name(download_name):
    """
    Function to extract real showname

    :param download_name:   The transmission directory or file name
    :return:                The real showname, the showid and the season, episode and episodeid
                                or if it is considered a movie (Dict)
    """
    without_prefix = eliminate_prefixes(download_name)
    result = is_download_name_tvshow(without_prefix)
    if not result['is_tvshow']:
        data = {'is_tvshow': False,
                'showid': 0,
                'real_showname': '',
                'season': 0,
                'episode': 0,
                'episodeid': 0,
                'whole_season': False}
    else:
        end_of_showname = result['span'][0]
        raw_showname = without_prefix[:end_of_showname]
        raw_season_episode = result['match']
        clean_showname = fix_showname(str(raw_showname).replace('.', ' '))
        showinfo = get_showid(clean_showname)
        if showinfo['showid'] == 0 or showinfo['showid'] == 99999999:
            data = {'is_tvshow': True,
                    'showid': 0,
                    'real_showname': '',
                    'season': 0,
                    'episode': 0,
                    'episodeid': 0,
                    'whole_season': result['whole_season']}
        else:
            if not result['whole_season']:
                split = raw_season_episode.lower().split('e')
                season = int(split[0].lower().replace('s', ''))
                episode = int(split[1])
                episodeid = get_episodeid(showinfo['showid'], season, episode)
                data = {'is_tvshow': True,
                        'showid': showinfo['showid'],
                        'real_showname': showinfo['real_showname'],
                        'season': season,
                        'episode': episode,
                        'episodeid': episodeid,
                        'whole_season': result['whole_season']}
            else:
                season = raw_season_episode.lower()
                episode = ''
                episodeid = ''
                data = {'is_tvshow': True,
                        'showid': showinfo['showid'],
                        'real_showname': showinfo['real_showname'],
                        'season': season,
                        'episode': episode,
                        'episodeid': episodeid,
                        'whole_season': result['whole_season']}
    
    return data


def get_showid(clean_showname):
    db = mariaDB()
    logfile = logging(caller='Get Show Id', filename='Process')
    sql = f'select showid, showname from shows where alt_showname = "{clean_showname}" ' \
          f'and status = "Followed" and download != "Skip"'
    result = db.execute_sql(sqltype='Fetch', sql=sql)
    if len(result) > 1:
        logfile.write(f'Something is up, too many shows found {result}', 0)
        return {'showid': 99999999, 'real_showname': 'Too Many Shows Found'}
    elif len(result) == 0:
        logfile.write(f'Something is up, no show found {result}', 0)
        return {'showid': 0, 'real_showname': 'No ShowFound'}
    else:
        showid = result[0][0]
        showname = str(result[0][1]).replace(':', '')
        return {'showid': showid, 'real_showname': showname}


def get_episodeid(showid, season, episode):
    db = mariaDB()
    logfile = logging(caller='Get Episode Id', filename='Process')
    sql = f'select epiid from episodes where showid = {showid} and season = {season} and episode = {episode}'
    result = db.execute_sql(sqltype='Fetch', sql=sql)
    if len(result) != 1:
        logfile.write(f'Something is up, either too many episodes found or no episode found {result}', 0)
        episodeid = 0
    else:
        episodeid = result[0][0]
    return episodeid


def is_download_name_tvshow(download_name):
    reg_exs = ['s[0-9][0-9]e[0-9][0-9]',
               's[0-9][0-9]',
               'season[ .][0-9]',
               's[0-9]e[0-9]',
               'season[ .][0-9][0-9]']
    for reg_ex in reg_exs:
        result = re.search(reg_ex, download_name.lower())
        if result:
            span = result.span()
            match = str(result.group()).replace('.', '')
            if len(match) < 4 or 'season' in match:
                whole_season = True
            else:
                whole_season = False
            return {'is_tvshow': True, 'match': match, 'span': span, 'whole_season': whole_season}
    return {'is_tvshow': False, 'match': '', 'span': (0, 0), 'whole_season': False}


class paths:
    def __init__(self, mode='Prod'):
        sp = get_tvmaze_info('path_scripts')
        if mode == 'Prod':
            lp = get_tvmaze_info('path_prod_logs')
            ap = get_tvmaze_info('path_prod_apps')
        else:
            lp = get_tvmaze_info('path_tst_logs')
            ap = get_tvmaze_info('path_tst_apps')
        self.log_path = lp
        self.app_path = ap
        self.scr_path = sp
        self.process = f'{lp}Process.log'
        self.transmission = f'{lp}Transmission.log'


def convert_to_dict_within_list(data, data_type='DB', field_list=None):
    response = ''
    if not field_list:
        field_list = []
    if data_type == 'DB' and len(data) != 0 and len(field_list) == len(data[0]):
        for rec in data:
            row = "{"
            f_idx = 0
            for field in rec:
                row += f'''"{field_list[f_idx]}": "{str(field).replace('"', '~~')}", '''
                f_idx += 1
            response = response + row[:-2] + "},"
        response = "[" + response[:-1] + "]"
    else:
        return {}
    return response

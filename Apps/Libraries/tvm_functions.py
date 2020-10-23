# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
from datetime import datetime, timedelta, date
import time
import os
import re


from Libraries.tvm_db import execute_sql, get_tvmaze_info


class release:
    # Obsolete now - only used in the console app
    console_version = 'Version: In Development - V2.0 - Oct 7 at 11:00:00 AM'
    console_description = "TVMaze Management system"
    

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


def eliminate_prefixes(sn):
    """
                Function to eliminate show and movie prefixes from the name.
                Prefixes are retrieved from the key-values table
    :param sn:  Full name to be cleaned up
    :return:    cleaned name without any prefixes
    """
    plexprefs = execute_sql(sqltype='Fetch', sql="SELECT info FROM key_values WHERE `key` = 'plexprefs'")[0]
    plexprefs = str(plexprefs).replace('(', '').replace(')', '').replace("'", "")
    plexprefs = str(plexprefs).split(',')
    for pp in plexprefs:
        pp = pp + '.'
        if pp in sn:
            csn = sn.replace(pp, '')
            return csn
            

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
                'episodeid': 0}
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
                    'episodeid': 0}
        else:
            split = raw_season_episode.lower().split('e')
            season = int(split[0].lower().replace('s', ''))
            episode = int(split[1])
            episodeid = get_episodeid(showinfo['showid'], season, episode)
            data = {'is_tvshow': True,
                    'showid': showinfo['showid'],
                    'real_showname': showinfo['real_showname'],
                    'season': season,
                    'episode': episode,
                    'episodeid': episodeid}
    return data


def get_showid(clean_showname):
    sql = f'select showid, showname from shows where alt_showname = "{clean_showname}" and status = "Followed"'
    result = execute_sql(sqltype='Fetch', sql=sql)
    if len(result) > 1:
        print(f'Something is up, too many shows found', result)
        return {'showid': 99999999, 'real_showname': 'Too Many Shows Found'}
    elif len(result) == 0:
        print(f'Something is up, no show found', result)
        return {'showid': 0, 'real_showname': 'No ShowFound'}
    else:
        showid = result[0][0]
        showname = result[0][1]
        return {'showid': showid, 'real_showname': showname}


def get_episodeid(showid, season, episode):
    sql = f'select epiid from episodes where showid = {showid} and season = {season} and episode = {episode}'
    result = execute_sql(sqltype='Fetch', sql=sql)
    if len(result) != 1:
        print(f'Something is up, either too many episodes found or no episode found', result)
        episodeid = 0
    else:
        episodeid = result[0][0]
    return episodeid


def is_download_name_tvshow(download_name):
    reg_exs = ['.[Ss][0-9][Ee][0-9].',
               '.[Ss][0-9][0-9][Ee][0-9][0-9].',
               '.[Ss][0-9][0-9][0-9][Ee][0-9][0-9][0-9].']
    for reg_ex in reg_exs:
        result = re.search(reg_ex, download_name)
        if result:
            span = result.span()
            match = str(result.group()).replace('.', '')
            return {'is_tvshow': True, 'match': match, 'span': span}
    return {'is_tvshow': False, 'match': '', 'span': (0, 0)}


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
        self.console = lp + 'TVMaze.log'
        self.errors = lp + 'Errors.log'
        self.process = lp + 'Process.log'
        self.cleanup = lp + 'Cleanup.log'
        self.watched = lp + 'Watched.log'
        self.transmission = lp + "Transmission.log"
        self.shows_update = lp + "Shows_Update.log"
        
        
class def_downloader:
    dl = execute_sql(sqltype='Fetch', sql=f'SELECT info FROM key_values WHERE `key` = "def_dl"')[0][0]


def print_tvm(mode='Test', app='', line=''):
    p_time = time.strftime("%D - %T")
    if mode == '':
        quit('Mode was empty')
    path_info = paths(mode)
    if app != '':
        p_file = open(f'{path_info.log_path + app[:-3] + ".log"}', 'a')
        p_file.write(f'{p_time} -> {app} => {line}\n')
        p_file.close()


class operational_mode:
    def __init__(self):
        check = os.getcwd()
        if 'Pycharm' in check:
            prod = False
        else:
            prod = True
        self.prod = prod


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
        print(f'No result was found')
        return {}
    return response

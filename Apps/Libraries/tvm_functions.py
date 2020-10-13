import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, date
import time
import os

from Libraries.tvm_db import execute_sql, get_tvmaze_info


class release:
    # Obsolete now - only used in the console app
    console_version = 'Version: In Development - V2.0 - Oct 7 at 11:00:00 AM'
    console_description = "TVMaze Management system"
    

def get_today(tp='human', fmt='full'):
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

def fix_showname(sn):
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

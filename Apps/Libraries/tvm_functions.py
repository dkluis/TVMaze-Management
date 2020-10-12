import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, date
import time

from Libraries.tvm_db import *


class release:
    console_version = 'Version: In Development - V2.0 - Oct 7 at 11:00:00 AM'
    console_description = "TVMaze Management system"
    
    
class paths:
    def __init__(self, mode='Prod'):
        sp = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/scripts/'
        if mode == 'Prod':
            lp = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/'
            ap = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Apps/'
        else:
            lp = '/Volumes/HD-Data-CA-Server/Development/PycharmProjects/TVM-Management/Logs/'
            ap = '/Volumes/HD-Data-CA-Server/Development/PycharmProjects/TVM-Management/Apps/'
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
    dl = 'Multi'


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


def send_txt_message(message):
    # email = "dickkluis@gmail.com"
    email = get_tvmaze_info('email')
    # pas = "iu4exCvsNKbzTNDQyGYcutQs"
    pas = get_tvmaze_info('emailpas')
    # sms_gateway = '8138189195@tmomail.net'
    sms_gateway = get_tvmaze_info('sms')
    # The server we use to send emails in our case it will be gmail but every email provider has a different smtp
    # and port is also provided by the email provider.
    smtp = "smtp.gmail.com"
    port = 587
    # This will start our email server
    server = smtplib.SMTP(smtp, port)
    # Starting the server
    server.starttls()
    # Now we need to login
    server.login(email, pas)
    # Now we use the MIME module to structure our message.
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = sms_gateway
    # Make sure you add a new line in the subject
    msg['Subject'] = "TVMaze Show Download Notification\n"
    # Make sure you also add new lines to your body
    body = message
    # and then attach that body furthermore you can also send html content.
    msg.attach(MIMEText(body, 'plain'))
    sms = msg.as_string()
    server.sendmail(email, sms_gateway, sms)
    # lastly quit the server
    server.quit()


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


'''
class dir_paths:
    base_path = execute_sql(sqltype='Fetch', sql=f'SELECT info FROM key_values WHERE `key` = "base_path"')[0]
    process = execute_sql(sqltype='Fetch', sql=f'SELECT info FROM key_values WHERE `key` = "process"')[0]
    transmission = execute_sql(sqltype='Fetch', sql=f'SELECT info FROM key_values WHERE `key` = "transmission"')[0]
'''

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, date

from db_lib import *


class release:
    console_version = 'Version: In Development - V2.0 - Oct 7 at 11:00:00 AM'
    console_description = "TVMaze Management system"
    

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

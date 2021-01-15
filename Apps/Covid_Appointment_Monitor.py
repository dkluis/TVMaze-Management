from bs4 import BeautifulSoup as Soup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from Libraries import execute_tvm_request, logging
from Libraries import get_tvmaze_info


def read_publix_availability():
    availability_link = "https://www.publix.com/covid-vaccine/florida"
    availability_request = execute_tvm_request(api=availability_link, req_type='get')
    if availability_request:
        availability_html = Soup(availability_request.content, 'html.parser')
    else:
        log.write(f'Web Request Failed ###############################################################################')
        exit(99)

    availability_first_tbody = availability_html.find('tbody')
    availability_counties = availability_first_tbody.findAll('td')
    idx = 0
    while idx < len(availability_counties):
        for county in counties:
            if county in availability_counties[idx]:
                availability = str(availability_counties[idx + 1]).replace('<td>', '').replace('</td>', '')
                message = f'Publix Tracker: County {county} availability is {availability}'
                log.write(message)
                if availability != 'Fully Booked':
                    log.write(f'Not Fully Booked >>>>>>>>>>>>>{county}>>>>>>>>>>>>>>>>>>>>>{availability}>>>>>>>>>>>>>')
                    text_message(message)
        idx += 1
        

def text_message(message):
    email = get_tvmaze_info('email')
    pas = get_tvmaze_info('emailpas')
    sms_gateway = get_tvmaze_info('sms')
    smtp = "smtp.gmail.com"
    port = 587
    server = smtplib.SMTP(smtp, port)
    server.starttls()
    server.login(email, pas)
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = sms_gateway
    msg['Subject'] = "Covid Vaccine Availability"
    body = message
    msg.attach(MIMEText(body, 'plain'))
    sms = msg.as_string()
    server.sendmail(email, sms_gateway, sms)
    server.quit()


'''Main Program'''
log = logging(caller='Covid Vaccine Availability', filename='Covid_Availability_Monitor')
log.start()
counties = ['Citrus', 'Hernando', 'Marion']
read_publix_availability()
log.end()

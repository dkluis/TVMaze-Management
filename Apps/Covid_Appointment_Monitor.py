import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from Libraries import execute_tvm_request, logging
from Libraries import get_tvmaze_info


def read_publix_availability():
    availability_link = "https://www.publix.com/covid-vaccine/florida/florida-county-status.txt"
    availability_request = execute_tvm_request(api=availability_link, req_type='get')
    if availability_request:
        availability_counties = str(availability_request.content).split('\\r\\n')
    else:
        log.write(f'Web Request Failed ###############################################################################')
        exit(99)
        
    for county_info in availability_counties:
        county_info = county_info.replace("b'", "")
        split_county_info = county_info.split('|')
        county = split_county_info[0]
        availability = split_county_info[1]
        for check_county in counties:
            if county == check_county:
                message = f'Publix Tracker: County {county} availability is {availability}'
                log.write(message)
                if availability != 'Fully Booked' and availability != 'Coming Soon':
                    log.write(f'Not Fully Booked >>>>>>>>>>>>>{county}>>>>>>>>>>>>>>>>>>>>>{availability}>>>>>>>>>>>>>')
                    text_message(message)
        

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
counties = ['Citrus', 'Hernando', 'Marion', 'Pinellas', 'Manatee', 'Hillsborough', 'Polk', 'Hardee', 'Sarasota']
read_publix_availability()
log.end()

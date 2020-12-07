import time
import requests
from datetime import date

from Libraries.tvm_db import get_tvmaze_info
from Libraries.tvm_logging import logging


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


def execute_tvm_request(api, req_type='get', data='', err=True, return_err=False, sleep=1.25, code=False, redirect=5,
                        timeout=(10, 5), log=False):
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
    :param log:      Write to the log_file
    :return:            Resulting json if successful for get or HTTPS result or False if unsuccessful
    """
    
    time.sleep(sleep)
    session = requests.Session()
    session.max_redirects = redirect
    header_info = ''
    logfile = logging(caller='TVM Request', filename='Process')
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
    if log:
        logfile.write(f'API {api} with {data} Response is: {response.status_code}: {response.content}', 9)
    return response


def update_tvmaze_episode_status(epiid, status=1, upd_date=None, log_it=False):
    """
                     Go Update TVMaze that the show is
                     
    :param epiid:    Episode ID
    :param status:   Type of update: 0 = Watched, 1 = Acquired, 2 = Skipped
    :param upd_date: The date (human readable) to update the episode with
    :param log_it:   Tell the API to log the response
    :return:         HTML response
    """
    baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(epiid)
    if not upd_date:
        epoch_date = int(date.today().strftime("%s"))
    else:
        epoch_date = int(upd_date.strftime('%s'))
    data = str({"marked_at": epoch_date, "type": status})
    response = execute_tvm_request(baseurl, data=data, req_type='put', code=True, log=log_it)
    return response

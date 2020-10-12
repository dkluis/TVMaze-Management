import requests
import time


class tvm_apis:
    shows_by_page = 'http://api.tvmaze.com/shows?page='
    updated_shows = 'http://api.tvmaze.com/updates/shows'
    episodes_by_show_pre = 'http://api.tvmaze.com/shows/'  # + str(showid)
    episodes_by_show_suf = '/episodes?specials=1'
    episodes_status = 'https://api.tvmaze.com/v1/user/episodes'
    followed_shows_embed_info = 'https://api.tvmaze.com/v1/user/follows/shows?embed=show'
    followed_shows = 'https://api.tvmaze.com/v1/user/follows/shows'
    secret = {'Authorization: Basic RGlja0tsdWlzOlRUSFlfQ2hIeUF5SU1fV1ZZRmUwcDhrWTkxTkE1WUNH'}
    update_episode_status = 'https://api.tvmaze.com/v1/user/episodes/'


def execute_tvm_request(api, data='', err=True, sleep=1.25, code=False,
                        req_type='get', redirect=5, timeout=(10, 5)):
    time.sleep(sleep)
    session = requests.Session()
    session.max_redirects = redirect
    try:
        if req_type == 'get':
            if code:
                response = session.get(api,
                                       headers={
                                           'Authorization':
                                               'Basic RGlja0tsdWlzOlRUSFlfQ2hIeUF5SU1fV1ZZRmUwcDhrWTkxTkE1WUNH'},
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
                                       headers={
                                           'Authorization':
                                               'Basic RGlja0tsdWlzOlRUSFlfQ2hIeUF5SU1fV1ZZRmUwcDhrWTkxTkE1WUNH'},
                                       timeout=timeout,
                                       data=data)
            else:
                response = session.put(api, timeout=timeout)
        elif req_type == 'delete':
            if code:
                response = session.delete(api,
                                          headers={
                                              'Authorization':
                                                  'Basic RGlja0tsdWlzOlRUSFlfQ2hIeUF5SU1fV1ZZRmUwcDhrWTkxTkE1WUNH'},
                                          timeout=timeout)
            else:
                response = session.delete(api, timeout=timeout)
        else:
            print("Unknown Request type", flush=True)
            return False
    except requests.exceptions.Timeout:
        print(f'Request timed out for: {api}', flush=True)
        return False
    except requests.exceptions.RequestException as er:
        print(f'Request exception: {er} for: {api}', flush=True)
        return False
    if response.status_code != 200:
        if err:
            print(f"Error response: {response} for api call: {api}", flush=True)
            return False
    return response

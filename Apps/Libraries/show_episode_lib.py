from Libraries import mariaDB, fix_showname, tvmaze_apis, execute_tvm_request
from dateutil.parser import parse
import datetime


def find_show_via_name_and_episode(raw_show_name: str, season: int, epi_num: int, reason: str,
                                   update_tvm: bool = False,
                                   update_date: datetime = None):
    """
    Find the episode id (TVMaze) of a show, season, number
        Optionally update TVMaze with a status (reason) and reason date.
        Skipped, Downloaded, Watched
    
    :param raw_show_name:       Showname
    :param season:              Season
    :param epi_num:             Number
    :param reason:              Reason
    :param update_tvm:          Update True/False
    :param update_date:         yyyy-mm-dd
    :return:                    Tuple(Tuple)
                                ((Found the show: True/False
                                 List of Episodes[(Showid, Epiid, TVMaze status, TVMaze date])
                                Update Response Code)
    """
    show_name = fix_showname(raw_show_name)
    epis_found = find_show_id(show_name, season, epi_num)
    epis_determined = determine_which_episode(epis_found, reason)
    updated = False
    print(epis_determined)
    
    if update_tvm:
        found = epis_determined[0]
        epis = epis_determined[1]

        if found and len(epis) == 0:
            print('Found the epi but nothing to update')
        elif found and len(epis) > 1:
            print(f'Found {len(epis)} episodes, could not determine which one')
        elif found:
            print(f'Found the epi to update {epis[0][1]}, {epis[0][3]}')
            updated = update_tvm_epis(epis, reason, update_date)
        else:
            print('Episode was not found')
    
    return epis_determined, updated


def find_show_id(show_name: str, season: int, epi_num: int):
    db = mariaDB()
    sql = f'select showid, showname, alt_showname, status, showstatus, premiered from shows ' \
          f'where (showname = "{show_name}" or alt_showname = "{show_name}") and status = "Followed" ' \
          f'and download != "Skip" ' \
          f'order by showname, showid'
    all_shows = db.execute_sql(sql=sql)
    
    found_epis = []
    for show in all_shows:
        show_id = show[0]
        sql = f'select epiid, mystatus, airdate from episodes where showid = {show_id} and season = {season} ' \
              f'and episode = {epi_num}'
        epi = db.execute_sql(sql=sql)
        if len(epi) == 1:
            found_epis.append((show_id, epi[0][0], epi[0][1], epi[0][2]))

    return found_epis


def determine_which_episode(epis_found: list, reason: str):
    epis_det_download = []
    epis_determined = []
    if len(epis_found) == 0:
        return False, []
    
    for epi in epis_found:
        if not epi[2]:
            epis_det_download.append(epi)
        elif epi[2] == 'Watched' or epi[2] == 'Skipped':
            pass
        elif epi[2] == reason:
            pass
        else:
            epis_det_download.append(epi)

    if len(epis_det_download) > 1:
        for epi in epis_det_download:
            delta = (parse(str(epi[3])) - parse(datetime.datetime.today().strftime('%Y-%m-%d')))
            days = abs(int(str(delta).split(' days')[0]))
            if days < 730:
                epis_determined.append(epi)
            else:
                print('Rejected due to number of days difference', epi)
    else:
        epis_determined = epis_det_download
            
    return True, epis_determined


def update_tvm_epis(epis_to_update: list, reason: str, upd_date: datetime):
    if reason == 'Downloaded':
        tvm_type = 1
    elif reason == 'Watched':
        tvm_type = 0
    else:
        tvm_type = 2
    epiid = epis_to_update[0][1]
    baseurl = f'{tvmaze_apis.get_episodes_status}/{str(epiid)}'
    if upd_date != '':
        epoch_date = int(datetime.datetime.strptime(upd_date, '%Y-%m-%d').strftime("%s"))
    else:
        epoch_date = int(datetime.datetime.today().strftime("%s"))
    data = {"marked_at": epoch_date, "type": tvm_type}
    response = execute_tvm_request(baseurl, data=data, req_type='put', code=True)
    return response

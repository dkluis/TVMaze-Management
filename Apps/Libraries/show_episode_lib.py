from Libraries import mariaDB, fix_showname
from dateutil.parser import parse
import datetime


def find_show_via_name_and_episode(raw_show_name: str, season: int, epi_num: int, reason: str):
    show_name = fix_showname(raw_show_name)
    epis_found = find_show_id(show_name, season, epi_num)
    epis_determined = determine_which_episode(epis_found, reason)
    return epis_determined


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

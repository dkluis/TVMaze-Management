from Libraries import determine_directory, process_download_name
from Libraries import execute_sql
from Libraries import logging


def transform_season_string(season_in):
    if isinstance(season_in, int):
        return season_in
    if 'season' in str(season_in).lower():
        return int(str(season_in).lower().split('season')[1].replace(' ', ''))
    if 's' in str(season_in).lower():
        return int(str(season_in).lower().split('s')[1].replace(' ', ''))
    log.write(f'Should not happen {season_in}', 99)


def update_tvmaze_with_downloaded_episodes(epis):
    for epi in epis:
        log.write(f'Updating episode: {epi}')
    return


def move_to_plex(tv_show, file_name, direct, name, season):
    log.write(f'Moving to plex {file_name} and it is a directory: {direct} and it is tv-show: {tv_show}')
    return


'''
        Main Program
'''

log = logging(caller='Tor Decifering', filename='Tor Decifering')
log.start()

input_file = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/Transmissions_Processed.log'
tors = open(input_file, 'r')
recs = tors.readlines()
for rec in recs:
    seas = 0
    full_tor_name = rec.split(' > ')[1][:-1]
    directory = determine_directory(full_tor_name)
    processed_info = process_download_name(full_tor_name)
    if processed_info['is_tvshow']:
        all_episodes = []
        if not processed_info['whole_season']:
            all_episodes.append(processed_info['episodeid'])
        else:
            seas = transform_season_string(processed_info['season'])
            sql = f'select epiid from episodes where showid = {processed_info["showid"]} and ' \
                  f'season = {seas}'
            episodes = execute_sql(sql=sql, sqltype='Fetch')
            if len(episodes) != 0:
                for episode in episodes:
                    all_episodes.append(episode[0])
        log.write(f'Processing TV Show {processed_info["real_showname"]} with {len(all_episodes)} episodes')
        move_to_plex(True, full_tor_name, directory, processed_info['real_showname'], seas)
        update_tvmaze_with_downloaded_episodes(all_episodes)
    else:
        log.write(f'Processing Movie {full_tor_name}')
        move_to_plex(False, full_tor_name, directory, '', '')
        log.write(f'Processing Movie {full_tor_name}')

log.end()

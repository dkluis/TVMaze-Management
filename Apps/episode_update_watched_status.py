"""

update_pre_tvmaze_watched.eps.py  Name says it all.  It is a one-time update.

Usage:
  update_pre_tvmaze_watched.eps.py
  update_pre_tvmaze_watched.eps.py -h | --help
  update_pre_tvmaze_watched.eps.py --version

Options:
  -h --help      Show this screen
  --version      Show version.

"""

from Libraries import mariaDB, execute_tvm_request, logging, tvmaze_apis

log = logging(caller='Episodes Watched Update', filename='Episodes_Watched_Update')
log.start()
db = mariaDB(caller=log.caller, filename=log.filename)

etu_sql = "select epiid, airdate from episodes where mystatus = 'Watched' and mystatus_date is NULL"
eps_to_update = db.execute_sql(sqltype='Fetch', sql=etu_sql)
log.write(f'Number of Episodes to update: {len(eps_to_update)}')
for eptu in eps_to_update:
    baseurl = tvmaze_apis.get_episodes_status + '/' + str(eptu[0])
    # baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(eptu[0])
    if not eptu[1]:
        continue
    epoch_date = eptu[1].strftime('%s')
    if int(epoch_date) <= 0:
        continue
    data = {"marked_at": epoch_date, "type": 0}
    response = execute_tvm_request(baseurl, data=data, req_type='put', code=True)
    if response:
        log.write(f'Updated epi {eptu[0]} as watched on {eptu[1]}, with response {response}')
    else:
        log.write(f'Failed to update --------> epi {eptu[0]} as watched on {eptu[1]}')
        
db.close()
log.end()
quit()

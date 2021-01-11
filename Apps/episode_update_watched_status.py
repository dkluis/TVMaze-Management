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

from Libraries import execute_sql
from Libraries import execute_tvm_request
from Libraries import logging

log = logging(caller='Episodes Watched Update', filename='Episodes_Watched_Update')
log.start()

etu_sql = "select epiid, airdate from episodes where mystatus = 'Watched' and mystatus_date is None"
eps_to_update = execute_sql(sqltype='Fetch', sql=etu_sql.replace('None', 'NULL'))
print(f'Number of Episodes to update: {len(eps_to_update)}')
for eptu in eps_to_update:
    baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(eptu[0])
    epoch_date = eptu[1].strftime('%s')
    data = {"marked_at": epoch_date, "type": 0}
    response = execute_tvm_request(baseurl, data=data, req_type='put', code=True)
    if response:
        log.write(f'Updated epi {eptu[0]} as watched on {eptu[1]}, with response {response}')
    else:
        log.write(f'Failed to update --------> epi {eptu[0]} as watched on {eptu[1]}')
        
log.end()


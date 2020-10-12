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

from Libraries.tvm_db import execute_sql
from Libraries.tvm_apis import execute_tvm_request


etu_sql = "select epiid, airdate from episodes where mystatus = 'Watched' and mystatus_date is None"
eps_to_update = execute_sql(sqltype='Fetch', sql=etu_sql.replace('None', 'NULL'))
print(f'Number of Episodes to update: {len(eps_to_update)}')
for eptu in eps_to_update:
    # print(f'Working on {eptu[0]} with date {eptu[1]}')
    baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(eptu[0])
    epoch_date = eptu[1].strftime('%s')
    data = {"marked_at": epoch_date, "type": 0}
    response = execute_tvm_request(baseurl, data=data, req_type='put', code=True)
    if response:
        print(f'Updated epi {eptu[0]} as watched on {eptu[1]}, with response {response}')
    else:
        print(f'Failed to update --------> epi {eptu[0]} as watched on {eptu[1]}')


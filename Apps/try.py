"""

Try.py  Proof out the docopt library

Usage:
  try.py
  try.py -m <mshow> <mepisode> [-v]
  try.py [-d] [-r] [-v | --verbose] [-b [--db=<dbname>]]
  try.py -f (--show <fshow> --episode <fepisode> | <show> <episode>)
  try.py -s <sshow>...
  try.py -h | --help
  try.py --version

Options:
  -h --help      Show this screen
  --db=<dbname>  Production Schema (or not) [default: Test_TVM_DB]
  -v             Verbose Logging
  -d             Download all outstanding Episodes
  -r             Review all newly detected Shows
  -f             Find download options for Show and Episode (Episode can also be a whole season - S01E05 or S01)
  -s             Show Info (multiple shows can be requested)
  --version      Show version.

"""

from docopt import docopt

args = docopt(__doc__, version='Try Release 1.0')
print(args)
print(f'Option -d was selected {args["-d"]}')
print(f'Option -r was selected {args["-r"]}')
print(f'Option -f was selected {args["-f"]} show = {args["<fshow>"]} episode = {args["<fepisode>"]}')
print(f'Option -m was selected {args["-m"]} show = {args["<mshow>"]} episode = {args["<mepisode>"]}')
print(f'Option -s was selected {args["-s"]} list of show = {args["<sshow>"]}')
print(f'Option -b was selected {args["-b"]} DB schema to use = {args["--db"]}')
print(f'Option -v was selected {args["-v"]}')

"""
sys.stdout = open(f'try.log', 'a')

etu_sql = "select epiid, airdate from episodes where mystatus = 'Watched' and mystatus_date is None"
eps_to_update = execute_sql(sqltype='Fetch', sql=etu_sql.replace('None', 'NULL'))
# print_tvm(mode=ops, app='try.py', line=f'Number of Episodes to update: {len(eps_to_update)}')
print(f'Number of Episodes to update: {len(eps_to_update)}')
for eptu in eps_to_update:
    # print_tvm(mode=ops, app='try.py', line=f'Working on {eptu[0]} with date {eptu[1]}')
    print(f'Working on {eptu[0]} with date {eptu[1]}')
    baseurl = 'https://api.tvmaze.com/v1/user/episodes/' + str(eptu[0])
    epoch_date = eptu[1].strftime('%s')
    data = {"marked_at": epoch_date, "type": 0}
    response = execute_tvm_request(baseurl, data=data, req_type='put', code=True)

sys.stdout.close()
"""

from Libraries.tvm_logging import logging

log = logging(caller='Try out')
log1 = logging(caller='Another Try out')

print(log.content, log1.content)

log1.open('Tryout1', 'a+')
log1.write('Messagae 1')
log1.write('Messaage 2')
print('Log: ' + str(log.content) + 'Log1 :' + str(log1.content))
log.open('Tryout', 'a')
log.write('Message 1')
log.write('Message 2')
print('Log: ' + str(log.content) + 'Log1 :' + str(log1.content))
log.empty()
log.write('Message 3')
log.write('Message 4', read=True)
print('Log: ' + str(log.content) + 'Log1 :' + str(log1.content))
log.close()
log.write('Hello Again')

log1 = logging(caller='Another Try Out')
log1.open('Tryout1', 'w+')
print('Log: ' + str(log.content) + 'Log1 :' + str(log1.content))
log1.write('Messaage 3', level=5)
log1.write('Message 4')
print('Log: ' + str(log.content) + 'Log1 :' + str(log1.content))
log1.close()
log1.write('Helalo Again')

log1.read()
log.read()

print('Log: ' + str(log.content) + 'Log1 :' + str(log1.content))

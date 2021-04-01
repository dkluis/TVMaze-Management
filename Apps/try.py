from docopt import docopt
from Libraries import mariaDB, check_vli, logging
from Libraries import part
from Libraries import find_show_via_name_and_episode


result = find_show_via_name_and_episode('battlestar galactica', 1, 1, 'Watched')
found = result[0]
epis = result[1]
if found and len(epis) == 0:
    print('Found the epi but nothing to update')
elif found and len(epis) > 1:
    print(f'Found {len(epis)} episodes, could not determine which one')
elif found:
    print(f'Found the epi to update {epis[0]}')
else:
    print('Episode was not found')


'''
log = logging(caller="Try", filename='Try')

db = mariaDB()
part = part(db)
print(part.read(showid=7))
result = part.info
print(result, type(result))
'''

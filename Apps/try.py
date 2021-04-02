from docopt import docopt
from Libraries import mariaDB, check_vli, logging
from Libraries import part
from Libraries import find_show_via_name_and_episode


result = find_show_via_name_and_episode('Home', 1, 1, 'Watched', True, '2020-04-20')
print(result)



'''
log = logging(caller="Try", filename='Try')

db = mariaDB()
part = part(db)
print(part.read(showid=7))
result = part.info
print(result, type(result))
'''

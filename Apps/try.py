from docopt import docopt
from Libraries import mariaDB, check_vli, logging
from Libraries import part

log = logging(caller="Try", filename='Try')

db = mariaDB()
part = part(db)
print(part.read(showid=7))
result = part.info
print(result, type(result))


quit()

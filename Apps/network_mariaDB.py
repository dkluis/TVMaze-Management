import mariadb
import sys

try:
    mdb = mariadb.connect(
        host='192.168.42.68',
        user='dick',
        password='Sandy3942',
        database='TVMazeDB')
except mariadb.Error as err:
    if err:
        print(f"Connect MDB: Error connecting to MariaDB Platform: {err}", flush=True)
        print('--------------------------------------------------------------------------', flush=True)
        sys.exit(1)

mcur = mdb.cursor()

print(mdb, mcur)
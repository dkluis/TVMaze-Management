import os

from db_lib import *
from terminal_lib import check_cli_args, term_codes


def get_cli_args():
    tlc = ["-t", "-i", "-h", '-d', '-cto']
    flc = check_cli_args(tlc)
    found = False
    for e in flc.items():
        if e[1]:
            found = True
            break
    if not found or flc['-h']:
        print(f"{term_codes.green}CLI Options are: {term_codes.red}-h{term_codes.green} (Help), "
              f"{term_codes.red}-i{term_codes.green} (Initialize from TVMaze - Fresh), "
              f"{term_codes.red}-t{term_codes.green} (Initialize from SQLite DB - 'Legacy'), "
              f"{term_codes.red}-cto{term_codes.green} (Create TVMaze Tables Only), "
              f"{term_codes.red}-d{term_codes.green} (View Data Tables & Columns)")
        print()
        quit()
    return flc


def process_create_db_tvmaze():
    print('Create db TVMaze', execute_sql(d='', sqltype='Commit', sql=create_db_sql('TVMazeDB')))
    print('Create tvmaze table', execute_sql(sqltype='Commit', sql=create_tb_tvmaze.sql))
    print('Create download_options table', execute_sql(sqltype='Commit', sql=create_tb_dls.sql))
    print('Create Shows table', execute_sql(sqltype='Commit', sql=create_tb_shows.sql))
    # print('Create Alternate Show Names table', execute_sql(sqltype='Commit', sql=create_tb_alt_showname.sql))
    print('Create Episodes table', execute_sql(sqltype='Commit', sql=create_tb_eps_by_show.sql))
    # print('Create Followed Shows table', execute_sql(sqltype='Commit', sql=create_tb_followed_shows.sql))
    print('Create Statistics table', execute_sql(sqltype='Commit', sql=create_tb_statistics.sql))


def process_transfer():
    print('Checking to see if the SQLite DB exists')
    if not os.path.exists(sdb_info.data):
        print(f"{term_codes.red}SQLite database {term_codes.yellow}{sdb_info.data}{term_codes.red} does not exist")
        print(f"{term_codes.green}Update the sdb_info class in db_definitions.py")
        quit()
    
    print('Checking to see if the MariaDB exists')
    result = connect_mdb(d='TVMazeDB', err=False)
    if result:
        print(f"{term_codes.red}MariaDB is already setup with the database: {term_codes.yellow}{mdb_info.db}"
              f"{term_codes.normal} on {term_codes.yellow}{mdb_info.host}{term_codes.normal} "
              f"with user {term_codes.yellow}{mdb_info.user}{term_codes.normal}")
        print(f"{term_codes.green}Delete the DB or update mdb_info class in db_definitions.py "
              f"to create different database")
        quit()
    
    process_create_db_tvmaze()

    print('Filling the TVMaze Table')
    print(len(create_tb_tvmaze.fill))
    for sql in create_tb_tvmaze.fill:
        execute_sql(sqltype='Commit', sql=sql)

    print('Filling the download_options Table')
    print(len(create_tb_dls.fill))
    for sql in create_tb_dls.fill:
        execute_sql(sqltype='Commit', sql=sql)

    dbinfo = connect_mdb(d=mdb_info.db)
    mdb = dbinfo['mdb']
    mcur = dbinfo['mcursor']
    mdb.autocommit = False

    print('Filling the Shows Table')
    all_shows = execute_sqlite(sqltype='Fetch', sql='SELECT * from all_shows order by showid ')
    print(len(all_shows))
    recs = 0
    for rec in all_shows:
        new_rec = rec + (None, None, None, None)
        ins_sql = "INSERT INTO shows VALUES {0};".format(str(new_rec).replace('None', 'NULL'))
        execute_sql(sqltype="Commit", sql=ins_sql)
        recs = recs + 1
        if recs % 5000 == 0:
            mdb.commit()
            print(f'Committed {recs} number of Show records')
    mdb.commit()

    print('Updating the Alternate Showname in the Shows Table')
    all_alt_shownames = execute_sqlite(sqltype='Fetch', sql='SELECT * from alt_showname order by showid ')
    print(len(all_alt_shownames))
    recs = 0
    for rec in all_alt_shownames:
        alt_name = f'''{str(rec[2].replace('"', ' '))}'''
        if rec[3] == 'Yes':
            override = 'Yes'
            sql = f'''UPDATE shows set alt_showname='{alt_name}',
                                       alt_sn_override='{override}' WHERE showid={rec[0]}'''
        else:
            override = None
            sql = f'''UPDATE shows set alt_showname='{alt_name}',
                                       alt_sn_override={override} WHERE showid={rec[0]}'''.replace('None', 'NULL')
        execute_sql(con="Y", db=mdb, cur=mcur, batch='Y', sqltype="Commit", sql=sql)
        recs += 1
        if recs % 5000 == 0:
            mdb.commit()
            print(f'Committed {recs} number of Show records')
    mdb.commit()

    print('Filling the Episodes Table')
    eps_by_show = execute_sqlite(sqltype='Fetch', sql='SELECT * from eps_by_show order by showid, epiid ')
    print(len(eps_by_show))
    for rec in eps_by_show:
        ins_sql = "INSERT INTO episodes VALUES {0};".format(str(rec).replace('None', 'NULL').replace("''", "NULL"))
        execute_sql(sqltype="Commit", sql=ins_sql)

    print('Updating the Episode related info into Shows Table')
    followed_shows = execute_sqlite(sqltype='Fetch', sql='SELECT * from followed_shows order by showid ')
    print(len(followed_shows))
    for rec in followed_shows:
        sql = f'''UPDATE shows set eps_count={rec[8]}, eps_updated='{rec[9]}' WHERE showid={rec[0]}'''
        execute_sql(sqltype="Commit", sql=sql)

    print('Filling the Statistics Table')
    statistics = execute_sqlite(sqltype='Fetch', sql='SELECT * from statistics order by statepoch ')
    print(len(statistics))
    for rec in statistics:
        ins_sql = "INSERT INTO statistics VALUES {0};".format(str(rec).replace('None', 'NULL').replace("''", "NULL"))
        execute_sql(sqltype="Commit", sql=ins_sql)

    print('Changing the Episodes table to the new format')
    rename_sql = "ALTER TABLE TVMazeDB.episodes CHANGE mystatus_updated mystatus_date date DEFAULT NULL NULL;"
    drop_sql = "ALTER TABLE TVMazeDB.episodes DROP COLUMN showname;"
    execute_sql(sqltype='Commit', sql=drop_sql)
    execute_sql(sqltype='Commit', sql=rename_sql)

    close_mdb(mdb)


''' Main Program'''
print(term_codes.cl_scr)
print('TVMaze DB Management')
options = get_cli_args()

if options['-t']:
    process_transfer()

if options['-d']:
    dbtables = execute_sql(sqltype="Fetch", sql=tables('TVMazeDB'))
    for tbl in dbtables:
        fscols = execute_sql(sqltype="Fetch", sql=tables('TVMazeDB', tbl[0]))
        for fsc in fscols:
            print('Table:', tbl[0], 'Seq No:', fsc[1], 'Column:', fsc[0])

if options['-i']:
    print("Not implemented yet")
    print()

if options['-cto']:
    process_create_db_tvmaze()

quit()

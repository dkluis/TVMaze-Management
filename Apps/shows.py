from tvm_api_lib import *
from db_lib import *
from terminal_lib import *
from tvm_lib import def_downloader

from timeit import default_timer as timer
from datetime import datetime, date


def transform_showname(name):
    alt_showname = str(name).replace("'", "")
    alt_showname = alt_showname.replace("...", "")
    alt_showname = alt_showname.replace(":", "")
    alt_showname = alt_showname.replace(",", "")
    alt_showname = alt_showname.replace("&", "and")
    alt_showname = alt_showname.replace('"', '')
    alt_showname = alt_showname.replace('°', '')
    return alt_showname


def process_show_info(rec, interest="New"):
    network = ""
    country = ""
    if rec['webChannel']:
        network = rec['webChannel']['name']
        if rec['webChannel']['country']:
            country = rec['webChannel']['country']['name']
    elif rec['network']:
        network = rec['network']['name']
        if rec['network']['country']:
            country = rec['network']['country']['name']
    length = 99
    if rec['runtime']:
        length = rec['runtime']
    if rec['language']:
        language = rec['language']
    else:
        language = "NA"
    # Setting the default for classifying the show status/interest
    if rec['premiered'] is None:
        premiered = '2030-12-31'
    else:
        premiered = rec['premiered']

    my_interest = interest
    if interest == "New":
        my_interest = interest
        if language != "English" and network != 'Netflix':
            my_interest = "Skipped"
        elif language != "English":
            my_interest = "Skipped"
        elif rec['status'] == "Ended" and premiered < "2019-01-01":
            my_interest = "Skipped"
        elif rec['type'] == 'Sports' or \
                rec['type'] == 'News' or \
                rec['type'] == 'Variety' or \
                rec['type'] == 'Game Show':
            my_interest = "Skipped"
        elif network == 'Youtube' or \
                network == 'Youtube Premium' or \
                network == 'Facebook Watch':
            my_interest = 'Skipped'
    
    return {'network': network, 'country': country,
            'runtime': length, 'language': language,
            'premiered': premiered, 'interest': my_interest}


def get_cli_args():
    tlc = ["-i", "-s", "-u", "-h"]
    flc = check_cli_args(tlc)
    found = False
    for e in flc.items():
        if e[1]:
            found = True
            break
    if not found or flc['-h']:
        print(f"{term_codes.green}CLI Options are: {term_codes.red}-h{term_codes.green} (Help), "
              f"{term_codes.red}-i{term_codes.green} (Initialize from TVMaze - Fresh), "
              f"{term_codes.red}-s{term_codes.green} (Sync with TVMaze - All shows sync'), "
              f"{term_codes.red}-u{term_codes.green} (Update Sync with TVMaze - Updated Shows Only)")
        print()
        quit()
    return flc


def process_all_shows(start, end, sync):
    ind = start  # Enter the last page processed
    while ind <= end:  # Paging is going up to 250  # Remember last page processed here: 197
        print('All Shows Processing TVMaze Page: ', ind)
        req = tvm_apis.shows_by_page + str(ind)
        response = execute_tvm_request(api=req, err=False)
        if type(response) == bool:
            print('Last TVMaze page found was:', ind - 1)
            break
        for res in response.json():
            result = execute_sql(sql="SELECT * from shows WHERE showid = {0}".format(res['id']), sqltype="Fetch")
            if not result:
                print('Record Not Found:', result)
                # insert_show(res)
            else:
                if sync:
                    print('Syncing: ', res['id'], res['name'])
                    # update_show(res)
                else:
                    print("Found: ", res['id'], res['name'])
        # time.sleep(1)
        ind = ind + 1


def process_update_all_shows(mdb, mcur):
    response = execute_tvm_request(api=tvm_apis.updated_shows)
    response = response.json()
    print('Number of Shows to potentially update', len(response))
    updated = 0
    inserted = 0
    skipped = 0
    processed = 0
    batch = 0
    for key in response:
        processed = processed + 1
        if processed % 5000 == 0:
            print(f"Processed {processed} records. ")
        showid = key
        showupdated = response[key]
        result = execute_sql(con="Y", db=mdb, cur=mcur,
                             sql="SELECT * from shows WHERE showid = {0}".format(showid), sqltype="Fetch")
        if not result:
            showinfo = execute_tvm_request(f'http://api.tvmaze.com/shows/{showid}')
            showinfo = showinfo.json()
            si = process_show_info(showinfo)
            sql = generate_insert_sql(
                table='shows',
                primary=showinfo['id'],
                f1=('quotes', f'{showinfo["name"]}'),
                f2=(2, f"'{showinfo['url']}'"),
                f3=(3, f"'{showinfo['type']}'"),
                f4=(4, f"'{showinfo['status']}'"),
                f5=(5, f"'{si['premiered']}'"),
                f6=(6, f"'{si['language']}'"),
                f7=(7, f"'{si['runtime']}'"),
                f8=(8, f"'{si['network']}'"),
                f9=(9, f"'{si['country']}'"),
                f10=(10, f"'{showinfo['externals']['tvrage']}'"),
                f11=(11, f"'{showinfo['externals']['thetvdb']}'"),
                f12=(12, f"'{showinfo['externals']['imdb']}'"),
                f13=(13, f"'{showinfo['updated']}'"),
                f14=(14, f"'{date.fromtimestamp(showinfo['updated'])}'"),
                f15=(15, f"'{si['interest']}'"),
                f16=(16, 'NULL'),
                f17=(17, f"'{str(datetime.now())[:10]}'"),
                f18=(18, f"'{transform_showname(showinfo['name'])}'"),
                f19=(19, None),
                f20=(20, None),
                f21=(21, None)
            )
            sql = sql.replace("'None'", 'NULL').replace('None', 'NULL')
            execute_sql(con="Y", db=mdb, cur=mcur, sql=sql, sqltype='Commit')
            inserted = inserted + 1
        else:
            if len(result) != 1:
                print("Found too many records or not enough:", result)
                quit()
            else:
                result = result[0]
            if result[13] == showupdated or result[15] != "Followed":
                skipped = skipped + 1
            else:
                showinfo = execute_tvm_request(f'http://api.tvmaze.com/shows/{showid}')
                showinfo = showinfo.json()
                si = process_show_info(showinfo)
                if result[19] is None:
                    sql = generate_update_sql(tvmaze_updated=showupdated,
                                              tvmaze_upd_date=f"'{date.fromtimestamp(showupdated)}'",
                                              network=si['network'],
                                              country=si['country'],
                                              runtime=si['runtime'],
                                              language=si['language'],
                                              premiered=si['premiered'],
                                              showname=str(showinfo["name"]).replace('"', "'"),
                                              alt_showname=f'''{str(transform_showname(showinfo["name"]))
                                              .replace('"', "'")}''',
                                              tvrage=showinfo['externals']['tvrage'],
                                              thetvdb=showinfo['externals']['thetvdb'],
                                              imdb=showinfo['externals']['imdb'],
                                              record_updated='current_date',
                                              where=f"showid={showid}",
                                              table='shows')
                else:
                    sql = generate_update_sql(tvmaze_updated=showupdated,
                                              tvmaze_upd_date=f"'{date.fromtimestamp(showupdated)}'",
                                              network=si['network'],
                                              country=si['country'],
                                              runtime=si['runtime'],
                                              language=si['language'],
                                              premiered=si['premiered'],
                                              showname=str(showinfo["name"]).replace('"', "'"),
                                              tvrage=showinfo['externals']['tvrage'],
                                              thetvdb=showinfo['externals']['thetvdb'],
                                              imdb=showinfo['externals']['imdb'],
                                              record_updated='current_date',
                                              where=f"showid={showid}",
                                              table='shows')
                execute_sql(con="Y", batch="Y", db=mdb, cur=mcur, sql=sql, sqltype='Commit')
                updated = updated + 1
                batch = batch + 1
                if batch % 100 == 0:
                    print(f"Commit of {batch} updated records")
                    mdb.commit()
    if batch != 0:
        print("Final Commit of updated records")
        mdb.commit()
    print(f"Processed {processed} records. ")
    print(f'Shows Evaluated: {len(response)} -> Inserted: {inserted} '
          f'-> Updated: {updated}, No Update Needed: {skipped}')


def process_followed_shows():
    result = execute_tvm_request(api=tvm_apis.followed_shows, code=True)
    result = result.json()
    found = False
    shows = execute_sql(sqltype='Fetch', sql=std_sql.followed_shows)
    count = 0
    nf_list = []
    for show in shows:
        count += 1
        for res in result:
            if res['show_id'] == show[0]:
                found = True
                break
            else:
                found = False
        if not found:
            nf_list.append(show[0])
    new_followed = 0
    for res in result:
        validates = execute_sql(sqltype='Fetch',
                                sql=f'SELECT showname, status from shows where showid={res["show_id"]}')
        if validates[0][1] != 'Followed':
            new_followed += 1
            print(validates[0][0], validates[0][1])
            result = execute_sql(sqltype='Commit', sql=f'UPDATE shows SET status="Followed", '
                                                       f'download="{def_downloader.dl}" WHERE showid={res["show_id"]}')
            if not result:
                print(f'Update error on Shows table for show: {res["show_id"]} trying to make a followed show')
                quit()
            print(f'Now following show {validates[0][0]}')

    un_followed = 0
    for nf in nf_list:
        un_followed += 1
        result = execute_sql(sqltype="Fetch", sql=f'SELECT showname, status from shows where showid={nf}')
        if not result:
            print(f'Read error on: {nf}')
            quit()
        if len(result) != 1:
            print(f'Did not get a single record for show: {nf}')
            quit()
        showname = result[0][0]
        result = execute_sql(sqltype='Commit', sql=f'DELETE FROM episodes WHERE showid={nf}')
        if not result:
            print(f'Delete error on Episodes table for show: {nf}')
            quit()
        result = execute_sql(sqltype='Commit',
                             sql=f'UPDATE shows SET status="Skipped", download=NULL WHERE showid={nf}')
        if not result:
            print(f'Update error on Shows table for show: {nf} trying to un-follow')
            quit()
        print(f'Un-followed show {showname}')

    print(f"Updates performed based on TVMaze Followed status.  "
          f"Un-followed: {un_followed} and new Followed: {new_followed}")


''' Main Program'''
print(term_codes.cl_scr)
options = get_cli_args()

mdb_info = mdbi('', '')
tvmaze = connect_mdb(d=mdb_info.db)
db = tvmaze['mdb']
cur = tvmaze['mcursor']
db.autocommit = False

if options['-s']:
    print("Starting to process all tvmaze show with updates (sync)")
    print('Not fully implemented yet - no insert or update')
    process_all_shows(196, 199, sync=True)
elif options['-i']:
    print('Starting to process all tvmaze shows for initialize only')
    print('Not fully implemented yet - no insert or update')
    process_all_shows(0, 198, sync=False)
elif options['-u']:
    started = timer()
    print(f'{str(datetime.now())} -> Starting to process recently updated shows for insert and sync')
    process_update_all_shows(mdb=db, mcur=cur)
    ended = timer()
    print(f'{str(datetime.now())} -> The process (including calling the TVMaze APIs) took: {ended - started} seconds')
    print()
    started = timer()
    print(f'{str(datetime.now())} -> Starting to process to validate followed shows and update')
    process_followed_shows()
    ended = timer()
    print(f'{str(datetime.now())} -> The process (including calling the TVMaze APIs) took: {ended - started} seconds')
    print()

db.commit()
close_mdb(mdb=db)

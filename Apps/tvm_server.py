from flask import Flask
from flask_cors import CORS
import pandas as pd

from Libraries import mariaDB, convert_to_dict_within_list, connect_pd, shows


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'http://127.0.0.1'

db = mariaDB()


@app.route('/apis/v1/shows/page/<page>')
def get_shows_page(page):
    if int(page) <= 0:
        result = db.execute_sql(sqltype='Fetch', sql=f'select * from shows where showid < 1000')
    else:
        start = int(page) * 1000
        end = int(page) * 1000 + 999
        result = db.execute_sql(sqltype='Fetch', sql=f'select * from shows where showid between {start} and {end}')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return result


@app.route('/apis/v1/shows/page/<page>/followed')
def get_shows_page_followed(page):
    if int(page) <= 0:
        result = db.execute_sql(sqltype='Fetch', sql=f'select * from shows where showid < 1000 and status = "Followed"')
    else:
        start = int(page) * 1000
        end = int(page) * 1000 + 999
        result = db.execute_sql(sqltype='Fetch', sql=f'select * from shows '
                                                  f'where status = "Followed" and showid between {start} and {end}')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return result


@app.route('/apis/v1/shows/followed')
def get_shows_followed():
    result = db.execute_sql(sqltype='Fetch', sql=f'select * from shows where status = "Followed"')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return result


@app.route('/apis/v1/show/<showid>')
def get_show_by_id(showid):
    result = db.execute_sql(sqltype='Fetch', sql=f'select * from shows '
                                              f'where `showid` = {showid}')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return f'{result}'


@app.route('/apis/v1/show/name/<showname>/wild')
def get_show_by_name_wild(showname):
    result = db.execute_sql(sqltype='Fetch', sql=f'select * from shows '
                                              f'where showname like "%{showname}%"')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return f'{result}'


@app.route('/apis/v1/show/name/<showname>/followed/wild')
def get_show_by_name_followed_wild(showname):
    result = db.execute_sql(sqltype='Fetch', sql=f'select * from shows '
                                              f'where showname like "%{showname}%" and status = "Followed"')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return f'{result}'


@app.route('/apis/v1/show/name/<showname>')
def get_show_by_name(showname):
    result = db.execute_sql(sqltype='Fetch', sql=f'select * from shows '
                                              f'where showname = "{showname}"')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return f'{result}'


@app.route('/apis/v1/show/name/<showname>/followed')
def get_show_by_name_followed(showname):
    result = db.execute_sql(sqltype='Fetch', sql=f'select * from shows '
                                              f'where showname = "{showname}" and status = "Followed"')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return f'{result}'


@app.route('/apis/v1/stats')
def get_stat_records():
    con = connect_pd()
    df = pd.read_sql_query('select * from statistics where statrecind = "TVMaze" order by statepoch', con)
    return f'{df}'


if __name__ == '__main__':
    app.run(debug=True)

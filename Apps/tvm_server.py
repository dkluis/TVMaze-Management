from flask import Flask
from Libraries.tvm_functions import execute_sql, convert_to_dict_within_list
from Libraries.tvm_db import connect_pd, shows
import pandas as pd

app = Flask(__name__)


@app.route('/apis/v1/shows')
def get_shows():
    result = execute_sql(sqltype='Fetch', sql=f'select * from shows')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return f'{result}'


@app.route('/apis/v1/shows/followed')
def get_shows_followed():
    result = execute_sql(sqltype='Fetch', sql=f'select * from shows where status = "Followed"')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return f'{result}'


@app.route('/apis/v1/show/<showid>')
def get_show_by_id(showid):
    result = execute_sql(sqltype='Fetch', sql=f'select * from shows '
                                              f'where `showid` = {showid}')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return f'{result}'


@app.route('/apis/v1/show/name/<showname>/wild')
def get_show_by_name_wild(showname):
    result = execute_sql(sqltype='Fetch', sql=f'select * from shows '
                                              f'where showname like "%{showname}%"')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return f'{result}'


@app.route('/apis/v1/show/name/<showname>/followed/wild')
def get_show_by_name_followed_wild(showname):
    result = execute_sql(sqltype='Fetch', sql=f'select * from shows '
                                              f'where showname like "%{showname}%" and status = "Followed"')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return f'{result}'


@app.route('/apis/v1/show/name/<showname>')
def get_show_by_name(showname):
    result = execute_sql(sqltype='Fetch', sql=f'select * from shows '
                                              f'where showname = "{showname}"')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return f'{result}'


@app.route('/apis/v1/show/name/<showname>/followed')
def get_show_by_name_followed(showname):
    result = execute_sql(sqltype='Fetch', sql=f'select * from shows '
                                              f'where showname = "{showname}" and status = "Followed"')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=shows.field_list)
    return f'{result}'


@app.route('/apis/v1/stats')
def get_stat_records():
    con = connect_pd()
    df = pd.read_sql_query('select * from statistics where statrecind = "TVMaze" order by statepoch asc', con)
    return f'{df}'


if __name__ == '__main__':
    app.run(debug=True)

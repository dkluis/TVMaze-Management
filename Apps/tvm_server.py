from flask import Flask
from Libraries.tvm_functions import execute_sql, convert_to_dict_within_list
from Libraries.tvm_db import connect_pd
import pandas as pd

app = Flask(__name__)


@app.route('/apis/v1/shows')
def get_shows():
    result = execute_sql(sqltype='Fetch', sql=f'select showid, showname, alt_showname from shows')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=['showid', 'showname', 'alt_showname'])
    return f'{result}'


@app.route('/apis/v1/show/<showid>')
def get_show_by_id(showid):
    result = execute_sql(sqltype='Fetch', sql=f'select showid, showname, alt_showname from shows '
                                              f'where `showid` = {showid}')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=['showid', 'showname', 'alt_showname'])
    return f'{result}'


@app.route('/apis/v1/show/name/<showname>/wild')
def get_show_by_name_wild(showname):
    result = execute_sql(sqltype='Fetch', sql=f'select showid, showname, alt_showname from shows '
                                              f'where showname like "%{showname}%"')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=['showid', 'showname', 'alt_showname'])
    return f'{result}'


@app.route('/apis/v1/show/name/<showname>')
def get_show_by_name(showname):
    result = execute_sql(sqltype='Fetch', sql=f'select showid, showname, alt_showname from shows '
                                              f'where showname = "{showname}"')
    result = convert_to_dict_within_list(result, data_type='DB', field_list=['showid', 'showname', 'alt_showname'])
    return f'{result}'


@app.route('/apis/v1/stats')
def getstat_records():
    con = connect_pd()
    df = pd.read_sql_query('select * from statistics where statrecind = "TVMaze" order by statepoch asc', con)
    return f'{df}'


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask
from Libraries.tvm_functions import execute_sql
from Libraries.tvm_db import connect_pd
import pandas as pd

app = Flask(__name__)


@app.route('/tvmdb/sql=<sql>')
def getdb_records(sql):
    result = execute_sql(sqltype='Fetch', sql=str(sql).replace("'", ""))
    return f'{result}'


@app.route('/tvmstats')
def getstat_records():
    con = connect_pd()
    df = pd.read_sql_query('select * from statistics where statrecind = "TVMaze" order by statepoch asc', con)
    return f'{df}'


if __name__ == '__main__':
    app.run(debug=True)

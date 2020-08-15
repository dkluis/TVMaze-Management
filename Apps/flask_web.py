from flask import Flask
from tvm_lib import execute_sql

app = Flask(__name__)


@app.route('/tvmdb/sql=<sql>')
def hello_world(sql):
    result = execute_sql(sqltype='Fetch', sql=str(sql).replace("'", ""))
    return f'{result}'


if __name__ == '__main__':
    app.run(debug=True)

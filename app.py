#!/usr/bin/env python3
import sys
from datetime import datetime
from flask import Flask, render_template, session, redirect, request, Response
import flask
import json, os
from pathlib import Path
from utils import Config, safe_get_value
from utils.db import sqlite_db

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)


CFG = Config('config/config.json')

if not CFG:
    print('Could not create config')

db_file = Path(CFG.path('database/sqlite3/file'))

db_max_rows = \
    safe_get_value(CFG.path('/database/sqlite3/max_rows'), int, int(1e6))

db = sqlite_db(db_file, max_rows=db_max_rows)


def calc_since(seconds: int):
    if seconds > 0:
        now = datetime.now().timestamp()
        timestamp = now - seconds
    return timestamp


@app.route('/api/<table>', methods=['GET'])
def add_to_db(table=None):
    if not table:
        return f'{{"error": "Database is {table}"}}'
    column = request.args.get('measurement')
    value = request.args.get('value')
    since = request.args.get('since') or 0
    since = safe_get_value(since, int, 0)

    if column and value:
        db.insert(table, column, safe_get_value(value, float, 0))
        return json.dumps({'reply':'thanks'})
    elif column == 'list':
        return json.dumps(db.get_measurement_names(table))
    elif column:
        result = db.get_transient_data(
                    table,
                    column,
                    from_time=calc_since(since))
        out = []
        for item in result:
            out.append({'time': item[0],'value':item[1]})


        return json.dumps({'result': out})
    else:
        result = db.get_tables()
        return json.dumps({'tables': result})


if __name__ == '__main__':
    try:
        debug = sys.argv[1] == 'debug'
    except:
        debug = False
    print(f'PID: {os.getpid()}')
    app.run(host=CFG.path('server/ip'), port=CFG.path('server/port'), debug=debug)
    db.close()

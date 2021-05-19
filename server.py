from flask import Flask, jsonify, request
app = Flask(__name__)

import sqlite3, datetime



def rounder(t):
    if t.second >= 30:
        return t.replace(second=0, microsecond=0, minute=t.minute+1)
    else:
        return t.replace(second=0, microsecond=0, minute=t.minute)


@app.route('/current')
def get_current():
    with sqlite3.connect("data.db") as con:
        cur = con.cursor()
        date = rounder(datetime.datetime.now())
        stmt = f'''SELECT * FROM greenhouse WHERE date = '{date}';''' 
        data = cur.execute(stmt)
        return jsonify(data.fetchall())

@app.route('/between', methods=['POST'])
def get_between():
    start = request.form.get('start')
    end = request.form.get('end')
    
    start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

    dts = [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in
       datetime_range(start, end, datetime.timedelta(minutes=1))]
    
    print(dts)
    
    with sqlite3.connect("data.db") as con:
        cur = con.cursor()
        ret = []
        for dt in dts:
            stmt = f'''SELECT * FROM greenhouse WHERE date = '{dt}';'''
            cur.execute(stmt)
            ret.append(cur.fetchall())
        return jsonify(ret)

def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta

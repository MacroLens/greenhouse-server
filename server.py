from flask import Flask, jsonify, request
app = Flask(__name__)

import sqlite3
import datetime
from datetime import timedelta
import pdb
from gevent.pywsgi import WSGIServer


DATABASE = "/home/pi/greenhouse/data.db"

def rounder(t):
    """
    Rounds the time down to the minute
    """
    return t.replace(second=0, microsecond=0, minute=t.minute)


@app.route('/current')
def get_current():
    """
    Get the current temperature. This reads the latest entry from the DB
    """
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        stmt = f'''SELECT * FROM greenhouse ORDER BY timestamp DESC limit 1'''
        cur.execute(stmt)
        data = cur.fetchall()

        ret = {
            'timestamp': data[0][0],
            'temperature': float(data[0][1]),
            'humidity': float(data[0][2]),
            'pressure': data[0][3]
        }
        return jsonify(ret)


@app.route('/between')
def get_between():
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))

    # print(f'''start={start}, end={end}''')
    start_str = datetime.datetime.fromtimestamp(start)
    end_str = datetime.datetime.fromtimestamp(end)
    # print("Searching between " + str(start_str) + "->" + str(end_str))

    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        ret = []
        stmt = f'''SELECT * FROM greenhouse WHERE timestamp >= {start} and timestamp <= {end};'''
        # print(stmt)
        cur.execute(stmt)
        values = cur.fetchall()
        print(values)
        ret = [
            {
                'timestamp': data[0],
                'temperature': data[1],
                'humidity': data[2],
                'pressure': data[3]
            } for data in values
        ]
        return jsonify(ret)

@app.route('/hilo')
def get_hilo():
    days = int(request.args.get('days'))

    ret = []

    end = datetime.datetime.now()
    start = end.replace(hour=0, minute=0, microsecond=0)
    while days > 0:
        high_time, high_temp, low_time, low_temp = find_hilo(start.timestamp(), end.timestamp())
        ret.append({
            'high_time': high_time,
            'high_temp': high_temp,
            'low_time': low_time,
            'low_temp': low_temp
        })
        end = start
        start = start - timedelta(days=1)
        days -= 1

    return jsonify(ret)

def find_hilo(start, end):
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        stmt = f'''
            SELECT timestamp, MAX(temperature) FROM greenhouse
            WHERE timestamp >= {start} AND timestamp <= {end}
        '''
        # print(stmt)
        cur.execute(stmt)
        values = cur.fetchall()
        high_time = values[0][0]
        high_temp = values[0][1]

        stmt = f'''
            SELECT timestamp, MIN(temperature) FROM greenhouse
            WHERE timestamp >= {start} AND timestamp <= {end}
        '''
        cur.execute(stmt)
        values = cur.fetchall()
        low_time = values[0][0]
        low_temp = values[0][1]

        return high_time, high_temp, low_time, low_temp




if __name__ == "__main__":
    server = WSGIServer(('', 5000), app)
    server.serve_forever()

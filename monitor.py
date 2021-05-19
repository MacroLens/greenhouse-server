"""
Saves data to sqlite db.
"""

from sense_hat import SenseHat

import sched, time, sqlite3, datetime
con = sqlite3.connect('data.db')

cur = con.cursor()


# Create table
try:
    cur.execute('''CREATE TABLE greenhouse
                   (date text, temperature text, humidity text, pressure real)''')
except sqlite3.OperationalError:
    print("Database already created")
con.commit()


s = sched.scheduler(time.time, time.sleep)
sense = SenseHat()



def rounder(t):
    if t.second >= 30:
        return t.replace(second=0, microsecond=0, minute=t.minute+1)
    else:
        return t.replace(second=0, microsecond=0, minute=t.minute)

def save_data(sc):
    date = rounder(datetime.datetime.now())

    temp = round(sense.get_temperature(), 1)
    humidity = round(sense.get_humidity(), 1)
    pressure = int(sense.get_pressure())

    stmt = f'''INSERT INTO greenhouse VALUES ('{date}', '{temp}', '{humidity}', '{pressure}' );'''
    print(f'{date} : {temp}c, {humidity}%, {pressure}mbar')


    cur.execute(stmt)
    con.commit()

    s.enter(60, 1, save_data, (sc,))

s.enter(60, 1, save_data, (s,))
s.run()

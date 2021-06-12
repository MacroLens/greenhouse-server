"""
Saves data to sqlite db.
"""

from sense_hat import SenseHat
import numbers_image
# import inflect

DATABASE = "/home/pi/greenhouse/data.db"

import sched, time, sqlite3, datetime
con = sqlite3.connect(DATABASE)

cur = con.cursor()


# Create table
# the greenhouse table
try:
    cur.execute('''CREATE TABLE IF NOT EXISTS greenhouse
                   (timestamp bigint, temperature real, humidity real, pressure real)''')
except sqlite3.OperationalError:
    print("Database already created")
con.commit()


s = sched.scheduler(time.time, time.sleep)
sense = SenseHat()
# inf = inflect.engine()

def rounder(t):
    """
    Round down to the floor minute
    """
    return t.replace(second=0, microsecond=0, minute=t.minute)

def c2f(c):
    """
    Convert celsius to fahrenheit
    """
    return 9/5 * c + 32

def save_data(sc):
    timestamp = rounder(datetime.datetime.now()).timestamp()

    temp = round(sense.get_temperature(), 1)
    humidity = round(sense.get_humidity(), 1)
    pressure = int(sense.get_pressure())

    stmt = f'''INSERT INTO greenhouse VALUES ({timestamp}, {temp}, {humidity}, {pressure} );'''

    dt = datetime.datetime.fromtimestamp(timestamp)
    print(f'{dt} : {temp}c, {humidity}%, {pressure}mbar')

    cur.execute(stmt)
    con.commit()

    temp = c2f(temp)

    first = int(str(temp)[:1]) - 1
    second = int(str(temp)[1:2]) - 1
    sense.set_pixels(numbers_image.combine_numbers(numbers_image.numbers[first], numbers_image.numbers[second]))

    s.enter(60, 1, save_data, (sc,))


s.enter(1, 1, save_data, (s,))
s.run()

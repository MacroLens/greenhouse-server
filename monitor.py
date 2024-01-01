"""
Saves data to sqlite db.
"""

from sense_hat import SenseHat
import numpy as np
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

def get_poly_cal(filename: str, max_degree: int=2) -> np.ndarray :
    """
    Calculates the least squares regression polynomial
    curve for the CSV `filename` with N samples.
    With maximum degree max_degree or N-1 whichever is smaller.
    """
    # Open calibration file
    x,y = np.loadtxt(filename, delimiter=',', unpack=True)
    degree = min(max_degree, len(y)-1)

    # Calculate least squares regression
    return np.polynomial.polynomial.polyfit(x,y, degree)


s = sched.scheduler(time.time, time.sleep)
sense = SenseHat()
polynomial = get_poly_cal("cal.csv")

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

    # Read 1000 temps over 5 seconds to get the avg reading
    interval = 5 / 1000 # inteval between reads
    temps = []
    for _ in range(1000):
        temps.append(sense.get_temperature())
        time.sleep(interval)
    temp = sum(temps)/len(temps)

    calibrated_temp = round(np.polynomial.polynomial.polyval(temp, polynomial), 1)
    humidity = round(sense.get_humidity(), 1)
    pressure = int(sense.get_pressure())

    stmt = f'''INSERT INTO greenhouse VALUES ({timestamp}, {calibrated_temp}, {humidity}, {pressure} );'''

    dt = datetime.datetime.fromtimestamp(timestamp)
    print(f'{dt} : {temp}c, {humidity}%, {pressure}mbar')

    max_attempts = 10
    for _ in range(max_attempts):
        try:
            cur.execute(stmt)
            con.commit()
            break
        except sqlite3.OperationalError as e:
            print("Couldn't commit insert: ", e)

    temp = c2f(temp)

    first = int(str(temp)[:1]) - 1
    second = int(str(temp)[1:2]) - 1
    # sense.set_pixels(numbers_image.combine_numbers(numbers_image.numbers[first], numbers_image.numbers[second]))

    s.enter(60, 1, save_data, (sc,))


s.enter(1, 1, save_data, (s,))
s.run()

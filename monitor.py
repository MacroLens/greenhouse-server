"""
Saves data to Firebase firestore database.
"""

from sense_hat import SenseHat
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore 
import numpy as np
import numbers_image
import sched, time

# Use a service account. 
cred = credentials.Certificate('cert.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

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

def c2f(c):
    """
    Convert celsius to fahrenheit
    """
    return 9/5 * c + 32

def save_data(sc):
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

    sensor_read = {
            "timestamp": firestore.SERVER_TIMESTAMP,
            "humidity": humidity,
            "pressure": pressure,
            "temperature": calibrated_temp,
            }
    update_time, sensor_read_ref = db.collection("sensor-data").add(sensor_read)
    print(f"Added document with id {sensor_read_ref.id}")

    sc.enter(60, 1, save_data, (sc,))


s.enter(1, 1, save_data, (s,))
s.run()

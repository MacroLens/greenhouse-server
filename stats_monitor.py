"""
Experiments on the SenseHat
"""

from sense_hat import SenseHat
from typing import Callable
import numpy as np
import time

def get_temps(temperature_func, N, duration):
    """
    Returns an array of temperatures of length `N`
    taken evenly over duration `duration`.
    """
    interval = duration / N
    temps = []
    for _ in range(N):
        temps.append(temperature_func())
        time.sleep(interval)
    return temps


def get_avg_temp(temperature_func: Callable[[], float], N: int, duration: float):
    """ Returns the average temperature over duration
    `duration` with `N` readings.
    """
    temps = get_temps(temperature_func, N, duration)
    return sum(temps)/len(temps)

def get_std_temp(temperature_func: Callable[[], float], N: int, duration: float):
    """ Return the std deviation of `N` temperature readings
    over `duration`
    """
    return np.std(get_temps(temperature_func, N, duration))



if __name__ == "__main__":
    sense = SenseHat()
    humidity_temp = sense.get_temperature_from_humidity
    pressure_temp = sense.get_temperature_from_pressure

    N = 1000
    t = 0

    humidity_temps_no_sleep = get_temps(humidity_temp, N, t)
    avg_humidity_temp_no_sleep = sum(humidity_temps_no_sleep)/len(humidity_temps_no_sleep)
    pressure_temps_no_sleep = get_temps(pressure_temp, N, t)
    avg_pressure_temp_no_sleep = sum(pressure_temps_no_sleep)/len(pressure_temps_no_sleep)
    avg_diff_temp_no_sleep = avg_humidity_temp_no_sleep - avg_pressure_temp_no_sleep
    print("Average temperature from humidity sensor: ", avg_humidity_temp_no_sleep)
    print("Average temperature from pressure sensor: ", avg_pressure_temp_no_sleep)
    print("Std dev of temperature from humidity sensor: ", np.std(humidity_temps_no_sleep))
    print("Std dev of temperature from pressure sensor: ", np.std(pressure_temps_no_sleep))
    print("Difference in average no sleep (humidity - pressure): ", avg_diff_temp_no_sleep)

    N = 1000
    t = 5

    humidity_temps_sleep = get_temps(humidity_temp, N, t)
    avg_humidity_temp_sleep = sum(humidity_temps_sleep)/len(humidity_temps_sleep)
    pressure_temps_sleep = get_temps(pressure_temp, N, t)
    avg_pressure_temp_sleep = sum(pressure_temps_sleep)/len(pressure_temps_sleep)
    avg_diff_temp_sleep = avg_humidity_temp_sleep - avg_pressure_temp_sleep
    print("Average temperature from humidity sensor: ", avg_humidity_temp_sleep)
    print("Average temperature from pressure sensor: ", avg_pressure_temp_sleep)
    print("Std dev of temperature from humidity sensor: ", np.std(humidity_temps_sleep))
    print("Std dev of temperature from pressure sensor: ", np.std(pressure_temps_sleep))
    print("Difference in average with sleep (humidity - pressure): ", avg_diff_temp_sleep)

    num_tries = 100
    std_devs_humidity = []
    std_devs_pressure = []
    for _ in range(num_tries):
        humidity_temps_sleep = get_temps(humidity_temp, N, t)
        pressure_temps_sleep = get_temps(pressure_temp, N, t)
        std_devs_humidity.append(np.std(humidity_temps_sleep))
        std_devs_pressure.append(np.std(pressure_temps_sleep))

    print("Average Standard Deviation of humidity over {} tries: {}".format(num_tries, np.mean(std_devs_humidity)))
    print("Average Standard Deviation of pressure over {} tries: {}".format(num_tries, np.mean(std_devs_pressure)))


    num_tries = 100
    t = 0
    std_devs_humidity = []
    std_devs_pressure = []
    for _ in range(num_tries):
        humidity_temps_sleep = get_temps(humidity_temp, N, t)
        pressure_temps_sleep = get_temps(pressure_temp, N, t)
        std_devs_humidity.append(np.std(humidity_temps_sleep))
        std_devs_pressure.append(np.std(pressure_temps_sleep))

    print("Average Standard Deviation of humidity over {} tries no sleep: {}".format(num_tries, np.mean(std_devs_humidity)))
    print("Average Standard Deviation of pressure over {} tries no sleep: {}".format(num_tries, np.mean(std_devs_pressure)))

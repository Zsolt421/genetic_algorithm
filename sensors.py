import numpy as np
import math

NUMBER_OF_OUTPUTS = 2

def calculate_wheel_speed(genome, sensor_readings, NUMBER_OF_OUTPUTS, NUMBER_OF_SENSORS, MAX_SPEED) -> list:
    #array a gen listából,érzékelőkből -> dot product 2ször->
    
    weight_matrix = np.array(genome).reshape(NUMBER_OF_OUTPUTS,NUMBER_OF_SENSORS) 
    sensors_vector = np.array(sensor_readings)
    output = np.dot(weight_matrix, sensors_vector)
    ##float 2db egy a jobb egy a balkerékhez

    right_wheel_brake = output[0] #elso elem a jobb kerek
    left_wheel_brake = output[1] #masodik elem a bal kerek

    right_speed = MAX_SPEED - right_wheel_brake
    left_speed = MAX_SPEED - left_wheel_brake

    return right_speed, left_speed
    #vagy ez legyen külön függvényekben, egy a mátrix szorzásra, egy meg a speedre?
    


speed = (left_speed + right_speed) / 2

angular_speed = (left_speed - right_speed) / WHEEL_DISTANCE

angle += angular_speed * dt

x += math.cos(angle) * speed * dt #dt original.py-ban van defineolva
y += math.sin(angle) * speed * dt


def read_sensors(x, y, angle):

    sensor_values = []
    sensor_points = []

    # érzékelők indulópontja:
    # az autó eleje
    origin_x = x + math.cos(angle) * SENSOR_ORIGIN_OFFSET
    origin_y = y + math.sin(angle) * SENSOR_ORIGIN_OFFSET

    for distance in SENSOR_DISTANCES:

        for relative_angle in SENSOR_ANGLES:

            sensor_angle = ( angle + math.radians(relative_angle))

            sensor_x = ( origin_x + math.cos(sensor_angle) * distance)

            sensor_y = ( origin_y + math.sin(sensor_angle) * distance)

            if is_off_road(sensor_x, sensor_y):
                value = 1
            else:
                value = 0

            sensor_values.append(value)

            sensor_points.append(( sensor_x, sensor_y, value))

    return sensor_values, sensor_points, origin_x, origin_y
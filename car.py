import random
import numpy as np
import math

""" class Car:

    def __init__(self, genome = None):
        self.num_sensors = 16
        self.num_outputs = 2 #2 kerek van ezert 2, hogy kijojjon a matrix?
        self.genome_length = (self.num_sensors * self.num_outputs)

        self.checkpoint_index = (0)
        self.score = 0

        if genome is None:
            self.genome = [random.uniform(0, 1) for _ in range(self.genome_length)] # rasndint az nem int? hol a float?
        else:
            self.genome = genome


        self.fitness = 0
        self.is_alive = True """

def matrix_dot_product(self, sensor_readings) -> list:
    ##array a gen listából,érzékelőkből -> dot product 2ször->
    kereék_sebesség_változtató = []
    weight_matrix = np.array(self.genome).reshape(self.num_outputs, self.num_sensors) 
    sensors_vector = np.array(sensor_readings)
    output = np.dot(weight_matrix, sensors_vector)
    ##float 2db egy a jobb egy a balkerékhez
    return kereék_sebesség_változtató



#CEHCKPOINTS ITT JÖN-------------------------------------





def get_action(self, sensor_readings):

    output = matrix_dot_product()

    self.speed_left = self.speed + output[0]
    self.speed_right = self.speed + output [1]

    return output



#steering based on sensors


""" 
car.fitness = car.distance_traveled + (Car.self.score * 1000) #milegyenaszorzo?

# 


# Itt indul a fő program:
my_track = Track()

# A szimulációs ciklusban...
for car in cars:
  # Használhatod a Car metódusait, mert be lett importálva!
  steering = car.get_steering(sensor_readings)

  
        # -------------------------
        # KEYBOARD CONTROL
        # -------------------------

        keys = pygame.key.get_pressed()

        left_speed = 0
        right_speed = 0

        if keys[pygame.K_w]:
            left_speed = MAX_SPEED
            right_speed = MAX_SPEED

        if keys[pygame.K_a]:
            left_speed = TURN_SPEED
            right_speed = MAX_SPEED

        if keys[pygame.K_d]:
            left_speed = MAX_SPEED
            right_speed = TURN_SPEED

        # -------------------------
        # CAR MOVEMENT
        # -------------------------

        speed = (left_speed + right_speed) / 2

        angular_speed = ( left_speed - right_speed ) / wheel_distance

        angle += angular_speed * dt

        x += math.cos(angle) * speed * dt
        y += math.sin(angle) * speed * dt """




def update_checkpoints(self, checkpoints):
    checkpoints= [()]#ide kell sok minden még

    if self.checkpoint_index >= len(checkpoints):
        return

    target_x, target_y = checkpoints[self.checkpoint_index]

     # Kiszámoljuk a távolságot az autó és a checkpoint között (Pitagorasz-tétel)
    distance = math.sqrt((self.x - target_x) ** 2 + (self.y - target_y) ** 2)

     # Ha elég közel ment (pl. 40 pixelen belülre):
    if distance < #változó#:  #mi legyen a distance? mert itt kinda még nem érte el a checkpointot
        self.checkpoint_index += 1  # Lépünk a következő checkpointra
        self.score += 1000
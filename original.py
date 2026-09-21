import pygame
import math
import os

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Genetic Car Demo")

# -------------------------
# HÁTTÉR
# -------------------------

folder = os.path.dirname(__file__)

background = pygame.image.load(
    os.path.join(folder, "track.png")
)

background = pygame.transform.scale(
    background,
    (WIDTH, HEIGHT)
)

clock = pygame.time.Clock()


# -------------------------
# SENSOR BEÁLLÍTÁSOK
# -------------------------

# Negatív = balra
# Pozitív = jobbra
sensor_1 = 40
sensor_2 = 10
sensor_3 = -1 * sensor_1
sensor_4 = -1 * sensor_2
SENSOR_ANGLES = [sensor_1, sensor_2, sensor_3, sensor_4]

# Távolságok az autó előtt
sensor_dist = 20
SENSOR_DISTANCES = [sensor_dist, 2 * sensor_dist, 3 * sensor_dist, 4 * sensor_dist]

SENSOR_RADIUS = 3

# Ennyivel induljon az érzékelés
# az autó középpontja előtt
SENSOR_ORIGIN_OFFSET = 25


# -------------------------
# AUTÓ KEZDŐÁLLAPOTA
# -------------------------

x = WIDTH / 2
y = HEIGHT / 2

# indulási irány
angle = -math.pi / 4

left_speed = 0
right_speed = 0

WHEEL_DISTANCE = 40


# -------------------------
# ÚTFELÜLET ÉRZÉKELÉSE
# -------------------------

def is_off_road(px, py):

    px = int(px)
    py = int(py)

    # Ha a képernyőn kívül van
    if px < 0 or px >= WIDTH or py < 0 or py >= HEIGHT:
        return True

    color = background.get_at((px, py))

    r = color.r
    g = color.g
    b = color.b

    # A fű zöldebb, mint a szürke út.
    # Ha erősen dominál a zöld, akkor
    # az érzékelő az úton kívül van.
    if g > r + 25 and g > b + 25:
        return True

    return False


# -------------------------
# SENSOROK KIOLVASÁSA
# -------------------------

def read_sensors(x, y, angle):

    sensor_values = []
    sensor_points = []

    # érzékelők indulópontja:
    # az autó eleje
    origin_x = x + math.cos(angle) * SENSOR_ORIGIN_OFFSET
    origin_y = y + math.sin(angle) * SENSOR_ORIGIN_OFFSET

    for distance in SENSOR_DISTANCES:

        for relative_angle in SENSOR_ANGLES:

            sensor_angle = (
                angle
                + math.radians(relative_angle)
            )

            sensor_x = (
                origin_x
                + math.cos(sensor_angle) * distance
            )

            sensor_y = (
                origin_y
                + math.sin(sensor_angle) * distance
            )

            if is_off_road(sensor_x, sensor_y):
                value = 1
            else:
                value = 0

            sensor_values.append(value)

            sensor_points.append(
                (
                    sensor_x,
                    sensor_y,
                    value
                )
            )

    return sensor_values, sensor_points, origin_x, origin_y


# -------------------------
# FŐ PROGRAM
# -------------------------

running = True

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    left_speed = 0
    right_speed = 0

    # -------------------------
    # BILLENTYŰZETES VEZÉRLÉS
    # -------------------------

    if keys[pygame.K_w]:
        left_speed = 150
        right_speed = 150

    if keys[pygame.K_a]:
        left_speed = 70
        right_speed = 150

    if keys[pygame.K_d]:
        left_speed = 150
        right_speed = 70


    # -------------------------
    # MOZGÁS
    # -------------------------

    speed = (
        left_speed + right_speed
    ) / 2

    angular_speed = (
        left_speed - right_speed
    ) / wheel_distance

    angle += angular_speed * dt

    x += math.cos(angle) * speed * dt
    y += math.sin(angle) * speed * dt


    # -------------------------
    # SENSOROK
    # -------------------------

    (
        sensor_values,
        sensor_points,
        sensor_origin_x,
        sensor_origin_y
    ) = read_sensors(x, y, angle)


    # -------------------------
    # HÁTTÉR
    # -------------------------

    screen.blit(background, (0, 0))


    # -------------------------
    # SENSOROK KIRAJZOLÁSA
    # -------------------------

    for sensor_x, sensor_y, value in sensor_points:

        # A vonal csak vizualizáció
        pygame.draw.line(
            screen,
            (100, 100, 100),
            (sensor_origin_x, sensor_origin_y),
            (sensor_x, sensor_y),
            1
        )

        # 0 = út -> zöld pont
        # 1 = fű -> piros pont

        if value == 1:
            sensor_color = (255, 0, 0)
        else:
            sensor_color = (0, 255, 0)

        pygame.draw.circle(
            screen,
            sensor_color,
            (int(sensor_x), int(sensor_y)),
            SENSOR_RADIUS
        )


    # -------------------------
    # AUTÓ
    # -------------------------

    car_length = 50
    car_width = 30

    car_surface = pygame.Surface(
        (car_length, car_width),
        pygame.SRCALPHA
    )

    # PIROS AUTÓ
    car_surface.fill((220, 20, 20))

    rotated_car = pygame.transform.rotate(
        car_surface,
        -math.degrees(angle)
    )

    rect = rotated_car.get_rect(
        center=(int(x), int(y))
    )

    screen.blit(rotated_car, rect)

    pygame.display.flip()


pygame.quit()
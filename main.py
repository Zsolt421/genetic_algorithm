import pygame
import math
import os
pygame.init()

WIDTH = 1000
HEIGHT = 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
generation_counter = 1
pygame.display.set_caption(f"Iteration: {generation_counter}")
FPS = 60

folder = os.path.dirname(__file__)

background = pygame.image.load(
    os.path.join(folder, "track.png")
)

background = pygame.transform.scale(
    background, (WIDTH, HEIGHT)
)

# -------------------------
# CAR APPEARANCE AND SETTINGS
# -------------------------

car_length = 50
car_width = 30

car_surface = pygame.Surface(
    (car_length, car_width),
    pygame.SRCALPHA
)

car_surface.fill((220, 20, 20))

# -------------------------
# CAR MOVEMENT SETTINGS
# -------------------------

x = WIDTH / 2
y = HEIGHT / 2 - 10

# 0 = facing right
angle = math.radians(-45)

wheel_distance = 40

MAX_SPEED = 150
TURN_SPEED = 60

## main loop

def main():
    global x, y, angle
    clock = pygame.time.Clock()
    run = True

    while run:
        dt = clock.tick(FPS)/1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

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

        angular_speed = (
            left_speed - right_speed
        ) / wheel_distance

        angle += angular_speed * dt

        x += math.cos(angle) * speed * dt
        y += math.sin(angle) * speed * dt
        

        # Rotate the original car surface
        rotated_car = pygame.transform.rotate(
            car_surface,
            -math.degrees(angle)
        )

        # Put the center of the rotated car at x, y
        rect = rotated_car.get_rect(
            center=(int(x), int(y))
        )

        # Draw background
        SCREEN.blit(background, (0, 0))
        # Draw car
        SCREEN.blit(rotated_car, rect)

        # Show finished frame
        pygame.display.flip()      

    pygame.quit()


if __name__ == "__main__":
    main()
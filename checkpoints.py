import numpy as np
import pygame

#ezek a centerline pontok amikből majd a vonal lesz
pygame.init()
screen = pygame.display.set_mode((800, 600))
track_image = pygame.image.load("round_track.png")  # a pálya képfájlja

centerline_points = []
running = True

while running:
  screen.blit(track_image, (0, 0))  #kirajzoljuk a pályát

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    # Ha bal egérgombbal rákattintasz a képre:
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
      pos = pygame.mouse.get_pos()  # Megkapjuk az egér X, Y koordinátáját
      centerline_points.append(pos) # hozzáadja a listához
      print(f"Pont felvéve: {pos}")  # Kiírja a konzolra, amit másolhatsz is!

  # Kirajzoljuk a eddig letett pontokat, hogy lásd őket
  for p in centerline_points:
    pygame.draw.circle(screen, (255, 0, 0), p, 5)

  pygame.display.flip()

pygame.quit()
print("\nA végleges pontlistád:\n", centerline_points)




# Tegyük fel, hogy van egy listád a középvonal pontjairól: centerline_points
def generate_checkpoints(centerline_points, track_width = 60): #track witdh mennyi?
  checkpoints = []

  for i in range(len(centerline_points)):
    p1 = centerline_points[i]
    # Az előző vagy következő pontból megnézzük a irányt
    p2 = centerline_points[(i + 1) % len(centerline_points)] # p1 és p2 összeköti, % len(..) pedig megmondja, hogy az utolsó után az elsőt vedd 

    # Irányvektor
    dx = p2[0] - p1[0] #elv kiszámítja az egymást követő pontok távolságát
    dy = p2[1] - p1[1]
    length = np.hypot(dx, dy)

    # Egységvektor
    ux, uy = dx / length, dy / length

    # Merőlegesvektor (90 fokkal elforgatva)
    nx, ny = -uy, ux

    # A checkpoint bal és jobb széle (kapu a pályán)
    half_width = track_width / 2
    left_point = (p1[0] + nx * half_width, p1[1] + ny * half_width)
    right_point = (p1[0] - nx * half_width, p1[1] - ny * half_width)

    # Eltároljuk a kaput (két pontból álló szakasz)
    checkpoints.append((left_point, right_point))

  return checkpoints
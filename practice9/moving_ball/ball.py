import pygame
import sys

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
STEP = 20

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Moving Ball")
    clock = pygame.time.Clock()

    radius = 25
    x = WIDTH // 2
    y = HEIGHT // 2

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if x - STEP - radius >= 0:
                        x -= STEP

                elif event.key == pygame.K_RIGHT:
                    if x + STEP + radius <= WIDTH:
                        x += STEP

                elif event.key == pygame.K_UP:
                    if y - STEP - radius >= 0:
                        y -= STEP

                elif event.key == pygame.K_DOWN:
                    if y + STEP + radius <= HEIGHT:
                        y += STEP

        screen.fill(WHITE)
        pygame.draw.circle(screen, RED, (x, y), radius)
        pygame.display.flip()

    pygame.quit()
    sys.exit()
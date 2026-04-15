import pygame
import datetime
import math
import sys

WIDTH, HEIGHT = 600, 600
CENTER = (WIDTH // 2, HEIGHT // 2)

def run_clock():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mickey Clock")

    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))

        now = datetime.datetime.now()
        minute = now.minute
        second = now.second

        minute_angle = minute * 6
        second_angle = second * 6

        def draw_hand(angle, length, color, width):
            rad = math.radians(angle - 90)
            x = CENTER[0] + math.cos(rad) * length
            y = CENTER[1] + math.sin(rad) * length
            pygame.draw.line(screen, color, CENTER, (x, y), width)

        # Draw hands
        draw_hand(minute_angle, 150, (0, 0, 255), 8)   # blue = minute
        draw_hand(second_angle, 180, (255, 0, 0), 5)   # red = second

        # Center dot
        pygame.draw.circle(screen, (0, 0, 0), CENTER, 8)

        pygame.display.flip()

    pygame.quit()
    sys.exit()
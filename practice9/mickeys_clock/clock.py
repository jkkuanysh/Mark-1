import pygame
import datetime
import math
import sys
import os

WIDTH, HEIGHT = 600, 600
CENTER = (WIDTH // 2, HEIGHT // 2)

def run_clock():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mickey Clock")

    clock = pygame.time.Clock()



    # Загружаем фон
    background_path = os.path.join("images", "background.png")
    background = pygame.image.load(background_path)
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Рисуем фон
        screen.blit(background, (0, 0))

        # Берем текущее время
        now = datetime.datetime.now()
        minute = now.minute
        second = now.second

        # Переводим время в угол
        minute_angle = minute * 6
        second_angle = second * 6

        def draw_hand(angle, length, color, width):
            rad = math.radians(angle - 90)
            x = CENTER[0] + math.cos(rad) * length
            y = CENTER[1] + math.sin(rad) * length
            pygame.draw.line(screen, color, CENTER, (x, y), width)

        # Правая рука = минуты
        draw_hand(minute_angle, 150, (0, 0, 255), 8)

        # Левая рука = секунды
        draw_hand(second_angle, 180, (255, 0, 0), 5)

        # Точка в центре
        pygame.draw.circle(screen, (0, 0, 0), CENTER, 8)

        pygame.display.flip()

    pygame.quit()
    sys.exit()
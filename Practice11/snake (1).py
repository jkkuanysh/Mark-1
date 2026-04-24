import pygame
import random
import sys

pygame.init()

# ---------------- SETTINGS ----------------
WIDTH, HEIGHT = 600, 500
CELL_SIZE = 20
HUD_HEIGHT = 100

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game - Full Version")

clock = pygame.time.Clock()

# Colors
WHITE = (245, 245, 245)
BLACK = (30, 30, 30)
GREEN = (0, 180, 0)
RED = (220, 0, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 200, 0)
GRAY = (210, 210, 210)

font = pygame.font.SysFont("Arial", 22)
big_font = pygame.font.SysFont("Arial", 42)

# ---------------- GAME STATE ----------------
def reset_game():
    global snake, dx, dy, score, level, foods_eaten, speed, food, paused

    snake = [(100, 200), (80, 200), (60, 200)]
    dx, dy = CELL_SIZE, 0

    score = 0
    level = 1
    foods_eaten = 0
    speed = 8

    paused = False

    return spawn_food()


# ---------------- FOOD ----------------
def spawn_food():
    global food_weight, food_color, food_spawn_time

    while True:
        x = random.randrange(0, WIDTH, CELL_SIZE)
        y = random.randrange(HUD_HEIGHT, HEIGHT, CELL_SIZE)
        if (x, y) not in snake:
            break

    food_weight = random.choice([1, 2, 3])

    if food_weight == 1:
        food_color = RED
    elif food_weight == 2:
        food_color = YELLOW
    else:
        food_color = BLUE

    food_spawn_time = pygame.time.get_ticks()
    return (x, y)


# ---------------- DRAW ----------------
def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    rect.center = (x, y) if center else (x, y)
    screen.blit(surface, rect)


def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, HUD_HEIGHT), (x, HEIGHT))
    for y in range(HUD_HEIGHT, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))


def draw_hud():
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, HUD_HEIGHT))

    draw_text(f"Score: {score}", font, BLACK, 10, 10)
    draw_text(f"Level: {level}", font, BLACK, 10, 35)
    draw_text(f"Speed: {speed}", font, BLACK, 10, 60)
    draw_text(f"Food: {food_weight}", font, BLACK, 10, 80)

    # Timer bar
    elapsed = pygame.time.get_ticks() - food_spawn_time
    ratio = max(0, (5000 - elapsed) / 5000)

    pygame.draw.rect(screen, RED, (WIDTH - 220, 40, int(200 * ratio), 20))
    pygame.draw.rect(screen, BLACK, (WIDTH - 220, 40, 200, 20), 2)


# ---------------- SCREENS ----------------
def start_screen():
    screen.fill(WHITE)
    draw_text("SNAKE GAME", big_font, BLACK, WIDTH // 2, HEIGHT // 2 - 40, True)
    draw_text("Press any key to start", font, BLACK, WIDTH // 2, HEIGHT // 2 + 20, True)
    pygame.display.flip()

    wait_for_key()


def game_over_screen():
    screen.fill(WHITE)
    draw_text("GAME OVER", big_font, RED, WIDTH // 2, HEIGHT // 2 - 60, True)
    draw_text(f"Score: {score}", font, BLACK, WIDTH // 2, HEIGHT // 2, True)
    draw_text(f"Level: {level}", font, BLACK, WIDTH // 2, HEIGHT // 2 + 40, True)
    draw_text("Press any key to exit", font, BLACK, WIDTH // 2, HEIGHT // 2 + 90, True)
    pygame.display.flip()

    wait_for_key()


def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return


# ---------------- GAME LOOP ----------------
start_screen()
food = reset_game()

running = True
while running:
    clock.tick(speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused

            if not paused:
                if event.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -CELL_SIZE
                elif event.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, CELL_SIZE
                elif event.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -CELL_SIZE, 0
                elif event.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = CELL_SIZE, 0

    if paused:
        draw_text("PAUSED", big_font, BLACK, WIDTH // 2, HEIGHT // 2, True)
        pygame.display.flip()
        continue

    # Move
    head = (snake[0][0] + dx, snake[0][1] + dy)

    # Collisions
    if (
        head[0] < 0 or head[0] >= WIDTH or
        head[1] < HUD_HEIGHT or head[1] >= HEIGHT or
        head in snake
    ):
        break

    snake.insert(0, head)

    if head == food:
        score += food_weight
        foods_eaten += 1

        # Level system
        new_level = foods_eaten // 4 + 1
        if new_level != level:
            level = new_level 

            
            speed += 2

        food = spawn_food()
    else:
        snake.pop()

    # Food timer
    if pygame.time.get_ticks() - food_spawn_time > 5000:
        food = spawn_food()

    # Draw
    screen.fill(WHITE)
    draw_grid()
    draw_hud()

    for s in snake:
        pygame.draw.rect(screen, GREEN, (*s, CELL_SIZE, CELL_SIZE))

    pygame.draw.rect(screen, food_color, (*food, CELL_SIZE, CELL_SIZE))

    pygame.display.flip()

# End
game_over_screen()
pygame.quit()
import random
import pygame

# Initialize pygame
pygame.init()

# Screen and grid settings
CELL = 20
COLS = 30
ROWS = 25
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 11 - Snake")
clock = pygame.time.Clock()

# Colors
BLACK = (20, 20, 20)
WHITE = (245, 245, 245)
GREEN = (40, 200, 90)
DARK_GREEN = (30, 150, 70)
RED = (220, 70, 70)
ORANGE = (255, 165, 0)
PURPLE = (150, 80, 220)
GRAY = (80, 80, 80)

# Fonts
font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 42, bold=True)

# Weighted food settings: value -> lifetime in frames
FOOD_TYPES = {
    1: {"color": RED, "lifetime": 420},
    2: {"color": ORANGE, "lifetime": 300},
    3: {"color": PURPLE, "lifetime": 220},
}


def random_free_cell(snake):
    """Return a random cell that is not occupied by the snake."""
    while True:
        position = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if position not in snake:
            return position


class Food:
    """Food has weight/value and disappears after some time."""

    def __init__(self, snake):
        self.respawn(snake)

    def respawn(self, snake):
        self.value = random.choice([1, 1, 1, 2, 2, 3])
        self.position = random_free_cell(snake)
        self.timer = FOOD_TYPES[self.value]["lifetime"]
        self.max_timer = self.timer

    def update(self, snake):
        self.timer -= 1
        if self.timer <= 0:
            self.respawn(snake)

    def draw(self, surface):
        x, y = self.position
        rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
        pygame.draw.rect(surface, FOOD_TYPES[self.value]["color"], rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, rect, 2, border_radius=5)

        # Show the value inside the food block.
        text = font.render(str(self.value), True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)



def draw_grid():
    """Draw grid lines to make the board easier to see."""
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))



def draw_snake(snake):
    """Draw the snake body."""
    for index, (x, y) in enumerate(snake):
        rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
        color = DARK_GREEN if index == 0 else GREEN
        pygame.draw.rect(screen, color, rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, rect, 1, border_radius=5)



def draw_ui(score, food, speed):
    """Show score, speed, and food timer."""
    score_text = font.render(f"Score: {score}", True, WHITE)
    speed_text = font.render(f"Speed: {speed}", True, WHITE)
    timer_text = font.render(f"Food timer: {food.timer // 60}s", True, WHITE)
    info_text = font.render("Food values: red=1 orange=2 purple=3", True, WHITE)

    screen.blit(score_text, (10, 10))
    screen.blit(speed_text, (10, 40))
    screen.blit(timer_text, (10, 70))
    screen.blit(info_text, (10, HEIGHT - 35))



def game_over_screen(score):
    """Display game over screen."""
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(190)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    text1 = big_font.render("GAME OVER", True, WHITE)
    text2 = font.render(f"Final score: {score}", True, WHITE)
    text3 = font.render("Press R to restart or ESC to quit", True, WHITE)

    screen.blit(text1, text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
    screen.blit(text2, text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))
    screen.blit(text3, text3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 55)))
    pygame.display.flip()



def main():
    """Main snake game loop."""
    while True:
        snake = [(10, 10), (9, 10), (8, 10)]
        direction = (1, 0)
        next_direction = direction
        score = 0
        speed = 8
        food = Food(snake)
        game_over = False

        while not game_over:
            clock.tick(speed)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and direction != (0, 1):
                        next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN and direction != (0, -1):
                        next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT and direction != (1, 0):
                        next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                        next_direction = (1, 0)

            direction = next_direction
            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            # Border collision check.
            if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
                game_over = True
                continue

            # Self collision check.
            if new_head in snake[:-1]:
                game_over = True
                continue

            snake.insert(0, new_head)

            # Eat food and grow according to its value/weight.
            if new_head == food.position:
                score += food.value
                for _ in range(food.value - 1):
                    snake.append(snake[-1])
                food.respawn(snake)
            else:
                snake.pop()

            # Update disappearing food timer.
            food.update(snake)

            screen.fill(BLACK)
            draw_grid()
            draw_snake(snake)
            food.draw(screen)
            draw_ui(score, food, speed)
            pygame.display.flip()

        waiting = True
        while waiting:
            game_over_screen(score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        raise SystemExit


if __name__ == "__main__":
    main()

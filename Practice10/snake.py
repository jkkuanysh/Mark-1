import random
import sys
import pygame

# ---------------------------
# Snake Game - Practice 10
# Features:
# - Border/wall collision
# - Food never appears on a wall or snake body
# - Levels
# - Speed increases each level
# - Score and level counters
# - Commented code
# ---------------------------

pygame.init()

# Grid settings
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
WIDTH = GRID_WIDTH * CELL_SIZE
HEIGHT = GRID_HEIGHT * CELL_SIZE
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 10 - Snake")
CLOCK = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 80)
DARK_GREEN = (0, 120, 50)
RED = (220, 50, 50)
GRAY = (90, 90, 90)
BLUE = (80, 140, 255)

FONT = pygame.font.SysFont("Arial", 24)
BIG_FONT = pygame.font.SysFont("Arial", 40, bold=True)

# Create a simple wall border inside the field
# Snake must not touch it.
WALLS = set()
for x in range(GRID_WIDTH):
    WALLS.add((x, 0))
    WALLS.add((x, GRID_HEIGHT - 1))
for y in range(GRID_HEIGHT):
    WALLS.add((0, y))
    WALLS.add((GRID_WIDTH - 1, y))


class Snake:
    """Snake object stores the body and movement direction."""

    def __init__(self):
        self.body = [(8, 10), (7, 10), (6, 10)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.grow = False

    def change_direction(self, new_direction):
        # Prevent immediate reverse direction
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.next_direction = new_direction

    def move(self):
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)

        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def head(self):
        return self.body[0]

    def collided_with_self(self):
        return self.head() in self.body[1:]

    def draw(self, surface):
        for i, (x, y) in enumerate(self.body):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(surface, color, rect, border_radius=4)
            pygame.draw.rect(surface, BLACK, rect, 1, border_radius=4)


class Food:
    """Food chooses a random free cell that is not inside walls or snake."""

    def __init__(self, snake_body):
        self.position = self.random_position(snake_body)

    def random_position(self, snake_body):
        free_cells = []
        for x in range(1, GRID_WIDTH - 1):
            for y in range(1, GRID_HEIGHT - 1):
                cell = (x, y)
                if cell not in WALLS and cell not in snake_body:
                    free_cells.append(cell)
        return random.choice(free_cells)

    def respawn(self, snake_body):
        self.position = self.random_position(snake_body)

    def draw(self, surface):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, RED, rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, rect, 1, border_radius=10)


def draw_board(score, level):
    SCREEN.fill(BLACK)

    # Draw walls
    for x, y in WALLS:
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(SCREEN, GRAY, rect)

    # Draw HUD text
    score_text = FONT.render(f"Score: {score}", True, WHITE)
    level_text = FONT.render(f"Level: {level}", True, BLUE)
    SCREEN.blit(score_text, (10, 8))
    SCREEN.blit(level_text, (WIDTH - 110, 8))


def show_game_over(score, level):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    SCREEN.blit(overlay, (0, 0))

    lines = [
        BIG_FONT.render("GAME OVER", True, WHITE),
        FONT.render(f"Score: {score}", True, WHITE),
        FONT.render(f"Level: {level}", True, WHITE),
        FONT.render("Press R to restart or ESC to quit", True, WHITE),
    ]

    y = HEIGHT // 2 - 90
    for line in lines:
        rect = line.get_rect(center=(WIDTH // 2, y))
        SCREEN.blit(line, rect)
        y += 45

    pygame.display.update()


def main():
    snake = Snake()
    food = Food(snake.body)

    score = 0
    foods_eaten = 0
    level = 1
    speed = 8
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction((1, 0))
                elif game_over and event.key == pygame.K_r:
                    main()
                elif game_over and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if not game_over:
            snake.move()
            head = snake.head()

            # Check if snake leaves playing area
            if not (0 <= head[0] < GRID_WIDTH and 0 <= head[1] < GRID_HEIGHT):
                game_over = True

            # Check collision with border walls
            if head in WALLS:
                game_over = True

            # Check collision with itself
            if snake.collided_with_self():
                game_over = True

            # Check if food is eaten
            if head == food.position:
                snake.grow = True
                score += 10
                foods_eaten += 1
                food.respawn(snake.body)

                # Increase level every 4 foods
                new_level = foods_eaten // 4 + 1
                if new_level > level:
                    level = new_level
                    speed += 2

            draw_board(score, level)
            food.draw(SCREEN)
            snake.draw(SCREEN)
            pygame.display.update()
            CLOCK.tick(speed)
        else:
            show_game_over(score, level)
            CLOCK.tick(15)


if __name__ == "__main__":
    main()

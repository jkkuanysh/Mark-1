import random
import pygame

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 500, 700
ROAD_LEFT, ROAD_RIGHT = 80, 420
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 11 - Racer")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (60, 60, 60)
YELLOW = (255, 220, 0)
RED = (220, 50, 50)
BLUE = (40, 110, 255)
GREEN = (40, 200, 90)
PURPLE = (155, 70, 220)

# Fonts
font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 42, bold=True)

# Game constants
BASE_ENEMY_SPEED = 6
PLAYER_SPEED = 7
COIN_SPAWN_DELAY = 45
COINS_FOR_SPEED_UP = 5  # N coins needed to increase enemy speed
ENEMY_SPEED_STEP = 1
MAX_ENEMY_SPEED = 15


class Player:
    """Player car controlled by left/right arrow keys."""

    def __init__(self):
        self.width = 50
        self.height = 90
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        # Keep the player on the road
        if self.rect.left < ROAD_LEFT:
            self.rect.left = ROAD_LEFT
        if self.rect.right > ROAD_RIGHT:
            self.rect.right = ROAD_RIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, (self.rect.x + 10, self.rect.y + 12, 30, 20), border_radius=4)
        pygame.draw.rect(surface, BLACK, (self.rect.x + 8, self.rect.bottom - 18, 12, 10), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.rect.right - 20, self.rect.bottom - 18, 12, 10), border_radius=3)


class Enemy:
    """Enemy car moving downward."""

    def __init__(self, speed):
        self.width = 50
        self.height = 90
        self.speed = speed
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(
            random.randint(ROAD_LEFT, ROAD_RIGHT - self.width),
            random.randint(-500, -90),
            self.width,
            self.height,
        )

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.reset()

    def set_speed(self, speed):
        self.speed = speed

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, (self.rect.x + 10, self.rect.y + 12, 30, 20), border_radius=4)
        pygame.draw.rect(surface, BLACK, (self.rect.x + 8, self.rect.bottom - 18, 12, 10), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.rect.right - 20, self.rect.bottom - 18, 12, 10), border_radius=3)


class Coin:
    """Coin with weight/value. Different values give different points."""

    def __init__(self):
        self.radius = 14
        self.weights = [1, 2, 3]
        self.colors = {1: YELLOW, 2: GREEN, 3: PURPLE}
        self.value = 1
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.respawn()

    def respawn(self):
        self.value = random.choice(self.weights)
        self.rect = pygame.Rect(
            random.randint(ROAD_LEFT + 10, ROAD_RIGHT - self.radius * 2 - 10),
            random.randint(-700, -80),
            self.radius * 2,
            self.radius * 2,
        )

    def update(self, speed):
        self.rect.y += speed
        if self.rect.top > HEIGHT:
            self.respawn()

    def draw(self, surface):
        center = self.rect.center
        pygame.draw.circle(surface, self.colors[self.value], center, self.radius)
        pygame.draw.circle(surface, BLACK, center, self.radius, 2)
        text = font.render(str(self.value), True, BLACK)
        text_rect = text.get_rect(center=center)
        surface.blit(text, text_rect)


def draw_background(line_offset):
    """Draw the road and moving lane lines."""
    screen.fill((20, 130, 20))
    pygame.draw.rect(screen, GRAY, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))

    # Side borders
    pygame.draw.line(screen, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
    pygame.draw.line(screen, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)

    # Middle dashed line
    line_x = WIDTH // 2
    for y in range(-40, HEIGHT, 80):
        pygame.draw.rect(screen, WHITE, (line_x - 5, y + line_offset, 10, 40))


def draw_ui(score, enemy_speed, target_info):
    """Show score and current enemy speed."""
    score_text = font.render(f"Coins: {score}", True, WHITE)
    speed_text = font.render(f"Enemy speed: {enemy_speed}", True, WHITE)
    info_text = font.render(target_info, True, WHITE)
    legend = font.render("Coin values: yellow=1 green=2 purple=3", True, WHITE)

    screen.blit(score_text, (WIDTH - score_text.get_width() - 15, 10))
    screen.blit(speed_text, (15, 10))
    screen.blit(info_text, (15, 40))
    screen.blit(legend, (15, HEIGHT - 35))


def game_over_screen(score):
    """Display game over message."""
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    text1 = big_font.render("GAME OVER", True, WHITE)
    text2 = font.render(f"Total coins: {score}", True, WHITE)
    text3 = font.render("Press R to restart or ESC to quit", True, WHITE)

    screen.blit(text1, text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
    screen.blit(text2, text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))
    screen.blit(text3, text3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 55)))
    pygame.display.flip()


def main():
    """Main game loop."""
    while True:
        player = Player()
        enemy_speed = BASE_ENEMY_SPEED
        enemy = Enemy(enemy_speed)
        coins = [Coin()]
        coin_spawn_timer = 0
        line_offset = 0
        score = 0
        game_over = False

        while not game_over:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

            keys = pygame.key.get_pressed()
            player.move(keys)
            enemy.update()

            # Spawn extra coins from time to time if there are not many on screen.
            coin_spawn_timer += 1
            if coin_spawn_timer >= COIN_SPAWN_DELAY and len(coins) < 3:
                coins.append(Coin())
                coin_spawn_timer = 0

            for coin in coins:
                coin.update(enemy_speed)
                if player.rect.colliderect(coin.rect):
                    score += coin.value
                    coin.respawn()

                    # Increase enemy speed every time player reaches N coins.
                    level_speed = BASE_ENEMY_SPEED + (score // COINS_FOR_SPEED_UP) * ENEMY_SPEED_STEP
                    enemy_speed = min(level_speed, MAX_ENEMY_SPEED)
                    enemy.set_speed(enemy_speed)

            # Check collision with enemy car.
            if player.rect.colliderect(enemy.rect):
                game_over = True

            line_offset = (line_offset + enemy_speed) % 80

            draw_background(line_offset)
            player.draw(screen)
            enemy.draw(screen)
            for coin in coins:
                coin.draw(screen)

            remaining = COINS_FOR_SPEED_UP - (score % COINS_FOR_SPEED_UP)
            if remaining == COINS_FOR_SPEED_UP:
                remaining = 0
            target_info = f"Next speed up in: {remaining} coin(s)" if remaining else "Speed increased!"
            draw_ui(score, enemy_speed, target_info)
            pygame.display.flip()

        # Simple restart loop after losing.
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
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        raise SystemExit


if __name__ == "__main__":
    main()

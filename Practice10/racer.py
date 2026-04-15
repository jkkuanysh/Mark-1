import random
import sys
import pygame

# ---------------------------
# Racer Game - Practice 10
# Features:
# - Player car movement
# - Enemy cars
# - Randomly appearing coins
# - Coin counter in top-right corner
# - Score increases over time
# - Speed slowly increases
# ---------------------------

pygame.init()

# Screen settings
WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 10 - Racer")
CLOCK = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
YELLOW = (255, 215, 0)
RED = (220, 50, 50)
BLUE = (40, 120, 255)
GREEN = (30, 180, 90)
ROAD_COLOR = (55, 55, 55)
GRASS_COLOR = (20, 120, 20)

# Road settings
ROAD_X = 60
ROAD_WIDTH = WIDTH - 120
LANE_LINE_WIDTH = 6
road_scroll = 0

# Fonts
FONT = pygame.font.SysFont("Arial", 24)
BIG_FONT = pygame.font.SysFont("Arial", 42, bold=True)


class PlayerCar:
    """Player car controlled by left and right arrow keys."""

    def __init__(self):
        self.width = 50
        self.height = 90
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 6
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Keep the car inside the road boundaries
        left_limit = ROAD_X + 10
        right_limit = ROAD_X + ROAD_WIDTH - self.width - 10
        self.rect.x = max(left_limit, min(self.rect.x, right_limit))

    def draw(self, surface):
        # Simple car body
        pygame.draw.rect(surface, BLUE, self.rect, border_radius=10)
        # Windows
        pygame.draw.rect(surface, WHITE, (self.rect.x + 10, self.rect.y + 10, 30, 18), border_radius=4)
        pygame.draw.rect(surface, WHITE, (self.rect.x + 10, self.rect.y + 35, 30, 18), border_radius=4)
        # Wheels
        pygame.draw.rect(surface, BLACK, (self.rect.x - 4, self.rect.y + 10, 8, 18), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.rect.x - 4, self.rect.y + 62, 8, 18), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.rect.x + self.rect.width - 4, self.rect.y + 10, 8, 18), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.rect.x + self.rect.width - 4, self.rect.y + 62, 8, 18), border_radius=3)


class EnemyCar:
    """Enemy cars move downward and respawn at the top."""

    def __init__(self, speed):
        self.width = 50
        self.height = 90
        self.speed = speed
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.respawn(initial=True)

    def respawn(self, initial=False):
        lane_positions = [ROAD_X + 25, WIDTH // 2 - self.width // 2, ROAD_X + ROAD_WIDTH - self.width - 25]
        self.rect.x = random.choice(lane_positions)
        if initial:
            self.rect.y = random.randint(-500, -100)
        else:
            self.rect.y = random.randint(-250, -100)

    def update(self, game_speed):
        self.rect.y += game_speed
        if self.rect.top > HEIGHT:
            self.respawn()

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, (self.rect.x + 10, self.rect.y + 10, 30, 18), border_radius=4)
        pygame.draw.rect(surface, WHITE, (self.rect.x + 10, self.rect.y + 35, 30, 18), border_radius=4)
        pygame.draw.rect(surface, BLACK, (self.rect.x - 4, self.rect.y + 10, 8, 18), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.rect.x - 4, self.rect.y + 62, 8, 18), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.rect.x + self.rect.width - 4, self.rect.y + 10, 8, 18), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.rect.x + self.rect.width - 4, self.rect.y + 62, 8, 18), border_radius=3)


class Coin:
    """Coin appears on the road and can be collected by the player."""

    def __init__(self):
        self.radius = 12
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.active = False
        self.timer = 0
        self.spawn_delay = random.randint(70, 160)

    def spawn(self):
        x = random.randint(ROAD_X + 20, ROAD_X + ROAD_WIDTH - 20 - self.radius * 2)
        y = random.randint(-220, -60)
        self.rect.topleft = (x, y)
        self.active = True

    def update(self, game_speed):
        if self.active:
            self.rect.y += game_speed
            if self.rect.top > HEIGHT:
                self.active = False
                self.timer = 0
                self.spawn_delay = random.randint(70, 160)
        else:
            self.timer += 1
            if self.timer >= self.spawn_delay:
                self.spawn()

    def draw(self, surface):
        if self.active:
            center = self.rect.center
            pygame.draw.circle(surface, YELLOW, center, self.radius)
            pygame.draw.circle(surface, BLACK, center, self.radius, 2)
            pygame.draw.circle(surface, (255, 240, 140), center, 5)


def draw_background():
    """Draw grass, road, and lane markings."""
    global road_scroll

    SCREEN.fill(GRASS_COLOR)
    pygame.draw.rect(SCREEN, ROAD_COLOR, (ROAD_X, 0, ROAD_WIDTH, HEIGHT))

    # Lane lines that move downward to simulate motion
    road_scroll = (road_scroll + 8) % 40
    center_x = WIDTH // 2 - LANE_LINE_WIDTH // 2
    for y in range(-40, HEIGHT, 40):
        pygame.draw.rect(SCREEN, WHITE, (center_x, y + road_scroll, LANE_LINE_WIDTH, 24))


def draw_text(text, font, color, x, y, align_right=False):
    """Helper function to render text."""
    img = font.render(text, True, color)
    rect = img.get_rect()
    if align_right:
        rect.topright = (x, y)
    else:
        rect.topleft = (x, y)
    SCREEN.blit(img, rect)


def show_game_over(score, coins):
    """Display the game over screen."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    SCREEN.blit(overlay, (0, 0))

    draw_text("GAME OVER", BIG_FONT, WHITE, WIDTH // 2 - 120, HEIGHT // 2 - 100)
    draw_text(f"Score: {score}", FONT, WHITE, WIDTH // 2 - 55, HEIGHT // 2 - 30)
    draw_text(f"Coins: {coins}", FONT, WHITE, WIDTH // 2 - 52, HEIGHT // 2 + 10)
    draw_text("Press R to restart or ESC to quit", FONT, WHITE, 45, HEIGHT // 2 + 70)
    pygame.display.update()


def main():
    player = PlayerCar()
    enemies = [EnemyCar(5), EnemyCar(7)]
    coin = Coin()

    score = 0
    coins_collected = 0
    game_speed = 5
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)

            draw_background()

            # Update and draw enemies
            for enemy in enemies:
                enemy.update(game_speed)
                enemy.draw(SCREEN)

                # Collision with enemy ends the game
                if player.rect.colliderect(enemy.rect):
                    game_over = True

            # Update and draw coin
            coin.update(game_speed)
            coin.draw(SCREEN)

            # Coin collection
            if coin.active and player.rect.colliderect(coin.rect):
                coins_collected += 1
                score += 10
                coin.active = False
                coin.timer = 0
                coin.spawn_delay = random.randint(70, 160)

            # Draw player
            player.draw(SCREEN)

            # Score increases with survival time
            score += 1

            # Increase difficulty over time
            if score % 350 == 0:
                game_speed += 1

            # Draw HUD
            draw_text(f"Score: {score}", FONT, WHITE, 12, 10)
            draw_text(f"Coins: {coins_collected}", FONT, WHITE, WIDTH - 12, 10, align_right=True)

            pygame.display.update()
            CLOCK.tick(FPS)
        else:
            show_game_over(score, coins_collected)
            CLOCK.tick(15)


if __name__ == "__main__":
    main()

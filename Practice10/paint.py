import sys
import pygame

# ---------------------------
# Paint Program - Practice 10
# Features:
# - Free draw with mouse
# - Draw rectangle
# - Draw circle
# - Eraser
# - Color selection
# - Keyboard shortcuts
# ---------------------------

pygame.init()

WIDTH, HEIGHT = 1000, 700
TOOLBAR_HEIGHT = 90
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 10 - Paint")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 22)
SMALL_FONT = pygame.font.SysFont("Arial", 18)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 210, 210)
DARK_GRAY = (90, 90, 90)
RED = (220, 50, 50)
GREEN = (40, 170, 90)
BLUE = (50, 110, 220)
YELLOW = (250, 220, 70)
PURPLE = (150, 80, 220)
ORANGE = (255, 140, 40)
PINK = (240, 90, 170)

PALETTE = [BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, PINK, WHITE]

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# Current drawing settings
current_color = BLACK
brush_size = 6
current_tool = "brush"  # brush, rect, circle, eraser

drawing = False
start_pos = None
last_pos = None
preview_surface = None


def draw_toolbar():
    """Draw top toolbar with colors and tool information."""
    pygame.draw.rect(SCREEN, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(SCREEN, DARK_GRAY, (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    # Draw palette boxes
    x = 15
    for color in PALETTE:
        rect = pygame.Rect(x, 18, 36, 36)
        pygame.draw.rect(SCREEN, color, rect)
        border_color = BLUE if color == current_color else BLACK
        pygame.draw.rect(SCREEN, border_color, rect, 3)
        x += 46

    # Tool instructions
    info_lines = [
        f"Tool: {current_tool.upper()}    Size: {brush_size}",
        "Keys: B=brush  R=rectangle  C=circle  E=eraser  +/- change size  SPACE clear",
    ]
    y = 12
    for line in info_lines:
        img = SMALL_FONT.render(line, True, BLACK)
        SCREEN.blit(img, (470, y))
        y += 28


def get_color_from_palette(mouse_pos):
    """Return selected color if user clicked a palette box."""
    x = 15
    for color in PALETTE:
        rect = pygame.Rect(x, 18, 36, 36)
        if rect.collidepoint(mouse_pos):
            return color
        x += 46
    return None


def draw_on_canvas_line(surface, color, pos1, pos2, size):
    """Draw smooth freehand line between two positions."""
    pygame.draw.line(surface, color, pos1, pos2, size)
    pygame.draw.circle(surface, color, pos2, size // 2)


def draw_shape_preview():
    """Show preview of rectangle or circle while dragging."""
    if preview_surface:
        SCREEN.blit(preview_surface, (0, TOOLBAR_HEIGHT))


def make_preview(start, end):
    """Create a preview surface for rectangle or circle."""
    temp = canvas.copy()

    start_canvas = (start[0], start[1] - TOOLBAR_HEIGHT)
    end_canvas = (end[0], end[1] - TOOLBAR_HEIGHT)

    left = min(start_canvas[0], end_canvas[0])
    top = min(start_canvas[1], end_canvas[1])
    width = abs(end_canvas[0] - start_canvas[0])
    height = abs(end_canvas[1] - start_canvas[1])
    rect = pygame.Rect(left, top, width, height)

    if current_tool == "rect":
        pygame.draw.rect(temp, current_color, rect, 0)
    elif current_tool == "circle":
        center = rect.center
        radius = min(rect.width, rect.height) // 2
        pygame.draw.circle(temp, current_color, center, radius, 0)

    return temp


def commit_shape(start, end):
    """Draw final rectangle or circle on the main canvas."""
    global canvas
    canvas = make_preview(start, end)


def main():
    global current_color, brush_size, current_tool, drawing, start_pos, last_pos, preview_surface

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    current_tool = "brush"
                elif event.key == pygame.K_r:
                    current_tool = "rect"
                elif event.key == pygame.K_c:
                    current_tool = "circle"
                elif event.key == pygame.K_e:
                    current_tool = "eraser"
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    brush_size = min(50, brush_size + 1)
                elif event.key == pygame.K_MINUS:
                    brush_size = max(1, brush_size - 1)
                elif event.key == pygame.K_SPACE:
                    canvas.fill(WHITE)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                # Check color selection only inside toolbar area
                if mouse_pos[1] <= TOOLBAR_HEIGHT:
                    chosen = get_color_from_palette(mouse_pos)
                    if chosen is not None:
                        current_color = chosen
                else:
                    drawing = True
                    start_pos = mouse_pos
                    last_pos = (mouse_pos[0], mouse_pos[1] - TOOLBAR_HEIGHT)

                    # Draw a dot immediately for brush/eraser
                    if current_tool == "brush":
                        pygame.draw.circle(canvas, current_color, last_pos, brush_size // 2)
                    elif current_tool == "eraser":
                        pygame.draw.circle(canvas, WHITE, last_pos, brush_size)

            elif event.type == pygame.MOUSEMOTION and drawing:
                mouse_pos = event.pos
                canvas_pos = (mouse_pos[0], mouse_pos[1] - TOOLBAR_HEIGHT)

                # Only allow drawing below toolbar
                if mouse_pos[1] > TOOLBAR_HEIGHT:
                    if current_tool == "brush":
                        draw_on_canvas_line(canvas, current_color, last_pos, canvas_pos, brush_size)
                        last_pos = canvas_pos
                    elif current_tool == "eraser":
                        draw_on_canvas_line(canvas, WHITE, last_pos, canvas_pos, brush_size * 2)
                        last_pos = canvas_pos
                    elif current_tool in ("rect", "circle"):
                        preview_surface = make_preview(start_pos, mouse_pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    drawing = False
                    end_pos = event.pos

                    if current_tool in ("rect", "circle") and end_pos[1] > TOOLBAR_HEIGHT:
                        commit_shape(start_pos, end_pos)
                        preview_surface = None

        # Draw UI and canvas
        SCREEN.fill(WHITE)
        draw_toolbar()

        # Draw current canvas or preview
        if preview_surface is not None and current_tool in ("rect", "circle") and drawing:
            SCREEN.blit(preview_surface, (0, TOOLBAR_HEIGHT))
        else:
            SCREEN.blit(canvas, (0, TOOLBAR_HEIGHT))

        pygame.display.update()
        CLOCK.tick(60)


if __name__ == "__main__":
    main()

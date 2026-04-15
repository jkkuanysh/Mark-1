import math
import pygame

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 700
TOOLBAR_HEIGHT = 90
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 11 - Paint")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
DARK_GRAY = (90, 90, 90)
RED = (220, 60, 60)
GREEN = (50, 180, 80)
BLUE = (70, 100, 230)
YELLOW = (240, 220, 50)
PURPLE = (150, 80, 220)
ORANGE = (255, 165, 0)
CYAN = (0, 180, 180)

# Fonts
font = pygame.font.SysFont("arial", 20)
small_font = pygame.font.SysFont("arial", 16)

# Tool names
TOOLS = ["brush", "eraser", "square", "r_triangle", "eq_triangle", "rhombus"]
COLOR_OPTIONS = [BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, CYAN]

# Drawing area surface
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)


def draw_toolbar(selected_tool, selected_color, brush_size):
    """Draw top toolbar with tools and colors."""
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, DARK_GRAY, (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    x = 10
    for tool in TOOLS:
        rect = pygame.Rect(x, 10, 120, 30)
        color = CYAN if tool == selected_tool else WHITE
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
        label = small_font.render(tool, True, BLACK)
        screen.blit(label, label.get_rect(center=rect.center))
        x += 130

    # Draw color palette.
    x = 15
    for color in COLOR_OPTIONS:
        rect = pygame.Rect(x, 52, 32, 32)
        pygame.draw.rect(screen, color, rect)
        border = 3 if color == selected_color else 1
        pygame.draw.rect(screen, BLACK, rect, border)
        x += 40

    info = font.render(f"Size: {brush_size}   [ and ] to change", True, BLACK)
    screen.blit(info, (WIDTH - 250, 58))



def get_tool_at_pos(pos):
    """Return the selected tool if the mouse clicks a tool button."""
    x, y = pos
    if y > 40:
        return None
    current_x = 10
    for tool in TOOLS:
        rect = pygame.Rect(current_x, 10, 120, 30)
        if rect.collidepoint(pos):
            return tool
        current_x += 130
    return None



def get_color_at_pos(pos):
    """Return the chosen color if the mouse clicks a color box."""
    x = 15
    for color in COLOR_OPTIONS:
        rect = pygame.Rect(x, 52, 32, 32)
        if rect.collidepoint(pos):
            return color
        x += 40
    return None



def canvas_pos(mouse_pos):
    """Convert screen coordinates to canvas coordinates."""
    return mouse_pos[0], mouse_pos[1] - TOOLBAR_HEIGHT



def draw_preview_shape(surface, tool, color, start_pos, end_pos, width):
    """Draw temporary shape preview while dragging."""
    if tool == "square":
        draw_square(surface, color, start_pos, end_pos, width)
    elif tool == "r_triangle":
        draw_right_triangle(surface, color, start_pos, end_pos, width)
    elif tool == "eq_triangle":
        draw_equilateral_triangle(surface, color, start_pos, end_pos, width)
    elif tool == "rhombus":
        draw_rhombus(surface, color, start_pos, end_pos, width)



def draw_square(surface, color, start_pos, end_pos, width):
    """Draw a square using the drag distance."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    side = min(abs(x2 - x1), abs(y2 - y1))
    left = x1 if x2 >= x1 else x1 - side
    top = y1 if y2 >= y1 else y1 - side
    rect = pygame.Rect(left, top, side, side)
    pygame.draw.rect(surface, color, rect, width)



def draw_right_triangle(surface, color, start_pos, end_pos, width):
    """Draw a right triangle using a bounding rectangle."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    points = [(x1, y2), (x1, y1), (x2, y2)]
    pygame.draw.polygon(surface, color, points, width)



def draw_equilateral_triangle(surface, color, start_pos, end_pos, width):
    """Draw an equilateral triangle centered between drag points."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    side = abs(x2 - x1)
    if side < 2:
        return
    height = side * math.sqrt(3) / 2
    left = min(x1, x2)
    base_y = max(y1, y2)
    points = [
        (left, base_y),
        (left + side, base_y),
        (left + side / 2, base_y - height),
    ]
    pygame.draw.polygon(surface, color, points, width)



def draw_rhombus(surface, color, start_pos, end_pos, width):
    """Draw a rhombus using the diagonal points from dragging."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    points = [
        (cx, y1),
        (x2, cy),
        (cx, y2),
        (x1, cy),
    ]
    pygame.draw.polygon(surface, color, points, width)



def main():
    """Main paint program loop."""
    running = True
    selected_tool = "brush"
    selected_color = BLACK
    brush_size = 4
    drawing = False
    shape_start = None
    last_pos = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFTBRACKET:
                    brush_size = max(1, brush_size - 1)
                elif event.key == pygame.K_RIGHTBRACKET:
                    brush_size = min(20, brush_size + 1)
                elif event.key == pygame.K_c:
                    canvas.fill(WHITE)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Select a tool or a color from the toolbar.
                tool = get_tool_at_pos(event.pos)
                color = get_color_at_pos(event.pos)

                if tool:
                    selected_tool = tool
                elif color:
                    selected_color = color
                elif event.pos[1] >= TOOLBAR_HEIGHT:
                    drawing = True
                    shape_start = canvas_pos(event.pos)
                    last_pos = shape_start

                    # Brush and eraser start drawing immediately.
                    if selected_tool == "brush":
                        pygame.draw.circle(canvas, selected_color, shape_start, brush_size)
                    elif selected_tool == "eraser":
                        pygame.draw.circle(canvas, WHITE, shape_start, brush_size * 2)

            elif event.type == pygame.MOUSEBUTTONUP:
                if drawing and shape_start and event.pos[1] >= TOOLBAR_HEIGHT:
                    end_pos = canvas_pos(event.pos)

                    # Draw final geometric shape after mouse release.
                    if selected_tool == "square":
                        draw_square(canvas, selected_color, shape_start, end_pos, brush_size)
                    elif selected_tool == "r_triangle":
                        draw_right_triangle(canvas, selected_color, shape_start, end_pos, brush_size)
                    elif selected_tool == "eq_triangle":
                        draw_equilateral_triangle(canvas, selected_color, shape_start, end_pos, brush_size)
                    elif selected_tool == "rhombus":
                        draw_rhombus(canvas, selected_color, shape_start, end_pos, brush_size)

                drawing = False
                shape_start = None
                last_pos = None

            elif event.type == pygame.MOUSEMOTION and drawing and event.pos[1] >= TOOLBAR_HEIGHT:
                current_pos = canvas_pos(event.pos)

                # Freehand drawing for brush and eraser.
                if selected_tool == "brush":
                    pygame.draw.line(canvas, selected_color, last_pos, current_pos, brush_size * 2)
                elif selected_tool == "eraser":
                    pygame.draw.line(canvas, WHITE, last_pos, current_pos, brush_size * 4)
                last_pos = current_pos

        # Draw the toolbar and current canvas.
        screen.fill(WHITE)
        draw_toolbar(selected_tool, selected_color, brush_size)
        screen.blit(canvas, (0, TOOLBAR_HEIGHT))

        # Show live preview for shapes while dragging.
        if drawing and shape_start and selected_tool in {"square", "r_triangle", "eq_triangle", "rhombus"}:
            preview = canvas.copy()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_y >= TOOLBAR_HEIGHT:
                end_pos = canvas_pos((mouse_x, mouse_y))
                draw_preview_shape(preview, selected_tool, selected_color, shape_start, end_pos, brush_size)
                screen.blit(preview, (0, TOOLBAR_HEIGHT))

        help_text = small_font.render("C = clear canvas", True, BLACK)
        screen.blit(help_text, (WIDTH - 130, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()

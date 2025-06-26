import pygame
import sys
import subprocess

pygame.init()

WIDTH, HEIGHT = 500, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Jump - Main Menu")
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
GRAY = (30, 30, 30)
BLUE = (0, 120, 255)
LIGHT_BLUE = (100, 170, 255)

font = pygame.font.SysFont("Arial", 40)
button_font = pygame.font.SysFont("Arial", 28)

buttons = [
    {"label": "1 Player", "rect": pygame.Rect(150, 120, 200, 50)},
    {"label": "2 Player", "rect": pygame.Rect(150, 190, 200, 50)},
    {"label": "Quit", "rect": pygame.Rect(150, 260, 200, 50)},
]

def draw_buttons(mouse_pos):
    screen.fill(GRAY)
    title = font.render("Tower Jump", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

    for button in buttons:
        color = LIGHT_BLUE if button["rect"].collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(screen, color, button["rect"], border_radius=10)
        label = button_font.render(button["label"], True, WHITE)
        screen.blit(label, (
            button["rect"].x + (button["rect"].width - label.get_width()) // 2,
            button["rect"].y + (button["rect"].height - label.get_height()) // 2
        ))

    pygame.display.flip()

def main_menu():
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        draw_buttons(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["label"] == "1 Player":
                            subprocess.run(["python", "tower_jump_1player.py"])
                        elif button["label"] == "2 Player":
                            subprocess.run(["python", "tower_jump_2player.py"])
                        elif button["label"] == "Quit":
                            pygame.quit()
                            sys.exit()

        clock.tick(FPS)

main_menu()

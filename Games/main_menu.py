import pygame
import os
import sys
import subprocess

# Setup
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Hub")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
BLUE = (0, 120, 255)
font = pygame.font.SysFont("Arial", 28)
small_font = pygame.font.SysFont("Arial", 20)

clock = pygame.time.Clock()
FPS = 60

# Game list
games = [
    {"title": "Tower Jump", "file": "tower_jump_with_menu.py"},
    {"title": "Ship vs Monster", "file": "ship_vs_monster.py"}
]

def draw_menu(selected_index):
    screen.fill(GRAY)
    title = font.render("🎮 Select a Game", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))

    for i, game in enumerate(games):
        color = BLUE if i == selected_index else WHITE
        txt = small_font.render(game["title"], True, color)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 120 + i*40))

    tip = small_font.render("↑ ↓ to Move | ENTER to Play | ESC to Quit", True, WHITE)
    screen.blit(tip, (WIDTH//2 - tip.get_width()//2, HEIGHT - 40))

    pygame.display.flip()

def launch_game(game_file):
    if os.path.exists(game_file):
        subprocess.run([sys.executable, game_file])
    else:
        print(f"[ERROR] File not found: {game_file}")


def main():
    selected = 0
    running = True

    while running:
        clock.tick(FPS)
        draw_menu(selected)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(games)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(games)
                elif event.key == pygame.K_RETURN:
                    launch_game(games[selected]["file"])
                elif event.key == pygame.K_ESCAPE:
                    running = False

    pygame.quit()

if __name__ == "__main__":
    main()

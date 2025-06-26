import pygame
import random
import os
import uuid
import time

pygame.init()

# Window
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Jump")

# Colors
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
SKY = (135, 206, 250)
BLACK = (0, 0, 0)
GOLD = (255, 223, 0)

# Font
font = pygame.font.SysFont("Arial", 20)
big_font = pygame.font.SysFont("Arial", 32)
huge_font = pygame.font.SysFont("Arial", 40, bold=True)

# Clock
clock = pygame.time.Clock()
FPS = 60

# High score
high_score_file = "highscore.txt"
high_score = 0
if os.path.exists(high_score_file):
    with open(high_score_file, "r") as f:
        try:
            high_score = int(f.read())
        except:
            high_score = 0

# Clouds
clouds = []
for _ in range(5):
    side = random.choice(["left", "right"])
    x = -random.randint(100, 400) if side == "left" else WIDTH + random.randint(100, 400)
    y = random.randint(50, 300)
    speed = random.uniform(0.2, 0.5)
    clouds.append([x, y, side, speed])

# Sparkles
sparkles = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "dy": random.uniform(0.2, 0.6)} for _ in range(30)]

def show_loading_screen():
    screen.fill(BLACK)
    txt = big_font.render("Loading...", True, WHITE)
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 20))
    pygame.display.flip()
    time.sleep(2)

def game_loop():
    ball_radius = 15
    ball_x = WIDTH // 2
    ball_y = HEIGHT - ball_radius
    ball_speed_y = 0
    gravity = 0.5
    jump_power = -10

    pw, ph = 80, 10
    platforms = []
    platform_ids = []
    timers = []
    VISIBLE_PLATFORM_LIMIT = 7

    def spawn_platforms():
        while len([p for p in platforms if p.width > 0 and p.y < HEIGHT]) < VISIBLE_PLATFORM_LIMIT:
            max_attempts = 100
            while max_attempts > 0:
                x = random.randint(0, WIDTH - pw)
                if platforms:
                    min_y = min([p.y for p in platforms if p.width > 0])
                    y = min_y - random.randint(60, 100)
                else:
                    y = HEIGHT - 60
                too_close = any(abs(p.x - x) < pw and abs(p.y - y) < 20 for p in platforms)
                if not too_close:
                    platforms.append(pygame.Rect(x, y, pw, ph))
                    platform_ids.append(str(uuid.uuid4()))
                    timers.append(None)
                    break
                max_attempts -= 1

    for _ in range(VISIBLE_PLATFORM_LIMIT):
        spawn_platforms()

    visited = set()
    score = 0
    level = 1
    scroll = 0
    running = True
    game_over = False
    win = False
    opened_gate = False
    show_start = True
    has_touched = False

    global clouds, sparkles

    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if show_start and e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                show_start = False
            if (game_over or (win and opened_gate)) and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: return False
            if win and not opened_gate and e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                opened_gate = True

        if show_start:
            screen.fill(BLACK)
            title = big_font.render("Tower Jump", True, WHITE)
            start_txt = font.render("Press SPACE to Start", True, WHITE)
            quit_txt = font.render("Press Q to Quit", True, WHITE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 50))
            screen.blit(start_txt, (WIDTH//2 - start_txt.get_width()//2, HEIGHT//2 + 10))
            screen.blit(quit_txt, (WIDTH//2 - quit_txt.get_width()//2, HEIGHT//2 + 35))
            pygame.display.flip()
            continue

        if level <= 50:
            screen.fill(GRAY)
        elif level <= 99:
            screen.fill(SKY)
        else:
            screen.fill(WHITE)

        if level > 50:
            for cloud in clouds:
                x, y, side, s = cloud
                pygame.draw.ellipse(screen, WHITE, (x, y, 60, 30))
                cloud[0] += s if side == "left" else -s
                if side == "left" and cloud[0] > WIDTH:
                    cloud[0], cloud[1] = -100, random.randint(50, 300)
                if side == "right" and cloud[0] < -100:
                    cloud[0], cloud[1] = WIDTH + 100, random.randint(50, 300)

        if not win:
            if keys[pygame.K_LEFT]: ball_x -= 5
            if keys[pygame.K_RIGHT]: ball_x += 5
            if ball_x < -ball_radius: ball_x = WIDTH + ball_radius
            if ball_x > WIDTH + ball_radius: ball_x = -ball_radius

        if not win:
            ball_speed_y += gravity * (1 + ((level - 1) // 10) * 0.1)
            ball_y += ball_speed_y

        if ball_y >= HEIGHT - ball_radius:
            if has_touched:
                game_over = True
            else:
                ball_y = HEIGHT - ball_radius
                ball_speed_y = jump_power

        if ball_y < HEIGHT // 3 and ball_speed_y < 0:
            scroll = HEIGHT // 3 - ball_y
            ball_y = HEIGHT // 3
            for i in range(len(platforms)):
                platforms[i].y += scroll
        else:
            scroll = 0

        ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)

        for i, plat in enumerate(platforms):
            if plat.colliderect(ball_rect) and ball_speed_y > 0:
                ball_speed_y = jump_power * (1 + ((level - 1) // 10) * 0.1)
                has_touched = True
                pid = platform_ids[i]
                if pid not in visited:
                    visited.add(pid)
                    score += 10
                    if score // 100 + 1 > level:
                        level += 1
                        if level == 100: win = True
                if level >= 90 and timers[i] is None:
                    timers[i] = pygame.time.get_ticks()

        for i, plat in enumerate(platforms):
            if level >= 90 and timers[i] is not None:
                if pygame.time.get_ticks() - timers[i] > 1000:
                    platforms[i] = pygame.Rect(-100, -100, 0, 0)
                    timers[i] = None
            if platforms[i].width > 0:
                color = BROWN if level < 50 else LIGHT_BROWN
                pygame.draw.rect(screen, color, plat)

        spawn_platforms()

        pygame.draw.circle(screen, (0, 0, 255), (ball_x, int(ball_y)), ball_radius)

        screen.blit(font.render(f"Score: {score}", True, BLACK), (10, 10))
        screen.blit(font.render(f"Level: {level}", True, BLACK), (10, 30))
        screen.blit(font.render(f"High Score: {high_score}", True, BLACK), (10, 50))
        if level >= 90 and not win:
            screen.blit(font.render("⚠ Platforms disappear!", True, (200, 0, 0)), (10, 70))

        if game_over:
            game_over_txt = big_font.render("Game Over", True, (255, 0, 0))
            restart_txt = font.render("Press R to Restart", True, BLACK)
            quit_txt = font.render("Press Q to Quit", True, BLACK)
            screen.blit(game_over_txt, (WIDTH // 2 - game_over_txt.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 0))
            screen.blit(quit_txt, (WIDTH // 2 - quit_txt.get_width() // 2, HEIGHT // 2 + 25))

        if win and not opened_gate:
            pygame.draw.rect(screen, (150, 75, 0), (WIDTH // 2 - 25, HEIGHT // 2 - 60, 50, 100))
            gate_txt = font.render("Press ENTER to open gate", True, BLACK)
            screen.blit(gate_txt, (WIDTH // 2 - gate_txt.get_width() // 2, HEIGHT // 2 + 50))

        if win and opened_gate:
            screen.fill(WHITE)
            for sparkle in sparkles:
                pygame.draw.circle(screen, GOLD, (int(sparkle["x"]), int(sparkle["y"])), 3)
                sparkle["y"] += sparkle["dy"]
                if sparkle["y"] > HEIGHT:
                    sparkle["y"], sparkle["x"] = 0, random.randint(0, WIDTH)

            pygame.draw.circle(screen, (0, 0, 255), (WIDTH // 2, HEIGHT // 2 - 20), ball_radius)

            welcome_txt = huge_font.render("Welcome to Heaven", True, BLACK)
            king_txt = big_font.render("Tower King!", True, GOLD)
            restart_txt = font.render("Press R to Restart", True, BLACK)
            quit_txt = font.render("Press Q to Quit", True, BLACK)

            screen.blit(welcome_txt, (WIDTH // 2 - welcome_txt.get_width() // 2, HEIGHT // 2 + 10))
            screen.blit(king_txt, (WIDTH // 2 - king_txt.get_width() // 2, HEIGHT // 2 + 50))
            screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 90))
            screen.blit(quit_txt, (WIDTH // 2 - quit_txt.get_width() // 2, HEIGHT // 2 + 115))

        pygame.display.flip()

        if (game_over or (win and opened_gate)) and score > high_score:
            with open(high_score_file, "w") as f:
                f.write(str(score))

    return False

# Main
show_loading_screen()
while game_loop():
    pass
pygame.quit()

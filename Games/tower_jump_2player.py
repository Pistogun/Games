import pygame
import random
import os
import uuid
import time

pygame.init()
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Jump - Two Player")

WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
SKY = (135, 206, 250)
BLACK = (0, 0, 0)
GOLD = (255, 223, 0)

font = pygame.font.SysFont("Arial", 20)
big_font = pygame.font.SysFont("Arial", 32)
huge_font = pygame.font.SysFont("Arial", 40, bold=True)

clock = pygame.time.Clock()
FPS = 60

score_files = {
    "Player 1": "highscore_player1.txt",
    "Player 2": "highscore_player2.txt"
}

def load_high_score(name):
    try:
        with open(score_files[name], 'r') as f:
            return int(f.read())
    except:
        return 0

def save_high_score(name, score):
    with open(score_files[name], 'w') as f:
        f.write(str(score))

def get_overall_high_score():
    scores = [load_high_score("Player 1"), load_high_score("Player 2")]
    return max(scores)

class Player:
    def __init__(self, name, x_offset, left_key, right_key):
        self.name = name
        self.offset = x_offset
        self.left_key = left_key
        self.right_key = right_key
        self.high_score = load_high_score(name)
        self.reset()

    def reset(self):
        self.ball_radius = 15
        self.ball_x = self.offset + 200
        self.ball_y = HEIGHT - self.ball_radius
        self.ball_speed_y = 0
        self.gravity = 0.5
        self.jump_power = -10
        self.score = 0
        self.level = 1
        self.has_touched = False
        self.win = False
        self.opened_gate = False
        self.game_over = False
        self.visited = set()
        self.scroll = 0

        self.platforms = []
        self.platform_ids = []
        self.timers = []
        for _ in range(7):
            self.spawn_platform()

    def spawn_platform(self):
        pw, ph = 80, 10
        while True:
            x = random.randint(0, 400 - pw)
            y = HEIGHT - 60 if not self.platforms else min(p.y for p in self.platforms) - random.randint(60, 100)
            too_close = any(abs(p.x - x) < pw and abs(p.y - y) < 20 for p in self.platforms)
            if not too_close:
                self.platforms.append(pygame.Rect(x + self.offset, y, pw, ph))
                self.platform_ids.append(str(uuid.uuid4()))
                self.timers.append(None)
                break

    def update(self, keys):
        if self.win:
            return

        if keys[self.left_key]:
            self.ball_x -= 5
        if keys[self.right_key]:
            self.ball_x += 5
        if self.ball_x < self.offset - self.ball_radius:
            self.ball_x = self.offset + 400 + self.ball_radius
        if self.ball_x > self.offset + 400 + self.ball_radius:
            self.ball_x = self.offset - self.ball_radius

        self.ball_speed_y += self.gravity * (1 + ((self.level - 1) // 10) * 0.1)
        self.ball_y += self.ball_speed_y

        if self.ball_y >= HEIGHT - self.ball_radius:
            if self.has_touched:
                self.game_over = True
            else:
                self.ball_y = HEIGHT - self.ball_radius
                self.ball_speed_y = self.jump_power

        if self.ball_y < HEIGHT // 3 and self.ball_speed_y < 0:
            self.scroll = HEIGHT // 3 - self.ball_y
            self.ball_y = HEIGHT // 3
            for i in range(len(self.platforms)):
                self.platforms[i].y += self.scroll
        else:
            self.scroll = 0

        ball_rect = pygame.Rect(self.ball_x - self.ball_radius, self.ball_y - self.ball_radius, self.ball_radius * 2, self.ball_radius * 2)

        for i, plat in enumerate(self.platforms):
            if plat.colliderect(ball_rect) and self.ball_speed_y > 0:
                self.ball_speed_y = self.jump_power * (1 + ((self.level - 1) // 10) * 0.1)
                self.has_touched = True
                pid = self.platform_ids[i]
                if pid not in self.visited:
                    self.visited.add(pid)
                    self.score += 10
                    if self.score // 100 + 1 > self.level:
                        self.level += 1
                        if self.level == 100:
                            self.win = True
                if self.level >= 90 and self.timers[i] is None:
                    self.timers[i] = pygame.time.get_ticks()

        for i in range(len(self.platforms)):
            if self.level >= 90 and self.timers[i] is not None:
                if pygame.time.get_ticks() - self.timers[i] > 1000:
                    self.platforms[i] = pygame.Rect(-100, -100, 0, 0)
                    self.timers[i] = None

        while len([p for p in self.platforms if p.width > 0 and p.y < HEIGHT]) < 7:
            self.spawn_platform()

        if (self.game_over or self.win) and self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.name, self.score)

    def draw(self):
        color = BROWN if self.level < 50 else LIGHT_BROWN
        for plat in self.platforms:
            if plat.width > 0:
                pygame.draw.rect(screen, color, plat)
        pygame.draw.circle(screen, (0, 0, 255), (int(self.ball_x), int(self.ball_y)), self.ball_radius)
        screen.blit(font.render(f"{self.name} Score: {self.score}", True, BLACK), (self.offset + 10, 10))
        screen.blit(font.render(f"Level: {self.level}", True, BLACK), (self.offset + 10, 30))
        screen.blit(font.render(f"High: {self.high_score}", True, BLACK), (self.offset + 10, 50))
        if self.level >= 90 and not self.win:
            screen.blit(font.render("⚠ Platforms disappear!", True, (200, 0, 0)), (self.offset + 10, 70))
        if self.game_over:
            go_text = big_font.render("Game Over", True, (255, 0, 0))
            r_text = font.render("Press R to Restart", True, BLACK)
            q_text = font.render("Press Q to Quit", True, BLACK)
            screen.blit(go_text, (self.offset + 200 - go_text.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(r_text, (self.offset + 200 - r_text.get_width() // 2, HEIGHT // 2 + 0))
            screen.blit(q_text, (self.offset + 200 - q_text.get_width() // 2, HEIGHT // 2 + 30))
        if self.win:
            win_text = big_font.render("YOU WIN", True, GOLD)
            r_text = font.render("Press R to Restart", True, BLACK)
            q_text = font.render("Press Q to Quit", True, BLACK)
            screen.blit(win_text, (self.offset + 200 - win_text.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(r_text, (self.offset + 200 - r_text.get_width() // 2, HEIGHT // 2 + 0))
            screen.blit(q_text, (self.offset + 200 - q_text.get_width() // 2, HEIGHT // 2 + 30))

players = [
    Player("Player 1", 0, pygame.K_a, pygame.K_d),
    Player("Player 2", 400, pygame.K_LEFT, pygame.K_RIGHT)
]

def game_loop():
    show_start = True
    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return
                if show_start and event.key == pygame.K_SPACE:
                    show_start = False
                if event.key == pygame.K_r:
                    for player in players:
                        player.reset()
                    show_start = True

        if show_start:
            screen.fill(BLACK)
            screen.blit(big_font.render("Tower Jump - 2P", True, WHITE), (WIDTH//2 - 100, HEIGHT//2 - 70))
            screen.blit(font.render("Press SPACE to Start", True, WHITE), (WIDTH//2 - 90, HEIGHT//2 + 0))
            screen.blit(font.render("Press Q to Quit", True, WHITE), (WIDTH//2 - 70, HEIGHT//2 + 30))
            pygame.display.flip()
            continue

        screen.fill(GRAY)
        pygame.draw.line(screen, BLACK, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)

        for player in players:
            if not player.game_over and not player.win:
                player.update(keys)
            player.draw()

        top_score = get_overall_high_score()
        screen.blit(font.render(f"Top Score: {top_score}", True, GOLD), (WIDTH // 2 - 70, HEIGHT - 30))

        pygame.display.flip()

game_loop()
pygame.quit()

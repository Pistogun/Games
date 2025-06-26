import pygame
import random
import sys
import time
import os

pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ship vs Monster")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 150, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 100, 0)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()

ship_img = pygame.Surface((50, 40))
ship_img.fill(GREEN)

monster_img = pygame.Surface((100, 80))
monster_img.fill(RED)

boss_img = pygame.Surface((150, 120))
boss_img.fill(ORANGE)

bullet_img = pygame.Surface((5, 10))
bullet_img.fill(WHITE)

bg_img = pygame.Surface((WIDTH, HEIGHT))
bg_img.fill((20, 20, 40))

explosion_img = pygame.Surface((30, 30))
explosion_img.fill(YELLOW)

explosions = []

def draw_text(text, x, y, size=30, color=WHITE, center=False):
    font = pygame.font.SysFont("Arial", size)
    render = font.render(text, True, color)
    if center:
        rect = render.get_rect(center=(x, y))
        win.blit(render, rect)
    else:
        win.blit(render, (x, y))

def load_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            return int(f.read())
    return 0

def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

class Player:
    def __init__(self):
        self.rect = ship_img.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.bullets = []
        self.bullet_speed = 10
        self.lives = 3
        self.invincible = False
        self.invincible_start_time = 0
        self.shield = False
        self.bullet_level = 1  # 1 = normal, 2 = double, ..., max 4
        self.speed_boost = False

    def move(self, keys):
        speed = 8 if self.speed_boost else 5
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += speed

    def shoot(self):
        if self.bullet_level == 1:
            offsets = [0]
        elif self.bullet_level == 2:
            offsets = [-10, 10]
        elif self.bullet_level == 3:
            offsets = [-15, 0, 15]
        else:
            offsets = [-20, -7, 7, 20]

        for offset in offsets:
            bullet = bullet_img.get_rect(midbottom=(self.rect.centerx + offset, self.rect.top))
            self.bullets.append(bullet)

    def upgrade(self, level):
        if level >= 10:
            self.bullet_speed = 15

    def take_damage(self):
        if not self.invincible:
            if self.shield:
                self.shield = False
            else:
                self.lives -= 1
            self.invincible = True
            self.invincible_start_time = time.time()

    def update_invincibility(self):
        if self.invincible and time.time() - self.invincible_start_time > 2:
            self.invincible = False

    def draw(self):
        if self.invincible and int(time.time() * 5) % 2 == 0:
            return
        win.blit(ship_img, self.rect)
        for bullet in self.bullets:
            pygame.draw.rect(win, WHITE, bullet)
        if self.shield:
            pygame.draw.circle(win, BLUE, self.rect.center, 30, 2)

    def draw_hearts(self):
        for i in range(self.lives):
            draw_text("♥", WIDTH - (i + 1) * 30, 10, size=30, color=RED)

class Monster:
    def __init__(self, level):
        self.is_boss = level == 10
        self.img = boss_img if self.is_boss else monster_img
        self.rect = self.img.get_rect(center=(WIDTH // 2, 100))
        self.speed = 3 if self.is_boss else 2 + level
        self.direction = 1
        self.health = 50 if self.is_boss else 5 + level * 2
        self.max_health = self.health
        self.bullets = []
        self.level = level

    def move(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            self.direction *= -1

    def shoot(self):
        if random.random() < (0.07 if self.is_boss else 0.03):
            if self.is_boss:
                for offset in (-40, -20, 0, 20, 40):
                    bullet = bullet_img.get_rect(midtop=(self.rect.centerx + offset, self.rect.bottom))
                    self.bullets.append(bullet)
            else:
                bullet = bullet_img.get_rect(midtop=self.rect.midbottom)
                self.bullets.append(bullet)

    def draw(self):
        win.blit(self.img, self.rect)
        pygame.draw.rect(win, RED, (self.rect.left, self.rect.top - 10, self.rect.width, 5))
        health_ratio = self.health / self.max_health
        pygame.draw.rect(win, GREEN, (self.rect.left, self.rect.top - 10, int(self.rect.width * health_ratio), 5))
        for bullet in self.bullets:
            pygame.draw.rect(win, RED, bullet)

class PowerUp:
    def __init__(self):
        self.types = ['shield', 'double', 'speed']
        self.type = random.choice(self.types)
        self.rect = pygame.Rect(random.randint(50, WIDTH - 50), -30, 25, 25)
        self.speed = 3
        self.color = {'shield': YELLOW, 'double': RED, 'speed': CYAN}[self.type]

    def move(self):
        self.rect.y += self.speed

    def draw(self):
        pygame.draw.ellipse(win, self.color, self.rect)

def scroll_background(offset):
    win.blit(bg_img, (0, offset % HEIGHT))
    win.blit(bg_img, (0, (offset % HEIGHT) - HEIGHT))

def title_screen():
    win.fill(BLACK)
    draw_text("SHIP vs MONSTER", WIDTH // 2, HEIGHT // 2 - 60, 50, GREEN, center=True)
    draw_text("Press ENTER to Start", WIDTH // 2, HEIGHT // 2 + 10, 30, WHITE, center=True)
    draw_text("Arrow keys to move, Space to shoot", WIDTH // 2, HEIGHT // 2 + 60, 20, CYAN, center=True)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

def game_over_screen(score, high_score):
    win.fill(BLACK)
    draw_text("GAME OVER", WIDTH // 2, HEIGHT // 2 - 60, 50, RED, center=True)
    draw_text(f"Score: {score}", WIDTH // 2, HEIGHT // 2, 30, WHITE, center=True)
    draw_text(f"High Score: {high_score}", WIDTH // 2, HEIGHT // 2 + 40, 25, YELLOW, center=True)
    draw_text("Press R to Restart or Q to Quit", WIDTH // 2, HEIGHT // 2 + 80, 25, WHITE, center=True)
    pygame.display.flip()

def boss_intro():
    win.fill(BLACK)
    draw_text("⚠️ BOSS INCOMING!", WIDTH // 2, HEIGHT // 2, 40, RED, center=True)
    pygame.display.flip()
    pygame.time.delay(2000)

def spawn_explosion(x, y):
    explosions.append({"rect": explosion_img.get_rect(center=(x, y)), "time": time.time()})

def draw_explosions():
    for ex in explosions[:]:
        win.blit(explosion_img, ex["rect"])
        if time.time() - ex["time"] > 0.3:
            explosions.remove(ex)

def main():
    title_screen()
    level = 1
    player = Player()
    monster = Monster(level)
    score = 0
    bg_offset = 0
    game_over = False
    paused = False
    powerup = None
    high_score = load_high_score()

    if level == 10: boss_intro()

    while True:
        clock.tick(60)

        if not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE: player.shoot()
                    if event.key == pygame.K_p: paused = not paused

            if paused:
                scroll_background(bg_offset)
                player.draw()
                monster.draw()
                if powerup: powerup.draw()
                draw_explosions()
                player.draw_hearts()
                draw_text("PAUSED", WIDTH // 2, HEIGHT // 2, 50, YELLOW, center=True)
                pygame.display.flip()
                continue

            keys = pygame.key.get_pressed()
            player.move(keys)
            player.update_invincibility()
            player.upgrade(level)

            bg_offset += 1
            scroll_background(bg_offset)

            for bullet in player.bullets[:]:
                bullet.y -= player.bullet_speed
                if bullet.colliderect(monster.rect):
                    player.bullets.remove(bullet)
                    monster.health -= 1
                    spawn_explosion(bullet.centerx, bullet.centery)
                elif bullet.y < 0:
                    player.bullets.remove(bullet)

            monster.move()
            monster.shoot()

            for bullet in monster.bullets[:]:
                bullet.y += 7 + (level * 0.3)
                if bullet.colliderect(player.rect):
                    monster.bullets.remove(bullet)
                    player.take_damage()
                    if player.lives <= 0:
                        game_over = True
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
                elif bullet.y > HEIGHT:
                    monster.bullets.remove(bullet)

            if monster.health <= 0:
                spawn_explosion(monster.rect.centerx, monster.rect.centery)
                level += 1
                score += 300 if monster.is_boss else 100
                monster = Monster(level)
                if level == 10:
                    boss_intro()
                if random.random() < 0.5:
                    powerup = PowerUp()

            if powerup:
                powerup.move()
                if powerup.rect.colliderect(player.rect):
                    if powerup.type == 'shield':
                        player.shield = True
                    elif powerup.type == 'double':
                        player.bullet_level = min(player.bullet_level + 1, 4)
                    elif powerup.type == 'speed':
                        player.speed_boost = True
                    powerup = None
                elif powerup.rect.top > HEIGHT:
                    powerup = None

            player.draw()
            monster.draw()
            if powerup: powerup.draw()
            draw_explosions()
            player.draw_hearts()
            draw_text(f"Level: {level}", 10, 10)
            draw_text(f"Score: {score}", 10, 40)
            draw_text(f"High Score: {high_score}", 10, 70, 20, YELLOW)
            pygame.display.flip()
        else:
            game_over_screen(score, high_score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: main()
                    if event.key == pygame.K_q: pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()

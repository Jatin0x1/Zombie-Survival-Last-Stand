import math
import pygame
from settings import *


class Player:
    def __init__(self):
        self.rect = pygame.Rect(
            WIDTH // 2 - PLAYER_SIZE // 2,
            HEIGHT // 2 - PLAYER_SIZE // 2,
            PLAYER_SIZE, PLAYER_SIZE
        )
        self.speed = PLAYER_SPEED
        self.health = PLAYER_MAX_HEALTH
        self.last_damage_time = -DAMAGE_COOLDOWN
        self.anim_phase = 0.0
        self.moving = False
        self.recoil = 0

    def update(self):
        keys = pygame.key.get_pressed()
        dx = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP])
        self.moving = bool(dx or dy)
        if self.moving:
            length = math.hypot(dx, dy)
            dx = round(dx / length * self.speed)
            dy = round(dy / length * self.speed)
            self.anim_phase += 0.24
        else:
            self.anim_phase *= 0.85
        # Axis-separated collision allows sliding along buildings and cover.
        obstacles = [pygame.Rect(*item[:4]) for item in MAP_OBSTACLES]
        self.rect.x += dx
        self.rect.clamp_ip(pygame.Rect(12, 12, WIDTH - 24, HEIGHT - 24))
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if dx > 0: self.rect.right = obstacle.left
                elif dx < 0: self.rect.left = obstacle.right
        self.rect.y += dy
        self.rect.clamp_ip(pygame.Rect(12, 12, WIDTH - 24, HEIGHT - 24))
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if dy > 0: self.rect.bottom = obstacle.top
                elif dy < 0: self.rect.top = obstacle.bottom
        self.recoil = max(0, self.recoil - 1)

    def take_damage(self):
        now = pygame.time.get_ticks()
        if now - self.last_damage_time >= DAMAGE_COOLDOWN:
            self.health = max(0, self.health - PLAYER_DAMAGE)
            self.last_damage_time = now
            return True
        return False

    def draw(self, screen, aim_pos=None):
        # Ground shadow and compact tactical survivor silhouette.
        bob = int(abs(math.sin(self.anim_phase)) * 2) if self.moving else 0
        body = self.rect.move(0, -bob)
        pygame.draw.ellipse(screen, (3, 5, 6), self.rect.move(3, 5))
        pygame.draw.ellipse(screen, (17, 42, 31), body.inflate(5, 3))
        pygame.draw.ellipse(screen, (43, 104, 70), body.inflate(-2, 1))
        pygame.draw.ellipse(screen, (72, 132, 83), body.inflate(-9, -8))
        # Backpack and shoulder straps
        pygame.draw.rect(screen, (28, 55, 42), (body.left + 4, body.centery - 6, 8, 14), border_radius=3)
        pygame.draw.line(screen, (154, 160, 116), (body.centerx - 4, body.top + 5), (body.centerx + 5, body.bottom - 4), 2)
        pygame.draw.circle(screen, (188, 166, 127), (body.centerx, body.centery - 4), 7)
        pygame.draw.arc(screen, (67, 75, 64), (body.centerx - 6, body.centery - 10, 12, 12), 0.2, 2.8, 2)
        if aim_pos:
            dx = aim_pos[0] - body.centerx
            dy = aim_pos[1] - body.centery
            angle = math.atan2(dy, dx)
            end = (body.centerx + int(math.cos(angle) * 26), body.centery + int(math.sin(angle) * 26))
            start = (body.centerx + int(math.cos(angle) * 5), body.centery + int(math.sin(angle) * 5))
            pygame.draw.line(screen, (21, 28, 25), start, end, 9)
            pygame.draw.line(screen, (118, 126, 111), start, end, 4)
            pygame.draw.circle(screen, (190, 193, 166), end, 3)

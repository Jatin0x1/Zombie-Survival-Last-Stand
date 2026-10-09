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

    def update(self):
        keys = pygame.key.get_pressed()
        dx = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        dy = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(
            keys[pygame.K_w] or keys[pygame.K_UP]
        )
        if dx or dy:
            length = math.hypot(dx, dy)
            self.rect.x += round(dx / length * self.speed)
            self.rect.y += round(dy / length * self.speed)
        self.rect.clamp_ip(pygame.Rect(12, 12, WIDTH - 24, HEIGHT - 24))

    def take_damage(self):
        now = pygame.time.get_ticks()
        if now - self.last_damage_time >= DAMAGE_COOLDOWN:
            self.health = max(0, self.health - PLAYER_DAMAGE)
            self.last_damage_time = now
            return True
        return False

    def draw(self, screen, aim_pos=None):
        # Shadow and body
        pygame.draw.ellipse(screen, (4, 7, 8), self.rect.move(2, 4))
        pygame.draw.circle(screen, (32, 115, 72), self.rect.center, PLAYER_SIZE // 2)
        pygame.draw.circle(screen, GREEN, self.rect.center, PLAYER_SIZE // 2 - 4)
        pygame.draw.circle(screen, (225, 245, 220),
                           (self.rect.centerx - 5, self.rect.centery - 4), 3)
        pygame.draw.circle(screen, (225, 245, 220),
                           (self.rect.centerx + 5, self.rect.centery - 4), 3)
        if aim_pos:
            dx = aim_pos[0] - self.rect.centerx
            dy = aim_pos[1] - self.rect.centery
            angle = math.atan2(dy, dx)
            end = (self.rect.centerx + int(math.cos(angle) * 24),
                   self.rect.centery + int(math.sin(angle) * 24))
            pygame.draw.line(screen, (35, 45, 38), self.rect.center, end, 7)
            pygame.draw.line(screen, (180, 195, 180), self.rect.center, end, 3)

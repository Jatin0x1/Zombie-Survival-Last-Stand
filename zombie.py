import math
import random
import pygame
from settings import *


class Zombie:
    def __init__(self, x, y, wave=1):
        self.rect = pygame.Rect(x, y, ZOMBIE_SIZE, ZOMBIE_SIZE)
        self.speed = min(ZOMBIE_SPEED + (wave - 1) * ZOMBIE_SPEED_INCREASE,
                         MAX_ZOMBIE_SPEED)
        self.health = ZOMBIE_HEALTH + (1 if wave >= 5 else 0)
        self.max_health = self.health
        self.wobble = random.uniform(0, math.tau)

    def update(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance > 0:
            self.rect.x += round(dx / distance * self.speed)
            self.rect.y += round(dy / distance * self.speed)

    def draw(self, screen):
        pygame.draw.ellipse(screen, (5, 7, 8), self.rect.move(2, 4))
        pygame.draw.rect(screen, (100, 35, 42), self.rect, border_radius=8)
        body = self.rect.inflate(-6, -6)
        pygame.draw.rect(screen, (135, 57, 62), body, border_radius=7)
        pygame.draw.circle(screen, (255, 215, 150),
                           (self.rect.centerx - 5, self.rect.centery - 4), 3)
        pygame.draw.circle(screen, (255, 215, 150),
                           (self.rect.centerx + 5, self.rect.centery - 4), 3)
        # Tiny health bar
        if self.health < self.max_health:
            w = self.rect.width
            pygame.draw.rect(screen, (55, 20, 24),
                             (self.rect.x, self.rect.y - 6, w, 3))
            pygame.draw.rect(screen, RED,
                             (self.rect.x, self.rect.y - 6,
                              int(w * max(0, self.health / self.max_health)), 3))

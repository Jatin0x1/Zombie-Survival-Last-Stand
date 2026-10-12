
import math
import random
import pygame

from settings import *


class Zombie:
    TYPES = {
        "walker": {
            "size": ZOMBIE_SIZE,
            "speed": ZOMBIE_SPEED,
            "health": ZOMBIE_HEALTH,
            "color": (112, 104, 82),
            "damage": 8,
        },
        "runner": {
            "size": 22,
            "speed": ZOMBIE_SPEED * 1.75,
            "health": max(1, ZOMBIE_HEALTH - 1),
            "color": (150, 65, 48),
            "damage": 6,
        },
        "brute": {
            "size": 42,
            "speed": ZOMBIE_SPEED * 0.60,
            "health": ZOMBIE_HEALTH * 3,
            "color": (74, 83, 69),
            "damage": 18,
        },
        "boss": {
            "size": 66,
            "speed": ZOMBIE_SPEED * 0.72,
            "health": ZOMBIE_HEALTH * 12,
            "color": (92, 35, 43),
            "damage": 25,
        },
    }

    def __init__(self, x, y, wave=1, zombie_type=None):
        if zombie_type is None:
            roll = random.random()
            if wave >= 3 and roll < 0.20:
                zombie_type = "runner"
            elif wave >= 4 and roll < 0.38:
                zombie_type = "brute"
            else:
                zombie_type = "walker"

        self.zombie_type = zombie_type
        stats = self.TYPES[zombie_type]

        self.size = stats["size"]
        self.rect = pygame.Rect(x, y, self.size, self.size)

        wave_bonus = (wave - 1) * ZOMBIE_SPEED_INCREASE
        self.speed = min(
            stats["speed"] + wave_bonus,
            MAX_ZOMBIE_SPEED * (1.25 if zombie_type == "boss" else 1)
        )

        self.max_health = stats["health"] + (wave // 5)
        self.health = self.max_health
        self.color = stats["color"]
        self.damage = stats["damage"]
        self.wobble = random.uniform(0, math.tau)

    def update(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.rect.x += round(dx / distance * self.speed)
            self.rect.y += round(dy / distance * self.speed)

        self.wobble += 0.08

    def draw(self, screen):
        # Shadow
        shadow = self.rect.move(4, 5)
        pygame.draw.ellipse(screen, (12, 13, 12), shadow)

        # Body and head
        pygame.draw.ellipse(screen, self.color, self.rect)
        head_radius = max(5, self.size // 5)
        head = (
            self.rect.centerx,
            self.rect.y + head_radius + 3,
        )
        pygame.draw.circle(screen, (153, 139, 112), head, head_radius)

        # Glowing eyes
        eye_y = head[1]
        eye_offset = max(3, self.size // 12)
        eye_color = (255, 70, 40) if self.zombie_type == "boss" else (225, 185, 90)

        pygame.draw.circle(
            screen, eye_color,
            (self.rect.centerx - eye_offset, eye_y), 2
        )
        pygame.draw.circle(
            screen, eye_color,
            (self.rect.centerx + eye_offset, eye_y), 2
        )

        # Boss health bar
        if self.zombie_type == "boss":
            bar_width = 100
            bar = pygame.Rect(
                self.rect.centerx - bar_width // 2,
                self.rect.top - 14,
                bar_width,
                8,
            )
            pygame.draw.rect(screen, (35, 25, 25), bar)
            fill_width = int(
                bar_width * max(0, self.health) / self.max_health
            )
            pygame.draw.rect(
                screen, (205, 35, 42),
                (bar.x, bar.y, fill_width, bar.height)
            )

        # Small health bar for damaged enemies
        elif self.health < self.max_health:
            bar_width = self.size
            bar = pygame.Rect(
                self.rect.x, self.rect.y - 7, bar_width, 4
            )
            pygame.draw.rect(screen, (30, 25, 25), bar)
            fill_width = int(
                bar_width * max(0, self.health) / self.max_health
            )
            pygame.draw.rect(
                screen, (165, 45, 40),
                (bar.x, bar.y, fill_width, bar.height)
            )

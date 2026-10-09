import math
import pygame
from settings import *


class Bullet:
    def __init__(self, x, y, target_x, target_y, weapon="Pistol", angle_offset=0):
        self.x = float(x)
        self.y = float(y)
        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy) or 1
        angle = math.atan2(dy, dx) + angle_offset
        self.dx = math.cos(angle)
        self.dy = math.sin(angle)
        self.weapon = weapon
        self.speed = BULLET_SPEED if weapon != "Shotgun" else BULLET_SPEED * 0.9
        self.damage = 1 if weapon == "Pistol" else (2 if weapon == "Shotgun" else 1)
        self.size = 7 if weapon == "Pistol" else (6 if weapon == "Shotgun" else 5)
        self.rect = pygame.Rect(int(x), int(y), self.size, self.size)
        self.color = YELLOW if weapon == "Pistol" else (ORANGE if weapon == "Shotgun" else BLUE)

    def update(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        self.rect.center = (round(self.x), round(self.y))

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, max(2, self.size // 2))

    def is_off_screen(self):
        return (self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT)

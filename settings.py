WIDTH = 1200
HEIGHT = 760
FPS = 60
TITLE = "Zombie Survival: The Last Stand"

BLACK = (13, 16, 20)
WHITE = (240, 240, 240)
GREEN = (65, 210, 110)
RED = (220, 55, 55)
GRAY = (65, 72, 78)
DARK_GRAY = (27, 32, 38)
YELLOW = (255, 215, 75)
BLUE = (80, 170, 255)
ORANGE = (255, 145, 65)
PURPLE = (185, 115, 255)

PLAYER_SIZE = 32
PLAYER_SPEED = 5
PLAYER_MAX_HEALTH = 100
PLAYER_DAMAGE = 10
DAMAGE_COOLDOWN = 700

ZOMBIE_SIZE = 30
ZOMBIE_SPEED = 1.8
ZOMBIE_HEALTH = 3
ZOMBIES_PER_WAVE = 3
ZOMBIES_INCREASE_PER_WAVE = 2
ZOMBIE_SPEED_INCREASE = 0.20
MAX_ZOMBIE_SPEED = 4.0

BULLET_SPEED = 12
BULLET_SIZE = 7
BULLET_DAMAGE = 1

MAGAZINE_SIZE = 12
STARTING_RESERVE_AMMO = 72
RELOAD_TIME = 1200
WAVE_MESSAGE_DURATION = 2000

POWERUP_DROP_CHANCE = 0.22
POWERUP_LIFETIME = 12000
HIGH_SCORE_FILE = "highscore.txt"

# Map geometry: fixed structures, barricades and cover. Coordinates are world/screen coordinates.
# Rectangles are (x, y, width, height, kind).
MAP_OBSTACLES = [
    (110, 115, 210, 115, "building"), (420, 90, 145, 72, "building"),
    (805, 105, 250, 125, "building"), (130, 390, 155, 110, "building"),
    (890, 430, 190, 145, "building"), (465, 500, 185, 70, "building"),
    (365, 280, 90, 22, "wall"), (530, 260, 22, 125, "wall"),
    (690, 350, 125, 22, "wall"), (345, 590, 80, 22, "wall"),
    (700, 610, 100, 22, "wall"), (1040, 300, 22, 78, "wall"),
    (340, 180, 48, 38, "crate"), (620, 130, 42, 42, "crate"),
    (600, 430, 52, 42, "crate"), (820, 315, 48, 38, "crate"),
    (300, 545, 42, 42, "crate"), (1080, 620, 44, 38, "crate"),
    (735, 170, 75, 28, "barricade"), (500, 395, 80, 28, "barricade"),
]

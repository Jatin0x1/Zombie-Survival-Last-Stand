import math
import os
import random
import sys
from pathlib import Path
import pygame
from settings import *
from player import Player
from zombie import Zombie
from bullet import Bullet
# Initialize audio before pygame initializes its modules.
pygame.mixer.pre_init(
    frequency=44100,
    size=-16,
    channels=2,
    buffer=2048
)

pygame.init()

SOUND_AVAILABLE = pygame.mixer.get_init() is not None

if not SOUND_AVAILABLE:
    try:
        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=2048
        )
        SOUND_AVAILABLE = True
    except pygame.error as exc:
        print("Audio initialization failed:", exc)
        SOUND_AVAILABLE = False



# Assets are bundled beside the executable by PyInstaller's onedir build.


def resource_path(relative_path):

    base_path = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)

    return Path(base_path) / relative_path


# Background music: stream it through pygame.mixer.music, separately from SFX.
MUSIC_FILE = resource_path("assets/gameplay_music.wav")

MUSIC_AVAILABLE = False
if SOUND_AVAILABLE and MUSIC_FILE.is_file():
    try:
        pygame.mixer.music.load(str(MUSIC_FILE))
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1)
        MUSIC_AVAILABLE = True
    except (pygame.error, OSError) as exc:
        print("Background music error:", exc)

pygame.display.set_caption(TITLE)

clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 22)

small_font = pygame.font.SysFont("arial", 16)

big_font = pygame.font.SysFont("arial", 48)

title_font = pygame.font.SysFont("arial", 54, bold=True)


# Optional synthesized sound effects: no external assets required.


def make_tone(frequency=440, duration=0.08, volume=0.18):

    if not SOUND_AVAILABLE:

        return None

    try:

        import array

        sample_rate = 22050

        count = int(sample_rate * duration)

        amplitude = int(32767 * volume)

        samples = array.array("h")

        for i in range(count):

            fade = 1 - (i / max(1, count))

            samples.append(
                int(
                    amplitude
                    * fade
                    * math.sin(2 * math.pi * frequency * i / sample_rate)
                )
            )

        return pygame.mixer.Sound(buffer=samples.tobytes())

    except Exception:

        return None


SOUNDS = {
    "shoot": make_tone(620, 0.035, 0.12),
    "shotgun": make_tone(180, 0.12, 0.22),
    "reload": make_tone(330, 0.08, 0.15),
    "hit": make_tone(95, 0.10, 0.18),
    "pickup": make_tone(880, 0.09, 0.14),
    "wave": make_tone(520, 0.18, 0.14),
}


def play_sound(name):

    sound = SOUNDS.get(name)

    if SOUND_AVAILABLE and sound and sound_on:

        try:

            sound.play()

        except pygame.error:

            pass


def draw_text(text, font_obj, color, center, surface=None):

    if surface is None:

        surface = screen

    image = font_obj.render(str(text), True, color)

    surface.blit(
        image, (center[0] - image.get_width() // 2, center[1] - image.get_height() // 2)
    )


def high_score_candidates():
    """Return install-folder and per-user save paths in preferred order."""
    paths = [Path(__file__).resolve().parent / HIGH_SCORE_FILE]
    try:
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / ".local" / "share")
        paths.append(base / "ZombieSurvivalLastStand" / HIGH_SCORE_FILE)
    except (OSError, RuntimeError):
        pass
    return paths


def load_high_score():
    scores = []
    for path in high_score_candidates():
        try:
            scores.append(max(0, int(path.read_text(encoding="utf-8").strip() or "0")))
        except (OSError, ValueError):
            continue
    return max(scores, default=0)


def save_high_score(value):
    for path in high_score_candidates():
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(max(0, int(value))), encoding="utf-8")
            return True
        except OSError:
            continue
    return False


high_score = load_high_score()


# Background details are drawn procedurally, so no image downloads are needed.

random.seed(14)

floor_marks = []

for _ in range(95):

    floor_marks.append(
        (
            random.randint(18, WIDTH - 18),
            random.randint(18, HEIGHT - 18),
            random.randint(2, 5),
        )
    )

random.seed()


def draw_arena():

    # Dark, gritty concrete floor

    screen.fill((13, 16, 17))

    # Uneven concrete tiles

    tile = 50

    for x in range(0, WIDTH, tile):

        for y in range(0, HEIGHT, tile):

            shade = 24 if ((x // tile + y // tile) % 2 == 0) else 29

            pygame.draw.rect(screen, (shade, shade + 2, shade + 2), (x, y, tile, tile))

            # Worn tile seams

            pygame.draw.line(screen, (17, 20, 21), (x, y), (x + tile, y), 1)

            pygame.draw.line(screen, (17, 20, 21), (x, y), (x, y + tile), 1)

    # Existing floor marks

    for x, y, radius in floor_marks:

        pygame.draw.circle(screen, (35, 38, 36), (x, y), radius)

        pygame.draw.circle(screen, (19, 22, 21), (x - 2, y - 2), max(2, radius // 2), 1)

    # Random-looking cracks, fixed in place

    for x, y in [
        (140, 170),
        (350, 410),
        (610, 150),
        (790, 470),
        (900, 250),
        (440, 100),
    ]:

        pygame.draw.line(screen, (10, 13, 13), (x, y), (x + 13, y + 8), 2)

        pygame.draw.line(screen, (10, 13, 13), (x + 13, y + 8), (x + 23, y + 4), 2)

        pygame.draw.line(screen, (10, 13, 13), (x + 13, y + 8), (x + 18, y + 19), 2)

    # Scattered debris

    for x, y in [
        (95, 115),
        (265, 310),
        (520, 235),
        (720, 120),
        (865, 390),
        (180, 520),
        (570, 530),
        (950, 180),
        (390, 190),
    ]:

        pygame.draw.polygon(
            screen,
            (42, 43, 39),
            [(x, y), (x + 7, y - 3), (x + 12, y + 4), (x + 4, y + 8)],
        )

        pygame.draw.line(screen, (20, 22, 21), (x, y), (x + 8, y + 5), 1)

    # Abandoned district: structures, cover and readable doorway/window details.

    for ox, oy, ow, oh, kind in MAP_OBSTACLES:

        rect = pygame.Rect(ox, oy, ow, oh)

        shadow = rect.move(7, 8)

        pygame.draw.rect(screen, (5, 7, 8), shadow, border_radius=4)

        if kind == "building":

            pygame.draw.rect(screen, (44, 48, 45), rect, border_radius=4)

            pygame.draw.rect(screen, (83, 83, 73), rect, 3, border_radius=4)

            pygame.draw.rect(screen, (21, 25, 25), rect.inflate(-14, -14), 2)

            # Windows / broken roof panels

            for wx in range(rect.x + 20, rect.right - 16, 48):

                pygame.draw.rect(screen, (12, 20, 22), (wx, rect.y + 13, 25, 10))

                pygame.draw.line(
                    screen, (71, 75, 67), (wx, rect.y + 12), (wx + 25, rect.y + 12), 2
                )

            pygame.draw.rect(
                screen, (13, 17, 17), (rect.centerx - 13, rect.bottom - 23, 26, 23)
            )

            pygame.draw.line(
                screen,
                (101, 77, 49),
                (rect.x + 8, rect.y + 24),
                (rect.x + 32, rect.y + 38),
                2,
            )

        elif kind == "wall":

            pygame.draw.rect(screen, (67, 72, 67), rect, border_radius=2)

            pygame.draw.rect(screen, (100, 101, 88), rect, 2, border_radius=2)

            pygame.draw.line(
                screen,
                (36, 41, 39),
                (rect.x + 5, rect.y + 4),
                (rect.right - 5, rect.y + 4),
                2,
            )

        elif kind == "crate":

            pygame.draw.rect(screen, (65, 48, 33), rect, border_radius=3)

            pygame.draw.rect(screen, (117, 82, 49), rect, 2, border_radius=3)

            pygame.draw.line(screen, (36, 29, 23), rect.topleft, rect.bottomright, 3)

            pygame.draw.line(screen, (36, 29, 23), rect.topright, rect.bottomleft, 3)

        else:

            pygame.draw.rect(screen, (92, 57, 37), rect, border_radius=3)

            pygame.draw.rect(screen, (156, 100, 49), rect, 2, border_radius=3)

            for bx in range(rect.x + 8, rect.right - 4, 16):

                pygame.draw.line(
                    screen, (48, 37, 29), (bx, rect.y + 3), (bx, rect.bottom - 3), 2
                )

    # Dark perimeter and worn outer boundary

    pygame.draw.rect(screen, (7, 9, 10), (0, 0, WIDTH, HEIGHT), 12)

    pygame.draw.rect(
        screen, (67, 69, 63), (5, 5, WIDTH - 10, HEIGHT - 10), 3, border_radius=8
    )

    pygame.draw.rect(
        screen, (11, 14, 15), (12, 12, WIDTH - 24, HEIGHT - 24), 2, border_radius=7
    )

    # Faded hazard markings at the top and bottom

    for x in range(22, 92, 14):

        pygame.draw.line(screen, (105, 70, 34), (x, 20), (x + 8, 20), 4)

        pygame.draw.line(
            screen, (105, 70, 34), (x, HEIGHT - 20), (x + 8, HEIGHT - 20), 4
        )


class PowerUp:

    def __init__(self, x, y, kind):

        self.rect = pygame.Rect(x - 13, y - 13, 26, 26)

        self.kind = kind

        self.created = pygame.time.get_ticks()

    def update(self):

        return pygame.time.get_ticks() - self.created > POWERUP_LIFETIME

    def draw(self):

        color = GREEN if self.kind == "health" else BLUE

        pygame.draw.circle(screen, (8, 10, 12), self.rect.center, 16)

        pygame.draw.circle(screen, color, self.rect.center, 12)

        if self.kind == "health":

            pygame.draw.rect(
                screen, WHITE, (self.rect.centerx - 3, self.rect.centery - 7, 6, 14)
            )

            pygame.draw.rect(
                screen, WHITE, (self.rect.centerx - 7, self.rect.centery - 3, 14, 6)
            )

        else:

            pygame.draw.rect(
                screen, WHITE, (self.rect.centerx - 5, self.rect.centery - 7, 10, 14), 2
            )

            pygame.draw.line(
                screen,
                WHITE,
                (self.rect.centerx - 2, self.rect.centery - 3),
                (self.rect.centerx + 2, self.rect.centery + 3),
                2,
            )


def spawn_wave(wave_number):

    result = []

    count = ZOMBIES_PER_WAVE + (wave_number - 1) * ZOMBIES_INCREASE_PER_WAVE
    difficulty_settings = {
        "Easy": (0.75, 0.82, 0.85),
        "Normal": (1.0, 1.0, 1.0),
        "Hard": (1.25, 1.18, 1.20),
    }
    count_scale, speed_scale, health_scale = difficulty_settings.get(globals().get("difficulty", "Normal"), (1.0, 1.0, 1.0))
    count = max(1, round(count * count_scale))

    for _ in range(count):

        side = random.choice(("top", "bottom", "left", "right"))

        if side == "top":

            x, y = random.randint(25, WIDTH - ZOMBIE_SIZE - 25), 22

        elif side == "bottom":

            x, y = (
                random.randint(25, WIDTH - ZOMBIE_SIZE - 25),
                HEIGHT - ZOMBIE_SIZE - 22,
            )

        elif side == "left":

            x, y = 22, random.randint(25, HEIGHT - ZOMBIE_SIZE - 25)

        else:

            x, y = WIDTH - ZOMBIE_SIZE - 22, random.randint(
                25, HEIGHT - ZOMBIE_SIZE - 25
            )

        candidate = pygame.Rect(x, y, ZOMBIE_SIZE, ZOMBIE_SIZE)

        attempts = 0

        while (
            any(candidate.colliderect(pygame.Rect(*o[:4])) for o in MAP_OBSTACLES)
            and attempts < 30
        ):

            x = random.randint(28, WIDTH - ZOMBIE_SIZE - 28)

            y = random.randint(28, HEIGHT - ZOMBIE_SIZE - 28)

            candidate.topleft = (x, y)

            attempts += 1

        zombie = Zombie(x, y, wave_number)
        zombie.speed *= speed_scale
        zombie.max_health = max(1, round(zombie.max_health * health_scale))
        zombie.health = zombie.max_health
        result.append(zombie)

    return result


WEAPONS = {
    "Pistol": {"mag": 12, "reserve": 72, "delay": 250, "reload": 1200, "ammo_cost": 1},
    "Shotgun": {"mag": 6, "reserve": 30, "delay": 650, "reload": 1600, "ammo_cost": 1},
    "Rifle": {"mag": 30, "reserve": 150, "delay": 100, "reload": 1500, "ammo_cost": 1},
}

WEAPON_ORDER = ["Pistol", "Shotgun", "Rifle"]


def reset_game():

    state = {
        "player": Player(),
        "bullets": [],
        "zombies": [],
        "powerups": [],
        "score": 0,
        "wave": 1,
        "weapon": "Pistol",
        "ammo": {name: spec["mag"] for name, spec in WEAPONS.items()},
        "reserve": {name: spec["reserve"] for name, spec in WEAPONS.items()},
        "reloading": False,
        "reload_start": 0,
        "last_shot": 0,
        "wave_start": pygame.time.get_ticks(),
        "wave_message": True,
        "game_over": False,
        "paused": False,
        "flash_until": 0,
        "flashlight_on": True,
        "effects": [],
        "muzzle_until": 0,
        "muzzle_angle": 0.0,
        "kills": 0,
        "damage_flash": 0,
        "started_at": pygame.time.get_ticks(),
        "survival_time": 0,
    }

    state["zombies"] = spawn_wave(1)

    return state


game = reset_game()

scene = "menu"

sound_on = True  # Sound-effects toggle; retained name for existing gameplay calls.
music_on = True
music_volume = 0.25
sfx_volume = 0.70
difficulty = "Normal"
settings_return_scene = "menu"


def apply_music_settings():
    if SOUND_AVAILABLE:
        try:
            pygame.mixer.music.set_volume(music_volume if music_on else 0.0)
        except pygame.error:
            pass
    for effect in SOUNDS.values():
        if effect is not None:
            try:
                effect.set_volume(sfx_volume if sound_on else 0.0)
            except pygame.error:
                pass


def apply_sfx_settings():
    for effect in SOUNDS.values():
        if effect is not None:
            try:
                effect.set_volume(sfx_volume if sound_on else 0.0)
            except pygame.error:
                pass


apply_music_settings()


def toggle_fullscreen():
    """Toggle the display mode while keeping the game's logical canvas fixed."""
    global display, fullscreen
    fullscreen = not fullscreen
    if fullscreen:
        display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        display = pygame.display.set_mode((WIDTH, HEIGHT))


def logical_mouse_pos(pos=None):
    """Map display mouse coordinates to the fixed logical game canvas."""
    if pos is None:
        pos = pygame.mouse.get_pos()
    dw, dh = display.get_size()
    # The canvas is stretched to fill the display, so map each axis separately.
    x = pos[0] * WIDTH / max(1, dw)
    y = pos[1] * HEIGHT / max(1, dh)
    return int(x), int(y)


def present_screen():
    """Stretch the logical game canvas to fill the entire display."""
    dw, dh = display.get_size()
    scaled = pygame.transform.scale(screen, (max(1, dw), max(1, dh)))
    display.blit(scaled, (0, 0))
    pygame.display.flip()


_panel_cache = {}

def panel(rect, fill=(8, 13, 15, 225), border=(79, 103, 91), radius=12):
    key = (rect.width, rect.height, fill, border, radius)
    layer = _panel_cache.get(key)
    if layer is None:
        layer = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(layer, fill, layer.get_rect(), border_radius=radius)
        pygame.draw.rect(layer, (*border, 230), layer.get_rect(), 2, border_radius=radius)
        _panel_cache[key] = layer
    screen.blit(layer, rect.topleft)


def draw_button(label, rect, selected=False):

    mouse = logical_mouse_pos()

    hover = rect.collidepoint(mouse)

    fill = (41, 77, 61) if (selected or hover) else (23, 33, 34)

    pygame.draw.rect(screen, fill, rect, border_radius=8)

    pygame.draw.rect(
        screen, (102, 159, 118) if hover else (72, 104, 87), rect, 2, border_radius=8
    )

    draw_text(label, font, (236, 241, 229), rect.center)


def draw_menu():

    draw_arena()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    overlay.fill((2, 5, 7, 190))

    screen.blit(overlay, (0, 0))

    # Cinematic title panel with restrained tactical green and hazard red.

    panel(
        pygame.Rect(WIDTH // 2 - 280, 42, 560, 590), (5, 10, 12, 235), (68, 94, 79), 16
    )

    pygame.draw.rect(
        screen, (160, 52, 43), (WIDTH // 2 - 220, 108, 5, 118), border_radius=2
    )

    draw_text(
        "LAST STAND // SURVIVAL PROTOCOL",
        small_font,
        (166, 191, 170),
        (WIDTH // 2, 106),
    )

    draw_text("ZOMBIE", title_font, (226, 233, 219), (WIDTH // 2, 163))

    draw_text("SURVIVAL", title_font, GREEN, (WIDTH // 2, 218))

    draw_text("THE LAST STAND", font, (175, 187, 176), (WIDTH // 2, 263))

    pygame.draw.line(
        screen, (58, 77, 65), (WIDTH // 2 - 200, 290), (WIDTH // 2 + 200, 290), 2
    )

    draw_text(
        "SCAVENGE. ADAPT. SURVIVE.", small_font, (196, 199, 184), (WIDTH // 2, 316)
    )

    draw_button("DEPLOY  /  START GAME", pygame.Rect(WIDTH // 2 - 155, 328, 310, 48))

    draw_button(
        "MUSIC: ON" if music_on else "MUSIC: OFF",
        pygame.Rect(WIDTH // 2 - 155, 388, 145, 40),
    )

    draw_button(
        "SETTINGS",
        pygame.Rect(WIDTH // 2 + 10, 388, 145, 40),
    )

    draw_text("MUSIC VOLUME", small_font, (168, 181, 171), (WIDTH // 2 - 116, 453))

    draw_button("−", pygame.Rect(WIDTH // 2 - 155, 466, 42, 34))

    pygame.draw.rect(
        screen, (41, 48, 44), (WIDTH // 2 - 100, 478, 158, 10), border_radius=5
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (WIDTH // 2 - 100, 478, int(158 * music_volume), 10),
        border_radius=5,
    )

    pygame.draw.circle(
        screen, WHITE, (WIDTH // 2 - 100 + int(158 * music_volume), 483), 8
    )

    draw_button("+", pygame.Rect(WIDTH // 2 + 67, 466, 42, 34))

    draw_text(
        f"{round(music_volume*100)}%", small_font, YELLOW, (WIDTH // 2 + 133, 483)
    )

    draw_text(f"PERSONAL BEST  {high_score:06d}", small_font, YELLOW, (WIDTH // 2, 528))

    draw_text(
        "WASD MOVE  •  MOUSE FIRE  •  R RELOAD  •  1–3 WEAPONS",
        small_font,
        (168, 181, 171),
        (WIDTH // 2, 562),
    )

    draw_text(
        "F FLASHLIGHT  •  B SFX  •  ESC PAUSE  •  F11 FULLSCREEN",
        small_font,
        (133, 149, 138),
        (WIDTH // 2, 588),
    )


def draw_slider(label, value, y, prefix):
    draw_text(label, small_font, (168, 181, 171), (WIDTH // 2 - 110, y - 13))
    track = pygame.Rect(WIDTH // 2 - 100, y, 200, 10)
    pygame.draw.rect(screen, (41, 48, 44), track, border_radius=5)
    pygame.draw.rect(screen, GREEN, (track.x, track.y, int(track.width * value), track.height), border_radius=5)
    pygame.draw.circle(screen, WHITE, (track.x + int(track.width * value), track.centery), 8)
    draw_text(f"{round(value * 100)}%", small_font, YELLOW, (WIDTH // 2 + 135, y + 5))


def draw_settings():
    draw_arena()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((2, 5, 7, 205))
    screen.blit(overlay, (0, 0))
    panel(pygame.Rect(WIDTH // 2 - 270, 65, 540, 620), (5, 10, 12, 242), (68, 94, 79), 16)
    draw_text("SETTINGS", title_font, GREEN, (WIDTH // 2, 115))
    draw_button("MUSIC: ON" if music_on else "MUSIC: OFF", pygame.Rect(WIDTH // 2 - 210, 155, 200, 42))
    draw_button("SFX: ON" if sound_on else "SFX: OFF", pygame.Rect(WIDTH // 2 + 10, 155, 200, 42))
    draw_slider("MUSIC VOLUME", music_volume, 235, "music")
    draw_slider("SFX VOLUME", sfx_volume, 310, "sfx")
    draw_text("DIFFICULTY", small_font, (168, 181, 171), (WIDTH // 2, 365))
    for label, x in (("EASY", WIDTH // 2 - 210), ("NORMAL", WIDTH // 2 - 70), ("HARD", WIDTH // 2 + 70)):
        draw_button(label, pygame.Rect(x, 385, 130, 42), selected=(difficulty.upper() == label))
    draw_button("WINDOWED" if fullscreen else "FULLSCREEN", pygame.Rect(WIDTH // 2 - 210, 455, 200, 42))
    draw_text("Difficulty changes zombie count, speed and health", small_font, (168, 181, 171), (WIDTH // 2, 530))
    draw_button("BACK TO MENU", pygame.Rect(WIDTH // 2 - 125, 575, 250, 45))


MINIMAP_WIDTH, MINIMAP_HEIGHT = 160, 110
_minimap_background = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT), pygame.SRCALPHA)
_minimap_background.fill((5, 10, 12, 220))
for _mx in range(0, MINIMAP_WIDTH, 20):
    pygame.draw.line(_minimap_background, (25, 38, 38), (_mx, 0), (_mx, MINIMAP_HEIGHT), 1)
for _my in range(0, MINIMAP_HEIGHT, 20):
    pygame.draw.line(_minimap_background, (25, 38, 38), (0, _my), (MINIMAP_WIDTH, _my), 1)
_minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT), pygame.SRCALPHA)


def draw_minimap():

    map_width, map_height = MINIMAP_WIDTH, MINIMAP_HEIGHT

    # Keep the minimap anchored to the bottom-left of the logical canvas.
    margin = 20

    map_x = margin

    map_y = HEIGHT - map_height - margin

    # Reuse the same surface and static grid instead of allocating and
    # rebuilding the minimap background every frame.
    minimap = _minimap_surface
    minimap.blit(_minimap_background, (0, 0))

    # Player position

    player = game["player"]

    player_x = int(player.rect.centerx / WIDTH * map_width)

    player_y = int(player.rect.centery / HEIGHT * map_height)

    # Zombie positions

    for zombie in game["zombies"]:

        zx = int(zombie.rect.centerx / WIDTH * map_width)

        zy = int(zombie.rect.centery / HEIGHT * map_height)

        pygame.draw.circle(minimap, (235, 65, 65), (zx, zy), 3)

    pygame.draw.circle(minimap, (50, 235, 125), (player_x, player_y), 4)

    screen.blit(minimap, (map_x, map_y))

    pygame.draw.rect(
        screen,
        (100, 125, 115),
        (map_x, map_y, map_width, map_height),
        2,
        border_radius=5,
    )

    draw_text("RADAR", small_font, WHITE, (map_x + map_width // 2, map_y - 12))


def draw_hud():

    player = game["player"]

    # Health/status card

    panel(pygame.Rect(18, 16, 260, 92), (5, 10, 12, 225), (64, 89, 75), 10)

    draw_text("VITALS", small_font, (150, 172, 151), (55, 34))

    draw_text(
        f"{player.health:03d}",
        big_font if player.health <= 30 else font,
        RED if player.health <= 30 else WHITE,
        (66, 65),
    )

    ratio = max(0, min(1, player.health / PLAYER_MAX_HEALTH))

    pygame.draw.rect(screen, (52, 25, 25), (108, 57, 150, 12), border_radius=4)

    pygame.draw.rect(
        screen,
        (64, 190, 105) if ratio > 0.35 else (220, 60, 50),
        (108, 57, int(150 * ratio), 12),
        border_radius=4,
    )

    draw_text("OPERATOR", small_font, (139, 153, 141), (177, 84))

    # Center weapon card

    weapon = game["weapon"]

    ammo = game["ammo"][weapon]

    reserve = game["reserve"][weapon]

    panel(pygame.Rect(WIDTH // 2 - 145, 16, 290, 68), (5, 10, 12, 220), (65, 83, 74), 9)

    draw_text(
        f"ACTIVE WEAPON  /  {weapon.upper()}",
        small_font,
        (164, 186, 166),
        (WIDTH // 2, 34),
    )

    ammo_label = (
        f"RELOADING  {max(0, WEAPONS[weapon]['reload']-(pygame.time.get_ticks()-game['reload_start']))/1000:.1f}s"
        if game["reloading"]
        else f"{ammo:02d}   /   {reserve:03d}"
    )

    draw_text(
        ammo_label, font, ORANGE if game["reloading"] else WHITE, (WIDTH // 2, 61)
    )

    # Objective card

    panel(pygame.Rect(WIDTH - 210, 16, 190, 76), (5, 10, 12, 220), (65, 83, 74), 9)

    draw_text(f"SCORE  {game['score']:06d}", font, WHITE, (WIDTH - 115, 39))

    draw_text(
        f"WAVE  {game['wave']:02d}    HOSTILES {len(game['zombies']):02d}",
        small_font,
        YELLOW,
        (WIDTH - 115, 68),
    )

    panel(
        pygame.Rect(WIDTH // 2 - 280, HEIGHT - 38, 560, 26),
        (4, 8, 10, 210),
        (49, 66, 56),
        6,
    )

    draw_text(
        "1 PISTOL   2 SHOTGUN   3 RIFLE     R RELOAD     F FLASHLIGHT     ESC PAUSE",
        small_font,
        (174, 188, 175),
        (WIDTH // 2, HEIGHT - 25),
    )


def shoot():

    weapon = game["weapon"]

    spec = WEAPONS[weapon]

    target_x, target_y = logical_mouse_pos()

    player = game["player"]

    offsets = [0]

    if weapon == "Shotgun":

        offsets = [-0.20, -0.10, 0, 0.10, 0.20]

    for offset in offsets:

        game["bullets"].append(
            Bullet(
                player.rect.centerx,
                player.rect.centery,
                target_x,
                target_y,
                weapon,
                offset,
            )
        )

    game["ammo"][weapon] -= spec["ammo_cost"]

    game["last_shot"] = pygame.time.get_ticks()

    game["muzzle_until"] = pygame.time.get_ticks() + (95 if weapon == "Shotgun" else 55)

    game["muzzle_angle"] = math.atan2(
        target_y - player.rect.centery, target_x - player.rect.centerx
    )

    player.recoil = 5

    for _ in range(4 if weapon == "Shotgun" else 2):

        game["effects"].append(
            {
                "x": player.rect.centerx,
                "y": player.rect.centery,
                "vx": random.uniform(-2, 2),
                "vy": random.uniform(-2, 2),
                "life": random.randint(8, 16),
                "kind": "spark",
            }
        )

    if sound_on:

        play_sound("shotgun" if weapon == "Shotgun" else "shoot")


def update_game():

    global high_score

    now = pygame.time.get_ticks()

    player = game["player"]
    game["survival_time"] = max(0, (now - game["started_at"]) // 1000)

    weapon = game["weapon"]

    spec = WEAPONS[weapon]

    player.update()

    if game["reloading"] and now - game["reload_start"] >= spec["reload"]:

        needed = spec["mag"] - game["ammo"][weapon]

        amount = min(needed, game["reserve"][weapon])

        game["ammo"][weapon] += amount

        game["reserve"][weapon] -= amount

        game["reloading"] = False

    mouse = pygame.mouse.get_pressed()

    if (
        mouse[0]
        and not game["reloading"]
        and game["ammo"][weapon] > 0
        and now - game["last_shot"] >= spec["delay"]
    ):

        shoot()

    elif mouse[0] and game["ammo"][weapon] <= 0 and game["reserve"][weapon] > 0:

        game["reloading"] = True

        game["reload_start"] = now

    for bullet in game["bullets"][:]:

        bullet.update()

        if bullet.is_off_screen() or any(
            bullet.rect.colliderect(pygame.Rect(*o[:4])) for o in MAP_OBSTACLES
        ):

            game["bullets"].remove(bullet)

    for zombie in game["zombies"][:]:

        zombie.update(player)

        if zombie.rect.colliderect(player.rect):

            if player.take_damage():

                game["damage_flash"] = 9

                for _ in range(5):

                    game["effects"].append(
                        {
                            "x": player.rect.centerx,
                            "y": player.rect.centery,
                            "vx": random.uniform(-2, 2),
                            "vy": random.uniform(-2, 2),
                            "life": random.randint(8, 15),
                            "kind": "blood",
                        }
                    )

                if sound_on:

                    play_sound("hit")

    for bullet in game["bullets"][:]:

        hit = False

        for zombie in game["zombies"][:]:

            if bullet.rect.colliderect(zombie.rect):

                zombie.health -= bullet.damage

                zombie.hit_flash = 5

                for _ in range(7):

                    game["effects"].append(
                        {
                            "x": zombie.rect.centerx,
                            "y": zombie.rect.centery,
                            "vx": random.uniform(-3, 3),
                            "vy": random.uniform(-3, 3),
                            "life": random.randint(10, 24),
                            "kind": "blood",
                        }
                    )

                if bullet in game["bullets"]:

                    game["bullets"].remove(bullet)

                hit = True

                if zombie.health <= 0:

                    game["zombies"].remove(zombie)

                    game["score"] += 10

                    game["kills"] += 1

                    if random.random() < POWERUP_DROP_CHANCE:

                        kind = random.choice(["health", "ammo"])

                        game["powerups"].append(
                            PowerUp(zombie.rect.centerx, zombie.rect.centery, kind)
                        )

                break

        if hit:

            continue

    for powerup in game["powerups"][:]:

        if powerup.update():

            game["powerups"].remove(powerup)

        elif powerup.rect.colliderect(player.rect):

            if powerup.kind == "health":

                player.health = min(PLAYER_MAX_HEALTH, player.health + 25)

            else:

                for name in WEAPON_ORDER:

                    game["reserve"][name] += 12 if name != "Rifle" else 30

            game["powerups"].remove(powerup)

            if sound_on:

                play_sound("pickup")

    if not game["zombies"] and player.health > 0:

        game["wave"] += 1

        game["wave_start"] = now

        game["wave_message"] = True

        game["zombies"] = spawn_wave(game["wave"])

        if sound_on:

            play_sound("wave")

    if player.health <= 0:

        game["game_over"] = True

        if game["score"] > high_score:

            # update global persistent high score

            high_score = game["score"]

            save_high_score(high_score)



# Create the darkness surface once instead of every frame
darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
_damage_flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

def apply_darkness(player, aim_pos):
    darkness.fill((2, 4, 7, 225))

    px, py = player.rect.center

    # Visible area around the player
    pygame.draw.circle(
        darkness, (0, 0, 0, 0), (px, py), 65
    )

    if game["flashlight_on"]:
        dx = aim_pos[0] - px
        dy = aim_pos[1] - py
        angle = math.atan2(dy, dx)

        beam_length = 310
        half_angle = math.radians(24)
        segments = 28

        points = [(px, py)]

        for i in range(segments + 1):
            a = angle - half_angle + (
                2 * half_angle * i / segments
            )
            x = px + math.cos(a) * beam_length
            y = py + math.sin(a) * beam_length
            points.append((int(x), int(y)))

        pygame.draw.polygon(
            darkness, (0, 0, 0, 0), points
        )

    screen.blit(darkness, (0, 0))

def draw_effects():

    now = pygame.time.get_ticks()

    # Fade out particles smoothly; draw each as a tiny directional streak.

    for effect in game["effects"][:]:

        effect["x"] += effect["vx"]

        effect["y"] += effect["vy"]

        effect["life"] -= 1

        if effect["life"] <= 0:

            game["effects"].remove(effect)

            continue

        color = (255, 179, 72) if effect["kind"] == "spark" else (132, 24, 29)

        radius = max(1, min(4, effect["life"] // 3))

        pygame.draw.circle(screen, color, (int(effect["x"]), int(effect["y"])), radius)

    if now < game["muzzle_until"]:

        player = game["player"]

        angle = game["muzzle_angle"]

        origin = (
            player.rect.centerx + int(math.cos(angle) * 23),
            player.rect.centery + int(math.sin(angle) * 23),
        )

        tip = (
            origin[0] + int(math.cos(angle) * 29),
            origin[1] + int(math.sin(angle) * 29),
        )

        side1 = (
            origin[0] + int(math.cos(angle + 1.0) * 10),
            origin[1] + int(math.sin(angle + 1.0) * 10),
        )

        side2 = (
            origin[0] + int(math.cos(angle - 1.0) * 10),
            origin[1] + int(math.sin(angle - 1.0) * 10),
        )

        pygame.draw.polygon(screen, (255, 194, 72), [origin, side1, tip, side2])

        pygame.draw.circle(screen, (255, 244, 190), origin, 5)


def draw_game():

    draw_arena()

    for powerup in game["powerups"]:

        powerup.draw()

    for bullet in game["bullets"]:

        bullet.draw(screen)

    aim = logical_mouse_pos()

    game["player"].draw(screen, aim)

    for zombie in game["zombies"]:

        zombie.draw(screen)

    draw_effects()

    apply_darkness(game["player"], aim)

    draw_hud()

    draw_minimap()

    if game["damage_flash"] > 0:

        flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        flash.fill((155, 15, 20, game["damage_flash"] * 3))

        screen.blit(flash, (0, 0))

        game["damage_flash"] -= 1

    if game["wave_message"] and not game["game_over"]:

        if pygame.time.get_ticks() - game["wave_start"] < WAVE_MESSAGE_DURATION:

            draw_text(
                f"WAVE {game['wave']}", big_font, WHITE, (WIDTH // 2, HEIGHT // 2 - 55)
            )

        else:

            game["wave_message"] = False


def draw_pause():

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    overlay.fill((0, 0, 0, 185))
    screen.blit(overlay, (0, 0))

    panel(
        pygame.Rect(WIDTH // 2 - 235, HEIGHT // 2 - 135, 470, 270),
        (7, 13, 14, 245),
        (83, 117, 91),
        14,
    )

    draw_text("MISSION PAUSED", title_font, YELLOW, (WIDTH // 2, HEIGHT // 2 - 70))

    draw_text("Press ESC / P to resume", font, WHITE, (WIDTH // 2, HEIGHT // 2))

    draw_text(
        "Press M to return to title screen",
        small_font,
        (169, 184, 171),
        (WIDTH // 2, HEIGHT // 2 + 45),
    )


def draw_game_over():

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    overlay.fill((0, 0, 0, 205))
    screen.blit(overlay, (0, 0))

    panel(
        pygame.Rect(WIDTH // 2 - 290, HEIGHT // 2 - 205, 580, 410),
        (9, 12, 14, 245),
        (111, 63, 57),
        14,
    )

    draw_text("OPERATOR DOWN", title_font, RED, (WIDTH // 2, HEIGHT // 2 - 110))

    draw_text(
        "MISSION REPORT", small_font, (167, 179, 168), (WIDTH // 2, HEIGHT // 2 - 61)
    )

    draw_text(
        f"FINAL SCORE   {game['score']:06d}",
        big_font,
        WHITE,
        (WIDTH // 2, HEIGHT // 2 - 10),
    )

    draw_text(
        f"WAVE REACHED  {game['wave']}     HOSTILES ELIMINATED  {game['kills']}",
        small_font,
        YELLOW,
        (WIDTH // 2, HEIGHT // 2 + 32),
    )

    elapsed = int(game.get("survival_time", 0))
    minutes, seconds = divmod(elapsed, 60)
    draw_text(
        f"SURVIVAL TIME  {minutes:02d}:{seconds:02d}",
        font,
        (183, 202, 179),
        (WIDTH // 2, HEIGHT // 2 + 72),
    )

    draw_text(
        f"PERSONAL BEST  {high_score:06d}",
        font,
        (183, 202, 179),
        (WIDTH // 2, HEIGHT // 2 + 112),
    )

    draw_text(
        "R REDEPLOY    ENTER MAIN MENU    ESC QUIT",
        small_font,
        WHITE,
        (WIDTH // 2, HEIGHT // 2 + 158),
    )


display = pygame.display.set_mode((WIDTH, HEIGHT))
screen = pygame.Surface((WIDTH, HEIGHT)).convert()

# The arena is static, so render it once instead of redrawing hundreds of
# floor tiles, cracks, debris and obstacles on every gameplay frame.
_arena_draw_original = draw_arena
_arena_background = pygame.Surface((WIDTH, HEIGHT)).convert()
_screen_before_arena_cache = screen
screen = _arena_background
_arena_draw_original()
screen = _screen_before_arena_cache

def draw_arena():
    screen.blit(_arena_background, (0, 0))

fullscreen = False

running = True

while running:
    

    dt = clock.tick(FPS)
    pygame.display.set_caption(
    f"Zombie Survival | FPS: {clock.get_fps():.1f} | Frame: {dt} ms"
)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if scene == "menu":

                if event.key in (pygame.K_RETURN, pygame.K_SPACE) and not (
                    event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT
                ):

                    game = reset_game()

                    scene = "game"

                elif event.key == pygame.K_ESCAPE:

                    running = False

                elif event.key == pygame.K_b: 
                    sound_on = not sound_on

                    apply_music_settings()

                elif event.key in (
                    pygame.K_MINUS,
                    pygame.K_KP_MINUS,
                    pygame.K_LEFTBRACKET,
                ):

                    music_volume = max(0.0, round(music_volume - 0.05, 2))

                    apply_music_settings()

                elif event.key in (
                    pygame.K_EQUALS,
                    pygame.K_PLUS,
                    pygame.K_KP_PLUS,
                    pygame.K_RIGHTBRACKET,
                ):

                    music_volume = min(1.0, round(music_volume + 0.05, 2))

                    apply_music_settings()

            elif scene == "settings":
                if event.key == pygame.K_ESCAPE:
                    scene = settings_return_scene

            elif scene == "game":

                if event.key in (pygame.K_ESCAPE, pygame.K_p):

                    game["paused"] = not game["paused"]

                elif event.key == pygame.K_m:

                    scene = "menu"

                elif event.key == pygame.K_f:

                    game["flashlight_on"] = not game["flashlight_on"]

                elif event.key == pygame.K_r and not game["game_over"]:

                    weapon = game["weapon"]

                    if (
                        not game["reloading"]
                        and game["ammo"][weapon] < WEAPONS[weapon]["mag"]
                        and game["reserve"][weapon] > 0
                    ):

                        game["reloading"] = True

                        game["reload_start"] = pygame.time.get_ticks()

                        if sound_on:

                            play_sound("reload")

                elif (
                    event.key in (pygame.K_1, pygame.K_2, pygame.K_3)
                    and not game["game_over"]
                ):

                    game["weapon"] = WEAPON_ORDER[event.key - pygame.K_1]

                    game["reloading"] = False

                elif event.key == pygame.K_b:

                    sound_on = not sound_on

                    apply_music_settings()

            elif scene == "game" and game["game_over"]:

                pass

        if (
            scene == "menu"
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):

            mx, my = logical_mouse_pos(event.pos)

            if WIDTH // 2 - 155 <= mx <= WIDTH // 2 + 155 and 328 <= my <= 376:

                game = reset_game()

                scene = "game"

            elif WIDTH // 2 - 155 <= mx <= WIDTH // 2 - 10 and 388 <= my <= 428:

                music_on = not music_on
                apply_music_settings()

            elif WIDTH // 2 + 10 <= mx <= WIDTH // 2 + 155 and 388 <= my <= 428:

                settings_return_scene = "menu"
                scene = "settings"

            elif WIDTH // 2 - 155 <= mx <= WIDTH // 2 - 113 and 466 <= my <= 500:

                music_volume = max(0.0, round(music_volume - 0.05, 2))

                apply_music_settings()

            elif WIDTH // 2 - 100 <= mx <= WIDTH // 2 + 58 and 470 <= my <= 496:

                music_volume = max(0.0, min(1.0, (mx - (WIDTH // 2 - 100)) / 158))

                apply_music_settings()

            elif WIDTH // 2 + 67 <= mx <= WIDTH // 2 + 109 and 466 <= my <= 500:

                music_volume = min(1.0, round(music_volume + 0.05, 2))

                apply_music_settings()

        if scene == "settings" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = logical_mouse_pos(event.pos)
            if 155 <= my <= 197 and WIDTH // 2 - 210 <= mx <= WIDTH // 2 - 10:
                music_on = not music_on
                apply_music_settings()
            elif 155 <= my <= 197 and WIDTH // 2 + 10 <= mx <= WIDTH // 2 + 210:
                sound_on = not sound_on
                apply_music_settings()
            elif 225 <= my <= 255 and WIDTH // 2 - 100 <= mx <= WIDTH // 2 + 100:
                music_volume = max(0.0, min(1.0, (mx - (WIDTH // 2 - 100)) / 200))
                apply_music_settings()
            elif 300 <= my <= 330 and WIDTH // 2 - 100 <= mx <= WIDTH // 2 + 100:
                sfx_volume = max(0.0, min(1.0, (mx - (WIDTH // 2 - 100)) / 200))
                apply_music_settings()
            elif 385 <= my <= 430:
                if WIDTH // 2 - 210 <= mx <= WIDTH // 2 - 80:
                    difficulty = "Easy"
                elif WIDTH // 2 - 70 <= mx <= WIDTH // 2 + 60:
                    difficulty = "Normal"
                elif WIDTH // 2 + 70 <= mx <= WIDTH // 2 + 200:
                    difficulty = "Hard"
            elif 455 <= my <= 500 and WIDTH // 2 - 210 <= mx <= WIDTH // 2 - 10:
                toggle_fullscreen()
            elif 575 <= my <= 620 and WIDTH // 2 - 125 <= mx <= WIDTH // 2 + 125:
                scene = settings_return_scene

        if scene == "settings" and event.type == pygame.MOUSEMOTION and event.buttons[0]:
            mx, my = logical_mouse_pos(event.pos)
            if 225 <= my <= 255 and WIDTH // 2 - 100 <= mx <= WIDTH // 2 + 100:
                music_volume = max(0.0, min(1.0, (mx - (WIDTH // 2 - 100)) / 200))
                apply_music_settings()
            elif 300 <= my <= 330 and WIDTH // 2 - 100 <= mx <= WIDTH // 2 + 100:
                sfx_volume = max(0.0, min(1.0, (mx - (WIDTH // 2 - 100)) / 200))
                apply_music_settings()

        if event.type == pygame.KEYDOWN and (
            event.key == pygame.K_F11
            or (event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT)
        ):

            toggle_fullscreen()

        if (
            scene == "menu"
            and event.type == pygame.MOUSEMOTION
            and event.buttons[0]
            and WIDTH // 2 - 110 <= logical_mouse_pos(event.pos)[0] <= WIDTH // 2 + 68
            and 470 <= logical_mouse_pos(event.pos)[1] <= 496
        ):

            mouse_x, _ = logical_mouse_pos(event.pos)
            music_volume = max(0.0, min(1.0, (mouse_x - (WIDTH // 2 - 100)) / 158))

            apply_music_settings()

    if scene == "menu":
        draw_menu()

    elif scene == "settings":
        draw_settings()

    elif scene == "game":

        if not game["paused"] and not game["game_over"]:

            update_game()

        draw_game()

        if game["paused"] and not game["game_over"]:

            draw_pause()

        if game["game_over"]:

            draw_game_over()

            keys = pygame.key.get_pressed()

            if keys[pygame.K_r]:

                game = reset_game()

            elif keys[pygame.K_RETURN]:

                scene = "menu"

            elif keys[pygame.K_ESCAPE]:

                running = False

    present_screen()


pygame.quit()

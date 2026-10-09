import math
import os
import random
import pygame

from settings import *
from player import Player
from zombie import Zombie
from bullet import Bullet

pygame.init()
try:
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except pygame.error:
    SOUND_AVAILABLE = False

# Background music
if SOUND_AVAILABLE:
    pygame.mixer.music.load("assets/gameplay_music.mp3")
    pygame.mixer.music.set_volume(0.25)
    pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
            samples.append(int(amplitude * fade * math.sin(2 * math.pi * frequency * i / sample_rate)))
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
    if sound:
        try:
            sound.play()
        except pygame.error:
            pass

def draw_text(text, font_obj, color, center, surface=screen):
    image = font_obj.render(str(text), True, color)
    surface.blit(image, (center[0] - image.get_width() // 2,
                         center[1] - image.get_height() // 2))

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as file:
            return max(0, int(file.read().strip() or "0"))
    except (OSError, ValueError):
        return 0

def save_high_score(value):
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as file:
            file.write(str(int(value)))
    except OSError:
        pass

high_score = load_high_score()

# Background details are drawn procedurally, so no image downloads are needed.
random.seed(14)
floor_marks = []
for _ in range(95):
    floor_marks.append((random.randint(18, WIDTH - 18),
                        random.randint(18, HEIGHT - 18),
                        random.randint(2, 5)))
random.seed()

def draw_arena():
    screen.fill((20, 25, 28))
    # Floor tiles
    tile = 50
    for x in range(0, WIDTH, tile):
        for y in range(0, HEIGHT, tile):
            shade = 24 if ((x // tile + y // tile) % 2 == 0) else 28
            pygame.draw.rect(screen, (shade, shade + 3, shade + 4),
                             (x, y, tile, tile))
    for x, y, radius in floor_marks:
        pygame.draw.circle(screen, (37, 43, 43), (x, y), radius)
    # Arena boundary
    pygame.draw.rect(screen, (82, 91, 90), (5, 5, WIDTH - 10, HEIGHT - 10), 4, border_radius=8)
    pygame.draw.rect(screen, (12, 15, 18), (12, 12, WIDTH - 24, HEIGHT - 24), 2, border_radius=7)
    # Decorative corner warning stripes
    for x in range(22, 92, 14):
        pygame.draw.line(screen, (130, 91, 45), (x, 20), (x + 8, 20), 4)
        pygame.draw.line(screen, (130, 91, 45), (x, HEIGHT - 20), (x + 8, HEIGHT - 20), 4)

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
            pygame.draw.rect(screen, WHITE, (self.rect.centerx - 3, self.rect.centery - 7, 6, 14))
            pygame.draw.rect(screen, WHITE, (self.rect.centerx - 7, self.rect.centery - 3, 14, 6))
        else:
            pygame.draw.rect(screen, WHITE, (self.rect.centerx - 5, self.rect.centery - 7, 10, 14), 2)
            pygame.draw.line(screen, WHITE, (self.rect.centerx - 2, self.rect.centery - 3),
                             (self.rect.centerx + 2, self.rect.centery + 3), 2)

def spawn_wave(wave_number):
    result = []
    count = ZOMBIES_PER_WAVE + (wave_number - 1) * ZOMBIES_INCREASE_PER_WAVE
    for _ in range(count):
        side = random.choice(("top", "bottom", "left", "right"))
        if side == "top":
            x, y = random.randint(25, WIDTH - ZOMBIE_SIZE - 25), 22
        elif side == "bottom":
            x, y = random.randint(25, WIDTH - ZOMBIE_SIZE - 25), HEIGHT - ZOMBIE_SIZE - 22
        elif side == "left":
            x, y = 22, random.randint(25, HEIGHT - ZOMBIE_SIZE - 25)
        else:
            x, y = WIDTH - ZOMBIE_SIZE - 22, random.randint(25, HEIGHT - ZOMBIE_SIZE - 25)
        result.append(Zombie(x, y, wave_number))
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
    }
    state["zombies"] = spawn_wave(1)
    return state

game = reset_game()
scene = "menu"
sound_on = True

def draw_button(label, rect, selected=False):
    color = (58, 77, 70) if selected else (39, 47, 51)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (115, 137, 128), rect, 2, border_radius=8)
    draw_text(label, font, WHITE, rect.center)

def draw_menu():
    draw_arena()
    # Dark translucent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((4, 7, 10, 205))
    screen.blit(overlay, (0, 0))
    draw_text("ZOMBIE SURVIVAL", title_font, GREEN, (WIDTH // 2, 145))
    draw_text("THE LAST STAND", big_font, WHITE, (WIDTH // 2, 205))
    draw_text("Survive the waves. Don't get surrounded.", font, (185, 197, 190), (WIDTH // 2, 255))
    draw_button("START GAME", pygame.Rect(WIDTH // 2 - 125, 315, 250, 52))
    draw_button("SOUND: ON" if sound_on else "SOUND: OFF",
                pygame.Rect(WIDTH // 2 - 125, 385, 250, 46))
    draw_text(f"HIGH SCORE  {high_score}", font, YELLOW, (WIDTH // 2, 470))
    draw_text("WASD / Arrows: Move    Mouse: Aim & Shoot    R: Reload    1-3: Weapons",
              small_font, WHITE, (WIDTH // 2, 535))
    draw_text("ESC: Pause in game / Quit from menu", small_font, (180, 190, 190), (WIDTH // 2, 565))

def draw_hud():
    # Health panel
    pygame.draw.rect(screen, (7, 10, 12), (20, 18, 224, 82), border_radius=8)
    pygame.draw.rect(screen, (85, 95, 95), (20, 18, 224, 82), 2, border_radius=8)
    draw_text(f"HEALTH  {game['player'].health}", font, WHITE, (105, 38))
    ratio = max(0, min(1, game["player"].health / PLAYER_MAX_HEALTH))
    pygame.draw.rect(screen, (70, 24, 29), (32, 55, 198, 18), border_radius=4)
    pygame.draw.rect(screen, GREEN if ratio > .35 else RED,
                     (32, 55, int(198 * ratio), 18), border_radius=4)
    draw_text(f"SCORE  {game['score']}", font, WHITE, (WIDTH - 100, 32))
    draw_text(f"WAVE  {game['wave']}", font, YELLOW, (WIDTH - 100, 62))
    weapon = game["weapon"]
    ammo = game["ammo"][weapon]
    reserve = game["reserve"][weapon]
    ammo_label = f"RELOADING {max(0, WEAPONS[weapon]['reload'] - (pygame.time.get_ticks() - game['reload_start']) ) / 1000:.1f}s" if game["reloading"] else f"{weapon.upper()}  {ammo}/{reserve}"
    draw_text(ammo_label, font, BLUE if game["reloading"] else WHITE, (WIDTH // 2, 35))
    draw_text("1 Pistol   2 Shotgun   3 Rifle   |   R Reload   |   ESC Pause",
              small_font, (190, 198, 198), (WIDTH // 2, HEIGHT - 22))

def shoot():
    weapon = game["weapon"]
    spec = WEAPONS[weapon]
    target_x, target_y = pygame.mouse.get_pos()
    player = game["player"]
    offsets = [0]
    if weapon == "Shotgun":
        offsets = [-0.20, -0.10, 0, 0.10, 0.20]
    for offset in offsets:
        game["bullets"].append(Bullet(player.rect.centerx, player.rect.centery,
                                      target_x, target_y, weapon, offset))
    game["ammo"][weapon] -= spec["ammo_cost"]
    game["last_shot"] = pygame.time.get_ticks()
    if sound_on:
        play_sound("shotgun" if weapon == "Shotgun" else "shoot")

def update_game():
    global high_score
    now = pygame.time.get_ticks()
    player = game["player"]
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
    if (mouse[0] and not game["reloading"] and game["ammo"][weapon] > 0
            and now - game["last_shot"] >= spec["delay"]):
        shoot()
    elif mouse[0] and game["ammo"][weapon] <= 0 and game["reserve"][weapon] > 0:
        game["reloading"] = True
        game["reload_start"] = now

    for bullet in game["bullets"][:]:
        bullet.update()
        if bullet.is_off_screen():
            game["bullets"].remove(bullet)

    for zombie in game["zombies"][:]:
        zombie.update(player)
        if zombie.rect.colliderect(player.rect):
            if player.take_damage() and sound_on:
                play_sound("hit")

    for bullet in game["bullets"][:]:
        hit = False
        for zombie in game["zombies"][:]:
            if bullet.rect.colliderect(zombie.rect):
                zombie.health -= bullet.damage
                if bullet in game["bullets"]:
                    game["bullets"].remove(bullet)
                hit = True
                if zombie.health <= 0:
                    game["zombies"].remove(zombie)
                    game["score"] += 10
                    if random.random() < POWERUP_DROP_CHANCE:
                        kind = random.choice(["health", "ammo"])
                        game["powerups"].append(PowerUp(zombie.rect.centerx,
                                                        zombie.rect.centery, kind))
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

def draw_game():
    draw_arena()
    for powerup in game["powerups"]:
        powerup.draw()
    for bullet in game["bullets"]:
        bullet.draw(screen)
    aim = pygame.mouse.get_pos()
    game["player"].draw(screen, aim)
    for zombie in game["zombies"]:
        zombie.draw(screen)
    draw_hud()
    if game["wave_message"] and not game["game_over"]:
        if pygame.time.get_ticks() - game["wave_start"] < WAVE_MESSAGE_DURATION:
            draw_text(f"WAVE {game['wave']}", big_font, WHITE, (WIDTH // 2, HEIGHT // 2 - 55))
        else:
            game["wave_message"] = False

def draw_pause():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    screen.blit(overlay, (0, 0))
    draw_text("PAUSED", title_font, YELLOW, (WIDTH // 2, 220))
    draw_text("Press ESC or P to resume", font, WHITE, (WIDTH // 2, 290))
    draw_text("Press M to return to main menu", font, WHITE, (WIDTH // 2, 335))

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 195))
    screen.blit(overlay, (0, 0))
    draw_text("GAME OVER", title_font, RED, (WIDTH // 2, 210))
    draw_text(f"FINAL SCORE  {game['score']}", big_font, WHITE, (WIDTH // 2, 285))
    draw_text(f"HIGH SCORE  {high_score}", font, YELLOW, (WIDTH // 2, 340))
    draw_text("R: Restart    ENTER: Main Menu    ESC: Quit", font, WHITE, (WIDTH // 2, 410))

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if scene == "menu":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game = reset_game()
                    scene = "game"
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s:
                    sound_on = not sound_on
            elif scene == "game":
                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    game["paused"] = not game["paused"]
                elif event.key == pygame.K_m:
                    scene = "menu"
                elif event.key == pygame.K_r and not game["game_over"]:
                    weapon = game["weapon"]
                    if (not game["reloading"]
                            and game["ammo"][weapon] < WEAPONS[weapon]["mag"]
                            and game["reserve"][weapon] > 0):
                        game["reloading"] = True
                        game["reload_start"] = pygame.time.get_ticks()
                        if sound_on:
                            play_sound("reload")
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3) and not game["game_over"]:
                    game["weapon"] = WEAPON_ORDER[event.key - pygame.K_1]
                    game["reloading"] = False
                elif event.key == pygame.K_s:
                    sound_on = not sound_on
            elif scene == "game" and game["game_over"]:
                pass

        if scene == "menu" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if WIDTH // 2 - 125 <= mx <= WIDTH // 2 + 125 and 315 <= my <= 367:
                game = reset_game()
                scene = "game"
            elif WIDTH // 2 - 125 <= mx <= WIDTH // 2 + 125 and 385 <= my <= 431:
                sound_on = not sound_on

    if scene == "menu":
        draw_menu()
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

    pygame.display.flip()

pygame.quit()

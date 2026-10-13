# Zombie Survival: The Last Stand

A top-down Pygame survival game with increasing zombie waves, weapon switching and reloads, power-ups, flashlight, radar, sound effects and a gritty procedural arena.

## Run from source

Requirements: Python 3.10+ and Pygame.

```powershell
python -m pip install -r requirements.txt
python main.py
```

## Controls

- **WASD / Arrow keys:** move
- **Mouse:** aim and fire
- **1 / 2 / 3:** select pistol / shotgun / rifle
- **R:** reload
- **F:** flashlight
- **ESC / P:** pause or resume
- **M:** return to title menu while playing
- **F11 / Alt+Enter:** toggle fullscreen / windowed
- **B:** toggle sound effects on/off
- **- / +:** adjust music volume on the title screen

## Settings

Choose **Settings** on the title screen to change music and sound-effects volume independently, toggle either audio channel, choose Easy / Normal / Hard difficulty, and switch fullscreen/windowed mode. Difficulty changes zombie count, speed and health.

The game-over mission report includes final score, wave reached, hostiles eliminated, survival time and personal best.

## Assets and saved scores

The background track is `assets/gameplay_music.wav`. The game can continue without audio if the mixer or audio device is unavailable. High scores are saved beside the source/game when writable, with a per-user save location fallback for protected install folders.

This is a source-only update. No EXE has been built.

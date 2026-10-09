ZOMBIE SURVIVAL: THE LAST STAND
===============================

REQUIREMENTS
- Python 3.10+ recommended
- pygame

INSTALL
1. Open this folder in VS Code.
2. Open Terminal > New Terminal.
3. Run:
   py -m pip install pygame
4. Run:
   py main.py

CONTROLS
- WASD or Arrow Keys: Move
- Mouse: Aim
- Left Mouse Button: Shoot
- 1: Pistol
- 2: Shotgun (fires a spread of pellets)
- 3: Rifle (rapid fire)
- R: Reload
- ESC or P: Pause/resume
- M: Return to main menu (while playing)
- Enter/Space: Start from main menu
- R: Restart after game over
- Enter: Main menu after game over

FEATURES
- Top-down zombie survival with progressively harder waves
- Procedurally drawn arena, player, zombies, bullets and power-ups
- Pistol, shotgun, rifle, weapon-specific ammo and reload times
- Health and ammo pickups can drop from zombies
- Synthesized sound effects if the system audio mixer is available
- Main menu, pause overlay, game-over screen and local high score
- No external images/audio assets are required

NOTES
- highscore.txt is created in the working directory after you achieve a new high score.
- If pygame audio cannot initialize, the game still runs without sound.
- Run main.py from this folder so the high score file is saved here.

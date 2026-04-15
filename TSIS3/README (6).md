# TSIS3 - Snake Game with Database Integration

## Files
- `main.py` - app entry point
- `game.py` - game logic and screens
- `db.py` - PostgreSQL functions
- `config.py` - DB credentials
- `settings.json` - local settings
- `assets/` - optional folder for sounds/images

## Features completed
- PostgreSQL tables:
  - `players`
  - `game_sessions`
- Username entry on main menu
- Auto-save result after game over
- Leaderboard screen with top 10 scores
- Personal best shown during gameplay
- Poison food shortens snake by 2
- Power-ups:
  - speed boost
  - slow motion
  - shield
- Obstacles from level 3
- `settings.json`:
  - snake color
  - grid overlay
  - sound toggle
- Screens:
  - Main Menu
  - Game Over
  - Leaderboard
  - Settings

## Install
```bash
pip install pygame psycopg2-binary
```

## Run
```bash
python main.py
```

## Important
Edit `config.py` first with your PostgreSQL username and password.

## Controls
- Arrow keys to move snake
- Main menu: type username with keyboard
- Settings: click buttons

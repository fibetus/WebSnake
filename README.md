# s30331-python-game

# Snake Game

A classic Snake game implementation in Python.

## Overview

This is a simple implementation of the classic Snake game where you control a snake that grows longer as it eats food. The game ends if the snake hits the wall or collides with itself.

## Features

- Grid-based movement system
- Progressively increasing difficulty as your score grows
- Simple and intuitive controls

## Requirements

- Python Interpreter
- Libraries listed in the `requirements.txt` file

## Installation

1. Clone this repository:
```bash
git clone https://github.com/fibetus/s30331-python-game.git
cd s30331-python-game
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## How to Run

Run the game as an app with:
```bash
python main.py
```
Run the game in the web with:
- In first terminal:
```bash
python manage.py runserver
```
- In second terminal:
```bash
cd frontend
python -m http.server <port>
```
- Open your browser and type:
```bash
localhost:<port>
```

## Run with Arguments
- Run with `--history` flag to get Snake Game history

   ```bash
   python main.py --history
   ```
- Run with `--scores` flag to get current leaderboard for every map size

   ```bash
   python main.py --scores
   ```
- Run with `--map-size` flag to get filtered leaderboard by map size you write. 

   ```bash
   python main.py --scores --map-size [0-25]
   ```
   - Use with `--scores` flag. 
   - The argument after `--map-size` should be an integer between 5-25.


## Controls

- **Arrow Keys / WSAD**: Control the snake's direction
- **R**: Restart the game after game over
- **Q**: Quit the game (only in app)

## Game Rules

1. Navigate the snake around the grid using the arrow keys
2. Eat the red food to grow longer and increase your score
3. The game ends if the snake:
   - Hits the wall (goes beyond the grid)
   - Collides with its own body

## Testing

Run the tests with:
```bash
pytest
```

## Development

This project follows TDD and a modular design pattern, separating the game logic from the UI implementation. Now we also have Django implementation! This makes it easy to:

1. Extend the game with new features
2. Test the game logic independently
3. Implement alternative UIs (e.g., web-based, terminal-based) without changing the core logic


## Contributors

- @fibetus

---

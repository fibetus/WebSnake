# s30331-python-game

# Snake Game

A classic Snake game implementation in Python using Pygame.

## Overview

This is a simple implementation of the classic Snake game where you control a snake that grows longer as it eats food. The game ends if the snake hits the wall or collides with itself.

## Features

- Grid-based movement system
- Progressively increasing difficulty as your score grows
- Simple and intuitive controls

## Requirements

- Python 3.6+
- Pygame library

## Installation

1. Clone this repository:
```bash
git clone https://github.com/fibetus/s30331-python-game.git
cd snake-game
```

2. Install the required dependencies:
```bash
pip install pygame pytest
```

## How to Run

Run the game with:
```bash
python main.py
```

## Controls

- **Arrow Keys / WSAD**: Control the snake's direction
- **R**: Restart the game after game over
- **Q**: Quit the game

## Game Rules

1. Navigate the snake around the grid using the arrow keys
2. Eat the red food to grow longer and increase your score
3. The game ends if the snake:
   - Hits the wall (goes beyond the grid)
   - Collides with its own body

## Project Structure

- `engine_core.py`: Contains the core game logic
- `ui.py`: Contains the Pygame user interface implementation
- `main.py`: Entry point that connects game logic with UI
- `test_engine.py`: Contains tests for `engine_core.py`

## Testing

Run the tests with:
```bash
pytest
```

## Development

This project follows TDD and a modular design pattern, separating the game logic from the UI implementation. This makes it easy to:

1. Extend the game with new features
2. Test the game logic independently
3. Implement alternative UIs (e.g., web-based, terminal-based) without changing the core logic


## Contributors

- @fibetus

---

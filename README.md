# Hexagonal Chess

This is a Python based implementation of [Gliński's hexagonal chess](https://en.wikipedia.org/wiki/Hexagonal_chess) using Pygame. 

## Installation

To install and run the game, follow these steps:

1. Clone the repository to your local machine ```git clone git@github.com:Bcsotty/HexagonalChess.git```
2. Setup a virtual environment ```python3 -m venv /path/to/virtual/environment```
3. Once the environment is configured, activate it ```source {environment_folder}/bin/activate```
4. Install the requirements ```pip install -r requirements.txt```
5. Run the game ```python3 src/main.py```

## Test Mode
Test mode allows you to spawn pieces and delete them freely, allowing easy testing of the various pieces. To spawn a piece, the keybindings are:

p - Pawn
k - King
q - Queen
n - Knight
b - Bishop
r - Rook

By default, the pieces spawn as white. To spawn them as a black piece instead, hold shift while pressing the key. Once the key is pressed, so long as your cursor is hovering
over an unoccupied tile it will place the piece. Test mode does NOT enforce movement or turn rules. This means you can play any color at any time, and you can move pieces wherever
you want regardless of the visible possible moves.

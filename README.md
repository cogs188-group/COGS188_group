# COGS188 AI Tetris Backtracking Implementation

### Background 

AI Tetris is an AI-driven implementation of Tetris that uses backtracking and heuristics to determine optimal moves. The project simulates Tetris gameplay by exploring legal moves for the active piece and evaluating board states based on factors like aggregate height, holes, and bumpiness. The main logic of our code is located in `AI.py` with our backtracking implementation and heuristics. We also have our overall design and code structure of `AI.py` in the `DesignDocument.md`. Lastly a report on our results is located at `FinalProject_YourGroupNameHere.ipynb`.


### How to Run the Project

To run tetris manually run the command: `python run_tetris.py`

To backtracking, use: `python run_tetris.py -backtracking`

### Simulate Multiple Games

You can also run multiple games (100 games for example) with: `python run_multiple_tetris.py -num_games 100`

Additional Flags:
* -watch: Displays the game visually using Pygame for one game
* -step: Waits for a keypress before each move
* -max_moves <number>: Limits the number of moves per game
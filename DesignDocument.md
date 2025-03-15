# Design Document for AI Tetris

Our goal is to use backtracking and heuristics to use AI to play tetris. At each main stage of backtracking we preload 10 (we can change this at any time see 2.4 backtracking_search) pieces, search for all legal placements (rotation and x-coordinate) for each piece, then select the sequence of placements that yields the highest board evaluation. We can explore branch pruning and more advanced heuristics once we implement the base version.

---

## 1. Modifications to Tetris.py

### 1.1. Modified Function: `freeze`

- **Signature:**  
  `freeze(self) -> None`

- **Return:**  
  None

- **Description:**  
  This function finalizes the active piece by merging it into the board. For AI mode, modify `freeze` to:
  - Immediately update the board without delays or key-dependent checks.
  - Use a flag (`ai_mode`) so that, when enabled, delays (like `time.sleep`) and interactive logic are bypassed.
  Overall we likely want the game to freeze after placing each piece for a bit so the user can see the ai's moves.
---

### 1.2. New Function: `apply_placement`

- **Signature:**  
  `apply_placement(self, rotation: int, x: int) -> None`

- **Return:**  
  None

- **Description:**  
  This function executes a complete move for the active piece by:
  - Setting the piece’s rotation to the given `rotation`.
  - Positioning the piece at the provided horizontal coordinate `x`.
  - Instantly dropping the piece (bypassing/speeding up animated movement) to its final landing position.
  - Calling the modified `freeze` to merge the piece into the board.
  
  This should only place legal finalized moves once the AI is done calculating.

---

### Notes:
- Besides these functions we also need to modify the main while loop to add an option if `ai_mode` 
is true to switch away from a playable game to an AI run game.

- `rotation` is an int 0 to 3 corresponding to the figure class already implemented
---

## 2. New File for AI Backend (AI.py)

This file is responsible for all the backtracking and calculations that go on in the background. Overall we 
want a backtracking algorithm that simulates all legal placements for the next 10 pieces and selects the optimal sequence
based on heuristics.

### 2.1. Function: `get_legal_placements`

- **Signature:**  
  `def get_legal_placements(tetris: Tetris, piece: Figure) -> List[Tuple[int, int]]:`

- **Return:**  
  A list of tuples, each tuple in the form `(rotation: int, x: int)`

- **Description:**  
  Iterates over each possible rotation and horizontal position for the given piece and determines if dropping it at that position 
  results in a valid placement (i.e., no collision). Returns all such legal placements.

 Note: we might be able to use the `intersects` function in Tetris for this

---

### 2.2. Function: `simulate_placement`

- **Signature:**  
  `def simulate_placement(tetris: Tetris, piece: Figure, rotation: int, x: int) -> Tetris:`

- **Return:**  
  A deep copy of the Tetris game state after the move is applied.

- **Description:**  
  Creates a deep copy of the current game state, sets the active piece’s rotation and x-position, and then applies the move using `apply_placement`. 
  This simulated state is used to evaluate the impact of that placement without altering the live game. Please ensure you are not modifying the passed in
  Tetris object.

---

### 2.3. Function: `evaluate_state`

- **Signature:**  
  `def evaluate_state(tetris: Tetris) -> float:`

- **Return:**  
  A numerical score representing how "good" the current board state is.

- **Description:**  
  Evaluates the board state based on heuristics such as:
  - Total number of cleared lines (or derived score)
  - Overall board height

 Note: Feel free to add anything more but I'd focus on the basic things first then once we get it working we can add more. 

---

### 2.4. Function: `backtracking_search`

- **Signature:**  
  `def backtracking_search(tetris: Tetris, pieces: List[Figure], depth: int) -> Tuple[List[Tuple[int, int]], float]:`

- **Return:**  
  A tuple containing:
  - A list of placements (each a tuple `(rotation, x)`) for the best sequence. Each tuple corresponds 
    to its piece's placement and rotation.
  - A float representing the evaluation score of the resulting board.

- **Description:**  
  Recursively simulates all legal moves for the current piece by:
  - Using `get_legal_placements` to generate valid moves.
  - For each move, creating a simulated game state with `simulate_placement`.
  - Recursing with the next piece until the set depth (10) is reached.
  
  At the leaf nodes, `evaluate_state` is used to score the board. The function returns the sequence of moves that maximizes the score.

---

### 2.5. Function: `get_next_moves`

- **Signature:**  
  `def get_next_moves(tetris: Tetris, pieces: List[Figure]) -> List[Tuple[int, int]]:`

- **Return:**  
  A list of placements (each a tuple `(rotation, x)`) for the next 10 moves.

- **Description:**  
  This is the main "starter" of AI.py that:
  - Randomly selects the next 10 pieces.
  - Calls `backtracking_search` with the current game state and the list of pieces.
  - Returns the optimal move sequence as determined by the backtracking search.
  
  The returned move sequence is then used to update the game board in AI mode by applying each move in order using `apply_placement`.

---

## 3. Overall Code Flow Overview

1. **Game Initialization (Tetris.py):**  
   - The Tetris game is initialized and, based on a mode flag (`ai_mode`), it either waits for interactive user input or runs the AI.

2. **AI Move Calculation (AI.py):**  
   - The AI preloads the next 10 pieces.
   - `get_next_moves` is invoked, which internally calls:
     - `backtracking_search`, which recursively:
       - Uses `get_legal_placements` to list all possible moves for the current piece.
       - For each move, `simulate_placement` creates a deep copy of the game state.
       - When the search reaches a depth of 10 moves, `evaluate_state` is used to assign a score to the board.
   - The best sequence of moves is selected based on the evaluation scores.

3. **Applying the AI Moves (Tetris.py):**  
   - The chosen move sequence is applied one move at a time using `apply_placement`, which sets the piece’s rotation, position, and instantly drops it.
   - The modified `freeze` function finalizes the placement without delays.

4. **Game Update and Rendering:**  
   - The game board is updated to reflect the new state after each move.
   - The updated state is rendered to show the final placements for each AI decision.

5. **Loop:**  
   - The AI is repeatedly invoked as long as the game is active, continually processing the next set of 10 pieces until the game is over.
   - We can maybe have the user hit space to proceed onto the next AI generated moves or just exit

TODO: 
#1 Run 100 simulations and store their scores in a csv. - Pierce TODO
#2 Get stats like average, median, range, etc. Look into alpha beta pruning.
#3 Implement other heuristics/Monte Carlo
#4 Look into basic DQN approach for comparison.

Project Proposal Feedback
"The idea is solid to me, but you did mention that there are existing approaches using DQN to solve this task. I think it would be a good idea to benchmark your approach against the DQN approach to understand which approach obtains a higher score and why. Your backtracking algorithm idea sounds good, but you could also try some of the methods explored in this class, like MCTS. This will help you establish more interesting benchmarks beyond just the random placement model (which should definitely perform worse than your algorithm)."
from tetris import Tetris, Figure
from typing import List, Tuple

def get_legal_placements(tetris: Tetris, piece: Figure) -> List[Tuple[int, int]]:
    """
    Check design doc for details
    """
    # TODO: Implement
    legal = []
    original_figure = tetris.figure
    num_rotations = len(piece.figures[piece.type])

    for rotation in range(num_rotations):
        temp_figure = Figure(0, 0)
        temp_figure.type = piece.type
        temp_figure.rotation = rotation
        temp_figure.color = piece.color

        min_x = min([j for i in range(4) for j in range(4) if i*4 + j in temp_figure.image()])
        max_x = max([j for i in range(4) for j in range(4) if i*4 + j in temp_figure.image()])

        min_allowed_x = -min_x
        max_allowed_x = tetris.width - max_x - 1

        for x in range(min_allowed_x, max_allowed_x + 1):
            temp_figure.x = x
            tetris.figure = temp_figure
            if not tetris.intersects():
                legal.append((rotation, x))

    tetris.figure = original_figure
    return legal


def simulate_placement(tetris: Tetris, piece: Figure, rotation: int, x: int) -> Tetris:
    """
    Check design doc for details
    """
    # TODO: Implement
    new_tetris = Tetris(tetris.height, tetris.width)
    new_tetris.ai_mode = True
    new_tetris.level = tetris.level
    new_tetris.score = tetris.score
    new_tetris.state = tetris.state
    new_tetris.field = [row.copy() for row in tetris.field]
    new_tetris.x = tetris.x
    new_tetris.y = tetris.y
    new_tetris.zoom = tetris.zoom

    new_figure = Figure(x, 0)
    new_figure.type = piece.type
    new_figure.rotation = rotation
    new_figure.color = piece.color
    new_tetris.figure = new_figure

    if new_tetris.intersects():
        return new_tetris

    while not new_tetris.intersects():
        new_tetris.figure.y += 1
    new_tetris.figure.y -= 1

    new_tetris.freeze()
    return new_tetris

def evaluate_state(tetris: Tetris) -> float:
    """
    Check design doc for details
    """
    # TODO: Implement
    aggregate_height = 0
    for col in range(tetris.width):
        for row in range(tetris.height):
            if tetris.field[row][col] != 0:
                aggregate_height += tetris.height - row
                break

    holes = 0
    for col in range(tetris.width):
        found = False
        for row in range(tetris.height):
            if tetris.field[row][col] != 0:
                found = True
            elif found:
                holes += 1

    bumpiness = 0
    prev_height = 0
    for col in range(tetris.width):
        height = 0
        for row in range(tetris.height):
            if tetris.field[row][col] != 0:
                height = tetris.height - row
                break
        if col > 0:
            bumpiness += abs(height - prev_height)
        prev_height = height

    return tetris.score * 100 - aggregate_height * 10 - holes * 50 - bumpiness * 5

def backtracking_search(tetris: Tetris, pieces: List[Figure], depth: int) -> Tuple[List[Tuple[int, int]], float]:
    """
    Check design doc for details
    """
    #if depth is 0 or no pieces are left, return the current board status
    if depth == 0 or not pieces:
        return [], evaluate_state(tetris)
    
    best_sequence: List[Tuple[int, int]] = []
    best_score = float('-inf')
    
    #start at the first piece
    current_piece = pieces[0]
    legal_moves = get_legal_placements(tetris, current_piece)
    
    #for every legal move recursively take them
    for move in legal_moves:
        rotation, x = move
        #simulate the move then recurse
        new_state = simulate_placement(tetris, current_piece, rotation, x)
        subsequent_moves, score = backtracking_search(new_state, pieces[1:], depth - 1)
        #update best score and move accordingly
        if score > best_score:
            best_score = score
            best_sequence = [move] + subsequent_moves
    
    return best_sequence, best_score

def backtracking_search_ab(tetris: Tetris, pieces: List[Figure], depth: int, alpha: float = float('-inf'), beta: float = float('inf')) -> Tuple[List[Tuple[int, int]], float]:
    """
    Backtracking search with basic alpha beta pruning
    """
    if depth == 0 or not pieces:
        return [], evaluate_state(tetris)
    
    best_sequence: List[Tuple[int, int]] = []
    best_score = float('-inf')
    
    current_piece = pieces[0]
    legal_moves = get_legal_placements(tetris, current_piece)
    
    ordered_moves = []
    for move in legal_moves:
        rotation, x = move
        simulated_state = simulate_placement(tetris, current_piece, rotation, x)
        heuristic = evaluate_state(simulated_state)
        ordered_moves.append((move, simulated_state, heuristic))
    #sort moves so that the ones w/ the highest score are explored first
    ordered_moves.sort(key=lambda tup: tup[2], reverse=True)
    
    for move, sim_state, _ in ordered_moves:
        subsequent_moves, score = backtracking_search_ab(sim_state, pieces[1:], depth - 1, alpha, beta)
        if score > best_score:
            best_score = score
            best_sequence = [move] + subsequent_moves
        alpha = max(alpha, best_score)
        if beta <= alpha:
            break  # beta cutoff
    
    return best_sequence, best_score

def get_next_moves(tetris: Tetris, pieces: List[Figure]) -> List[Tuple[int, int]]:
    """
    Check design doc for details
    """
    # return [(0, 3)] * 10 # dummy data
    #generate our next 10 moves using backtracking
    depth = min(3, len(pieces)) #Note: depth must be the same as self.n in tetris.py otherwise it will crash
    moves, _ = backtracking_search_ab(tetris, pieces, depth)
    #this will return to tetris.py
    return moves
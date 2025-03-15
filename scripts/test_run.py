from tetris import *
from AI import *

done = False
fps = 25
game = Tetris(20, 10)
counter = 0

pressing_down = False

while not done:
    if game.figure is None:
        game.new_figure()

    if not game.state == "gameover":
        # Set figure as first figure
        game.figure = game.next_n_figures[0]
        # Get best placement
        moves = get_next_moves(game, game.next_n_figures)
        print("Moves: ", moves)

        for move in moves:
            # Check if exit game within the smallest loop so we don't get spinny cursor in pygame
            if not game.apply_placement(move[0], move[1]):
                # Placement failed, game over
                done = True
                break
    
print(game.score)
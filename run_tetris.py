from tetris import *
from AI import *
import argparse
import pygame
import torch

def draw_entire_game(game: Tetris):
    screen.fill(BLACK)

    # Draw game state
    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
            if game.field[i][j] > 0:
                pygame.draw.rect(screen, colors[game.field[i][j]],
                                 [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])

    # Draw current figure
    if game.figure is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.figure.image():
                    pygame.draw.rect(screen, colors[game.figure.color],
                                     [game.x + game.zoom * (j + game.figure.x) + 1,
                                      game.y + game.zoom * (i + game.figure.y) + 1,
                                      game.zoom - 2, game.zoom - 2])

    font = pygame.font.SysFont('Calibri', 25, True, False)
    font1 = pygame.font.SysFont('Calibri', 65, True, False)
    text = font.render("Score: " + str(game.score), True, WHITE)
    text_game_over = font1.render("Game Over", True, (255, 125, 0))
    text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))

    screen.blit(text, [0, 0])
    if game.state == "gameover":
        screen.blit(text_game_over, [20, 200])
        screen.blit(text_game_over1, [25, 265])

    pygame.display.flip()


# Initialize the game engine
pygame.init()

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

size = (400, 500)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Tetris")

# Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()
fps = 25
game = Tetris(20, 10)
counter = 0

pressing_down = False

# Argument parsing
parser = argparse.ArgumentParser(description='Tetris Solver')
parser.add_argument('-backtracking', action='store_true', help='Enable backtracking')
args = parser.parse_args()
print("backtracking: ",args.backtracking)

if game.figure is None:
    game.new_figure()

while not done:
    # Check if exit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    if args.backtracking: # Using backtracking
        if not game.state == "gameover":
            # Set figure as first figure
            game.figure = game.next_n_figures[0]
            # Get best placement
            moves = get_next_moves(game, game.next_n_figures)
            print("Moves: ", moves)

            for move in moves:
                # Check if exit game within the smallest loop so we don't get spinny cursor in pygame
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True
                if not game.apply_placement(move[0], move[1]):
                    # Placement failed, game over
                    break
                draw_entire_game(game)
                time.sleep(1)
    else: # Normal game with manual input
        counter += 1
        if counter > 100000:
            counter = 0

        if counter % (fps // game.level // 2) == 0 or pressing_down:
            if game.state == "start":
                game.go_down()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.rotate()
                    pressing_down = False
                if event.key == pygame.K_DOWN:
                    pressing_down = True
                if event.key == pygame.K_LEFT:
                    game.go_side(-1)
                    pressing_down = False
                if event.key == pygame.K_RIGHT:
                    game.go_side(1)
                    pressing_down = False
                if event.key == pygame.K_SPACE:
                    game.go_space()
                    pressing_down = False
                if event.key == pygame.K_ESCAPE:
                    game.__init__(20, 10)

        if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    pressing_down = False

    draw_entire_game(game)
    clock.tick(fps)

pygame.quit()
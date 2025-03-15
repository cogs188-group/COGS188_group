import csv
import argparse
import time
from tetris import Tetris, Figure
from AI import get_next_moves

def run_game(watch=False, step=False, max_moves=None):
    """
    Run a single game of Tetris with the AI.
    
    If watch is True, display the game using pygame.
    If step is True, wait for a user keypress before applying each move.
    If max_moves is specified, stop the game after that many moves.
    
    ex: python run_multiple_tetris.py -watch -step -max_moves 150  (watch each game step by step)
        python run_multiple_tetris.py -max_moves 150               (run via command line (recommended))

    Returns:
        tuple: (final_score, move_count) where move_count is the number of moves applied.
    """
    move_count = 0
    if watch:
        import pygame
        pygame.init()
        size = (400, 500)
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption("AI Tetris Watch Mode")
        clock = pygame.time.Clock()

        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GRAY = (128, 128, 128)
        colors = [
            (0, 0, 0),
            (120, 37, 179),
            (100, 179, 179),
            (80, 34, 22),
            (80, 134, 22),
            (180, 34, 22),
            (180, 34, 122),
        ]

        def draw_entire_game(game):
            screen.fill(BLACK)
            for i in range(game.height):
                for j in range(game.width):
                    pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j,
                                                      game.y + game.zoom * i,
                                                      game.zoom, game.zoom], 1)
                    if game.field[i][j] > 0:
                        pygame.draw.rect(screen, colors[game.field[i][j]],
                                         [game.x + game.zoom * j + 1,
                                          game.y + game.zoom * i + 1,
                                          game.zoom - 2, game.zoom - 1])
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

        game = Tetris(20, 10)
        while game.state != "gameover" and (max_moves is None or move_count < max_moves):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.state = "gameover"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game.state = "gameover"
            if game.figure is None:
                game.new_figure()
            game.figure = game.next_n_figures[0]
            moves = get_next_moves(game, game.next_n_figures)
            if not moves:
                break
            print("Moves:", moves)
            print("Score:", game.score)
            for move in moves:
                if max_moves is not None and move_count >= max_moves:
                    break
                if step:
                    waiting = True
                    print("Press any key to place the next move...")
                    while waiting:
                        event = pygame.event.wait()
                        if event.type == pygame.KEYDOWN:
                            waiting = False
                rotation, x = move
                if not game.apply_placement(rotation, x):
                    break
                move_count += 1
                draw_entire_game(game)
                #wait so its easier to watch
                clock.tick(10)
            draw_entire_game(game)
        final_score = game.score
        pygame.quit()
        return final_score, move_count

    else:
        #cli tetris game
        game = Tetris(20, 10)
        while game.state != "gameover" and (max_moves is None or move_count < max_moves):
            if game.figure is None:
                game.new_figure()
            game.figure = game.next_n_figures[0]
            moves = get_next_moves(game, game.next_n_figures)
            if not moves:
                break
            print("Moves:", moves)
            print("Score:", game.score)
            for move in moves:
                if max_moves is not None and move_count >= max_moves:
                    break
                if step:
                    input("Press Enter to apply the next move...")
                rotation, x = move
                if not game.apply_placement(rotation, x):
                    break
                move_count += 1
        return game.score, move_count

def main():
    parser = argparse.ArgumentParser(description="AI Tetris Simulation")
    parser.add_argument('-watch', action='store_true',
                        help='Display the game visually using pygame (runs one game in watch mode)')
    parser.add_argument('-step', action='store_true',
                        help='Wait for a keypress before placing each move')
    parser.add_argument('-num_games', type=int, default=100,
                        help='Total number of games to simulate (if watch mode is enabled, one game will be visual and the remainder headless)')
    parser.add_argument('-max_moves', type=int, default=None,
                        help='Maximum number of moves per game (if reached, the game stops and the score is recorded)')
    args = parser.parse_args()

    scores = []
    moves_list = []
    num_games = args.num_games

    if args.watch:
        print("Running one game in watch mode...")
        score, moves = run_game(watch=True, step=args.step, max_moves=args.max_moves)
        scores.append(score)
        moves_list.append(moves)
        remaining_games = num_games - 1
        print(f"Running remaining {remaining_games} games in headless mode...")
        for _ in range(remaining_games):
            score, moves = run_game(watch=False, step=args.step, max_moves=args.max_moves)
            scores.append(score)
            moves_list.append(moves)
    else:
        for i in range(num_games):
            score, moves = run_game(watch=False, step=args.step, max_moves=args.max_moves)
            scores.append(score)
            moves_list.append(moves)

    #save scores to csv
    with open("tetris_scores.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Game", "Max Score", "Moves"])
        for idx, (score, moves) in enumerate(zip(scores, moves_list), start=1):
            writer.writerow([idx, score, moves])

if __name__ == "__main__":
    main()

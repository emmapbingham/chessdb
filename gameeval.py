# Evaluate all the moves of a chess game from a PGN file using Stockfish engine
# Requires Python Chess library and requires that you put the path to your Stockfish engine
# NOTE: often chess databases, including lichess, report centipawn scores as divided by 100,
#    so then it would be e.g. +1.38 rather than +138
# This script currently reports as +138
# By Emma Bingham
# Feb 2025

import sqlite3
import io
import chess
import chess.pgn
import chess.engine


# Open a connection to the sqlite db
conn = conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# Select a game to look at
query = "SELECT * FROM games"
res = cursor.execute(query)
game_text = res.fetchall()[0]

# Print the moves
print("Moves: ", game_text[-1])
print("-----------")

# Read game pgn string into python-chess library
pgn = io.StringIO(game_text[-1])
game = chess.pgn.read_game(pgn)

# Make evaluations of position using stockfish
# Path to stockfish engine
engine = chess.engine.SimpleEngine.popen_uci("/usr/local/Cellar/stockfish/17/bin/stockfish")

# Make board
board = chess.Board()
# Make updated pgn game we will write stockfish evals to
updated_game = chess.pgn.Game()
for i, move in enumerate(game.mainline_moves()): 
    # Push current move to board
    board.push(move)
    # Analyze current board position
    info = engine.analyse(board, chess.engine.Limit(time=0.1)) # can also do chess.engine.Limit(depth=20)
    # print(str(move))
    # print("Score:", info["score"].white()) # from White's POV
    # print("--")

    # Write evaluations into the updated PGN game text
    if i == 0:
        node = updated_game.add_variation(move)
    else:
        node = node.add_variation(move)
    node.comment = f"[%eval {str(info['score'].white())}]"

# Print updated PGN with eval scores
print("Moves with eval: ", updated_game.variations[0])

engine.quit()

# Save new PGN text to database? Not sure if we really want to do this.
# TODO

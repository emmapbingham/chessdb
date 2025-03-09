# Evaluate all the moves of a chess game from a PGN file using Stockfish engine
# Requires Python Chess library and requires that you put the path to your Stockfish engine
# NOTE: often chess databases, including lichess, report centipawn scores as divided by 100,
#    so then it would be e.g. +1.38 rather than +138
# This script currently reports as +138
# By Emma Bingham
# Feb 2025

import chess
import numpy as np


def gameeval(game, engine, depth=10):
    """
    Calculate evaluations for each move in the mainline game.
    engine: the engine we are using for calculation
    game: the chess game object from python-chess library
    depth = default 10 # depth parameter for stockfish engine

    Returns: two lists of evals as centipawns, (win, draw, loss) for each move.
    Note that scores are all from white's perspective.
    """

    centipawns = []
    wdls = []
    for i, mainline_node in enumerate(game.mainline()):
        if mainline_node.is_end(): # break if it's the ending node
            break
        if i == 0: # analyze using empty board if it's the starting node
            analysis = engine.analyse(chess.Board(), chess.engine.Limit(depth=depth), root_moves=[mainline_node.move])
        else: # analyze the next move with the current board
            analysis = engine.analyse(mainline_node.board(), chess.engine.Limit(depth=depth), root_moves=[mainline_node[0].move])
        score = analysis["score"].white()
        centipawns.append(score.score(mate_score=100000))
        wdls.append(tuple(score.wdl()))

    return np.asarray(centipawns), np.asarray(wdls)


def landscapeeval(game, engine, k=3, d=2, depth=10):
    """
    Calculate tree of moves and their evaluations for each move in the mainline game.
    engine: the engine we are using for calculation
    game: the chess game object from python-chess library
    params:
    k = 3 # number of branches off each node
    d = 2 # depth of tree
    depth = 10 # depth parameter for stockfish engine

    Returns: list of (nodes, edges) of tree for each mainline move.
    Note that scores are all from white's perspective.

    Also note that the total tree size is sum(k**i) from 0 to d
    and the number of leaf nodes is k**d
    """
    
    landscape = [] # consists of list of tuples of (nodes, edges) for each mainline move
    for mainline_node in game.mainline():
        if mainline_node.is_end(): # if it's the last move, we don't need to keep going with the loop
            break

        # for our altnerate data structure (outside of the python-chess game tree structure)
        nodes = [] # (number, fen, eval)
        edges = [] # e.g. (0, 1)
        counter = 0 # for counting nodes to label them
        # append the current node to our data structure (has format node number, fen, depth, centipawn score, wdl score)
        nodes.append((counter, mainline_node.board().fen(), 0, np.nan, np.nan)) 

        # initialize the list of nodes to visit for our search
        nodes_to_visit = []
        nodes_to_visit.append((mainline_node, 0, 0)) # append the current node (node, depth, number)

        # search loop
        while nodes_to_visit:
            current_node, current_depth, current_num = nodes_to_visit.pop() # pop off the last node 
            if current_depth == d: # if we've reached the depth d with this node, we don't need to do anything else with it
                continue
            # analyze the current node to get up to k best move options
            analysis = engine.analyse(current_node.board(), chess.engine.Limit(depth=depth), multipv=k)
            for pv in analysis: # iterate through each move found
                if "pv" not in pv.keys(): # if the board state is a mate, we will not have any move options
                    break
                counter += 1 # increase the counter so we can give the proper numeric label to this new node
                move = pv["pv"][0] # get what this move is
                score = pv["score"].white() # get its score
                current_node.add_variation(move, comment=f"[%eval {str(score)}]") # add it as a variation to this current node
                nodes_to_visit.append((current_node[-1], current_depth+1, counter)) # add the most recently added variation to the nodes to visit

                # Add the nodes and edges to the alternate data structure here
                nodes.append((
                        counter, 
                        str(current_node[-1].board().fen()), 
                        current_depth + 1,
                        score.score(mate_score=100000),
                        tuple(score.wdl())
                            )) 
                edges.append((current_num, counter))

        landscape.append((nodes, edges))
    return landscape

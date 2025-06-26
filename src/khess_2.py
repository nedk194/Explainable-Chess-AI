#!env pypy3

import time
from collections import namedtuple
import logging
import sys
import os
import chess
from square_weights import square_weights_white, square_weights_black
from tools import EagerStream

import evaluation

# from khess_minimax import minimax

PIECE_VAL = {chess.PAWN: 100, chess.KNIGHT: 280, chess.BISHOP: 320,
             chess.ROOK: 479, chess.QUEEN: 929, chess.KING: 1000000}

SCORE_MATE = 1000000
INF = 1000000000
AB_TRUNCATE = True  # Use alpha-beta pruning
AB_TRUNCATE_LEAVES = False  # Use alpha-beta pruning on leaves
ORDER_MOVES = True  # Use move ordering heuristic
ORDER_CAPTURE = -1000000
# ORDER_ATTACKERS = False
# ORDER_MVVLVA = False

VERBOSE = True
nodes = 0

board = chess.Board()

evaluated_move = namedtuple('move', ('move', 'score', 'order_value'))


logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), 'khess.log'), level=logging.DEBUG)
out = EagerStream(sys.stdout)


def output(line):
    print(line, file=out)
    logging.debug(line)


def print_board(board):
    # print(board.unicode(invert_color=True, empty_square=' ')) # Nicer for unicode terminals
    print(board)
    print()


# @profile
def eval_move(board, move, sw, sw_enemy, neg):
    order_value = 0 # ned - what does order value represent?
    piece = board.piece_type_at(move.from_square)

    # Positional score
    score = sw[piece][move.to_square] - sw[piece][move.from_square]

    # Capture
    if board.is_capture(move):
        order_value = ORDER_CAPTURE
        piece_victim = board.piece_type_at(move.to_square)
        if piece_victim is not None:
            # Ordinary capture
            score += PIECE_VAL[piece_victim] + sw_enemy[piece_victim][move.to_square]
            # if ORDER_ATTACKERS:
                # order_value -= PIECE_VAL[piece_victim] - PIECE_VAL[piece]
            # if ORDER_MVVLVA:
            order_value -= 1000 * PIECE_VAL[piece_victim] - PIECE_VAL[piece]
        else:
            # En passant?
            victim_square = move.to_square + (-8 if board.turn == chess.WHITE else 8)
            score += PIECE_VAL[chess.PAWN] + sw_enemy[chess.PAWN][victim_square]

    if piece == chess.QUEEN:
        score -= 10  # Penalty for moving the queen
    order_value -= score
    print("kiril: " + str(score*neg))
    return evaluated_move(move, score * neg, order_value)

def eval_board(board):
    score_order_tuple = evaluation.evaluate_agressive(board)
    return score_order_tuple


def minimax_ab(board, depth, max_depth, alpha, beta, side_is_white):
    global nodes  # Track the number of nodes evaluated

    # Scoring depends on whose side we are thinking for
    neg = 1 if side_is_white else -1  # Needed for checkmate evaluation

    # Check if the king is missing (checkmate detected)
    king_mask = board.occupied_co[side_is_white] & board.kings
    if not king_mask:
        return -SCORE_MATE * neg

    # Keep track of the best score and move
    best_move = None
    best_score = None

    # Base case: Max depth reached or no legal moves
    if depth >= max_depth or board.is_game_over():
        nodes += 1
        ###################
        start_time = time.time()
        out = eval_board(board)
        end_time = time.time()
        print(f"eval took {end_time - start_time:.5f} seconds - ned")
        ####################
        return out, None  # Full board evaluation
        


    eval_moves = list(board.legal_moves)  # Get all legal moves

    if ORDER_MOVES:  # Move ordering, need to add this
        print("order moves")
        #eval_moves = order_moves(board, eval_moves)  # Sort moves using heuristic

    # explaore moves
    for move in eval_moves:
        board.push(move)  # Make tentative move
        nodes += 1

        # Evaluate the resulting position
        score, _ = minimax_ab(board, depth + 1, max_depth, alpha, beta, not side_is_white)
        board.pop()  # Undo the move

        # track Best Move & Score
        if best_score is None or (side_is_white and score > best_score) or (not side_is_white and score < best_score):
            best_score = score
            best_move = move  # Store best move

        # Alpha-Beta Pruning
        if AB_TRUNCATE:
            if side_is_white:
                if best_score >= beta:
                    break  # Beta cutoff
                alpha = max(alpha, best_score)
            else:
                if best_score <= alpha:
                    break  # Alpha cutoff
                beta = min(beta, best_score)

        # Debug output
        if depth == 0 and VERBOSE:
            output(f'info {move} {score} {best_score}')

    return (best_score, best_move) if depth == 0 else (best_score, None)


def find_best_move(board, depth, color):
    global nodes
    nodes = 0
    t = time.time()
    best_score, best_move = minimax_ab(board, 0, depth, -INF, INF, color)

    dt = time.time() - t
    print(f'Nodes: {nodes}, time: {dt:.2f} sec, nodes/sec: {nodes / dt:.2f}')
    # output(f'info Nodes: {nodes}, time: {dt:.2f} sec, nodes/sec: {nodes / dt:.2f}')
    return best_score, best_move


def main():
    global nodes
    stack = []
    # Interaction with GUI is stolen from sunfish
    while True:
        if stack:
            smove = stack.pop()
        else:
            smove = input()

        logging.debug(f'>>> {smove} ')

        if smove == 'quit':
            break

        elif smove == 'uci':
            output('id name Khess')
            output('id author Kirill Sidorov')
            output('uciok')

        elif smove == 'isready':
            output('readyok')

        elif smove == 'ucinewgame':
            stack.append('position fen ' + chess.STARTING_FEN)

        elif smove.startswith('position'):
            params = smove.split(' ')
            idx = smove.find('moves')

            if idx >= 0:
                moveslist = smove[idx:].split()[1:]
            else:
                moveslist = []

            if params[1] == 'fen':
                if idx >= 0:
                    fenpart = smove[:idx]
                else:
                    fenpart = smove

                _, _, fen = fenpart.split(' ', 2)

            elif params[1] == 'startpos':
                fen = chess.STARTING_FEN

            else:
                pass

            board.set_fen(fen)
            color = chess.WHITE if fen.split()[1] == 'w' else chess.BLACK

            for move in moveslist:
                board.push_san(move)

        elif smove.startswith('go'):
            depth = 7

            _, *params = smove.split(' ')  # Take remaining arguments without "go"
            for param, val in zip(*2*(iter(params),)):  # Iterate over parameter/value pairs
                if param == 'depth':
                    depth = int(val)

            logging.debug(f'Starting search. Color: {color}, depth: {depth}')

            # Find best move
            best_score, best_move = find_best_move(board, depth, board.turn, True)

            # Send best move to engine
            output('bestmove ' + str(best_move))

        else:
            pass



def test_move():
    global nodes, AB_TRUNCATE, ORDER_MOVES, ORDER_ATTACKERS, ORDER_MVVLVA, VERBOSE
    # board.set_fen(chess.STARTING_FEN)
    board.set_fen('1K3RQ1/ppn3p1/r3N1pq/2pN4/2b1kPB1/b5r1/8/2BR4 w - - 0 1')

    depth = 2
    # nodes = 0
    # best_score, best_move = find_best_move(board, depth, board.turn, ab=False)
    # print('Best move', best_move, best_score)

    VERBOSE = False
    # AB_TRUNCATE = False
    # best_score, best_move = find_best_move(board, depth, board.turn)
    # print('Best move no alpha-beta            ', best_move, best_score)

    AB_TRUNCATE = False
    # ORDER_MOVES = False
    # best_score, best_move = find_best_move(board, depth, board.turn)
    # print('Best move alpha-beta, no ordering  ', best_move, best_score)
    ORDER_MOVES = False
    best_score, best_move = find_best_move(board, depth, board.turn)
    print('Best move alpha-beta, with ordering', best_move, best_score)

def self_play():
    global nodes, ORDER_MOVES, ORDER_ATTACKERS, ORDER_MVVLVA, VERBOSE
    VERBOSE = False
    board.set_fen(chess.STARTING_FEN)
    # board.set_fen('3r1rk1/p4ppp/2Q5/NB1p1b2/8/2P1B3/P5q1/RK2R3 w - - 2 22')
    # board.push_san('e2e4')

    depth = 7
    while True:
        # best_score, best_move = find_best_move(board, depth, board.turn, ab=False)
        # print('Best move naive     ', best_move, best_score)
        # print_board(board)
        # print(board.turn)
        # ORDER_MOVES = False
        # best_score, best_move = find_best_move(board, depth, board.turn)
        # print('Best move alpha-beta, no ordering            ', best_move, best_score)

        ORDER_MOVES = True
        best_score, best_move = find_best_move(board, depth, board.turn)
        print('Best move alpha-beta, with ordering          ', best_move, best_score)
        print()
        # best_score, best_move = khess_minimax.minimax(board, 0, depth, board.turn)
        # print('Best move original    ', best_move, best_score)

        # if best_move_order != best_move or best_score_order != best_score:
            # print('ERROR')
            # print(board.fen)
            # break
        board.push(best_move)
        if board.is_checkmate():
            break
    

if __name__ == '__main__':
    main()
    # test_move()
    # self_play()

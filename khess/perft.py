import chess
from khess_tools import Board
from tools import WHITE, BLACK
from time import time

# @profile
def perft(board, depth, side):
    nodes = 0
    moves = board.moves(side)
    if depth == 1:
        return len(moves)

    for move in moves:
        board.play(side, move)
        nodes += perft(board, depth - 1, not side)
        board.pop(side, move)

    return nodes


def main():
    board = Board()
    board.set_fen(chess.STARTING_FEN)

    t = time()
    nodes = perft(board, 6, WHITE)
    dt = time() - t
    print('Nodes:', nodes, 'time:', dt, 'nodes/second:', nodes / dt)


if __name__ == '__main__':
    main()

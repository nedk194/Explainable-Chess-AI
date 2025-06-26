#!env python3

from square_weights import square_weights_black, square_weights_white
import chess

def write_pst(file, piece_idx, pst, neg):
    # print(piece_idx, pst)
    file.write('{')
    file.write(','.join([str(x * neg) for x in pst]))
    file.write('}')

ZEROS = tuple([0] * 64)
with open('khess_tools/pst.h', 'w+') as file:
    file.write('const int PST[][NSQUARES] = {\n')
    for idx, piece_type in enumerate([chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING, None, None, chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING, None]):
        white = idx <= 5
        # print(idx, piece_type, white)
        if piece_type is not None:
            if white:
                pst = square_weights_white[piece_type]
            else:
                pst = square_weights_black[piece_type]
        else:
            pst = ZEROS
        write_pst(file, idx, pst, 1 if white else -1)
        if idx < 14:
            file.write(',\n')
        else:
            file.write('};')

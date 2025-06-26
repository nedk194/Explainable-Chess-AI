import logging
import os
import sys
import move_flags as flags


WHITE = 0
BLACK = 1
RANK_NAMES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
FILE_NAMES = ['1', '2', '3', '4', '5', '6', '7', '8']
ORDA = ord('a')
ORD1 = ord('1')

# Piece types
WHITE_PAWN = 0
BLACK_PAWN = 8
NO_PIECE = 14

SQUARE_NAMES = [
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8"]


def bitboard_to_str(bb):
    binary = format(bb, '064b')
    idx = 0
    result = ''
    for row in range(8):
        row = ''
        for col in range(8):
            row = ('#' if binary[idx] == '1' else '.') + '  ' + row
            idx += 1
        result += row + '\n'

    return result

# Extremely naughty!
# old_print = print
# def print(*args, **kwargs):
#     # Print to stderr and flush immediately
#     old_print(*args, file=sys.stderr, **kwargs)
#     sys.stderr.flush()

def log(*args, **kwargs):
    # Print to stderr and flush immediately
    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()


INTERACTIVE = False
if sys.stdin and sys.stdin.isatty():
    INTERACTIVE = True

class EagerStream():
    '''A thin wrapper around I/O stream that immediately flushes the output.'''
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
        # if not INTERACTIVE:
        # sys.stderr.write(data)
        # sys.stderr.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), 'khess.log'), level=logging.DEBUG)
out = EagerStream(sys.stdout)

#def initalise_gui(fen):



def output(line):
    print(line, file=out)
    logging.debug(line)
    out.flush()


def move_from(move):
    return (move >> 6) & 0x3f


def move_to(move):
    return move & 0x3f


def square_to_str(square):
    return RANK_NAMES[square & 7] + FILE_NAMES[(square >> 3) & 7]


def move_flags(move):
    return (move >> 12) & 0xf


def move_to_alg(move):
    '''16-bit move representation to algebraic notation with promotion.'''
    fr = move_from(move)
    to = move_to(move)
    move_str = square_to_str(fr) + square_to_str(to)

    flag = move_flags(move)

    if flag == flags.PR_QUEEN:
        move_str += 'q'
    elif flag == flags.PR_ROOK:
        move_str += 'r'
    elif flag == flags.PR_BISHOP:
        move_str += 'b'
    elif flag == flags.PR_KNIGHT:
        move_str += 'n'

    return move_str

'''
def alg_to_move(alg, board): old method
    

    fr = SQUARE_NAMES.index(alg[0:2])
    to = SQUARE_NAMES.index(alg[2:4])
    
    if len(alg) == 5:
        print("---------------------")
        print(alg)
        print("--------------------")
        promo = alg[4]
        if promo == 'q':
            return flags.PR_QUEEN << 12 | fr << 6 | to
        elif promo == 'r':
            return flags.PR_ROOK << 12 | fr << 6 | to
        elif promo == 'b':
            return flags.PR_BISHOP << 12 | fr << 6 | to
        elif promo == 'n':
            return flags.PR_KNIGHT << 12 | fr << 6 | to

    # We need to add castling flags when necessary and the target square is the rook's square
    if alg == 'e1g1':
        return flags.OO << 12 | 263
    if alg == 'e8g8':
        return flags.OO << 12 | 3903
    if alg == 'e1c1':
        return flags.OOO << 12 | 256
    if alg == 'e8c8':
        return flags.OOO << 12 | 3896

    # fr = ((ord(alg[1]) - ORD1) << 9) | ((ord(alg[0]) - ORDA) << 6)
    # to = ((ord(alg[3]) - ORD1) << 3) | (ord(alg[2]) - ORDA)
    
    # print('fr', fr, 'to', to)

    # Capture?
    victim = board.at(to)
    if victim != NO_PIECE:
        return flags.CAPTURE << 12 | fr << 6 | to

    # Double push?
    piece = board.at(fr)
    # print('piece', piece)
    if (piece == WHITE_PAWN or piece == BLACK_PAWN) and (abs(fr - to) == 16):
        return flags.DOUBLE_PUSH << 12 | fr << 6 | to

    

    # Ordinary quiet move
    return fr << 6 | to
'''

def alg_to_move(alg, board):
    output("tools i sworking")
    '''Convert algebraic string (e.g., e2e4 or e7e8q) to 16-bit move representation with appropriate flags.'''

    fr = SQUARE_NAMES.index(alg[0:2])
    to = SQUARE_NAMES.index(alg[2:4])

    output("in alg_to_move: alg = {alg} from = {fr} to = {to}")

    # Castling moves
    if alg == 'e1g1':
        return flags.OO << 12 | (4 << 6) | 6  # e1 to g1
    if alg == 'e8g8':
        return flags.OO << 12 | (60 << 6) | 62  # e8 to g8
    if alg == 'e1c1':
        return flags.OOO << 12 | (4 << 6) | 2  # e1 to c1
    if alg == 'e8c8':
        return flags.OOO << 12 | (60 << 6) | 58  # e8 to c8

    # Promotions (e.g., e7e8q)
    if len(alg) == 5:
        promo = alg[4].lower()
        promo_flags = {
            'q': flags.PR_QUEEN,
            'r': flags.PR_ROOK,
            'b': flags.PR_BISHOP,
            'n': flags.PR_KNIGHT,
        }
        if promo in promo_flags:
            return promo_flags[promo] << 12 | fr << 6 | to

    piece = board.at(fr)
    victim = board.at(to)

    # Capture
    if victim != NO_PIECE:
        return flags.CAPTURE << 12 | fr << 6 | to

    # Double pawn push
    if (piece == WHITE_PAWN or piece == BLACK_PAWN) and abs(fr - to) == 16:
        return flags.DOUBLE_PUSH << 12 | fr << 6 | to

    # Quiet move
    return fr << 6 | to

def is_capture(move):
    return move & 0x8000

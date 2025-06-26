import sys
import chess
from surge_player import surgePlayer
import platform


player = surgePlayer("Surge", chess.WHITE, None, depth=3)
board = chess.Board()

def main(args):
    ''' interacts with the engine in proper chess UCI '''
    while True:
        line = sys.stdin.readline().strip()
        if line == "uci":
            print("id name SurgeEngine")
            print("id author Ned Kingdon")
            print("uciok")
        elif line == "isready":
            print("readyok")
        elif line.startswith("position"):
            tokens = line.split()
            if "startpos" in tokens:
                board.set_fen(chess.STARTING_FEN)
                if "moves" in tokens:
                    move_idx = tokens.index("moves") + 1
                    for m in tokens[move_idx:]:
                        board.push_uci(m)
            elif "fen" in tokens:
                fen = " ".join(tokens[1 + tokens.index("fen"):])
                board.set_fen(fen)
        elif line.startswith("go"):
            move, _ = player.get_move(board, args, explain=False)
            print(f"bestmove {move.uci()}")
        elif line == "quit":
            player.close()
            break

if __name__ == "__main__":
    ''' handles input string imeadiatly after command - not as parameter with command '''
    config_string = sys.stdin.readline().strip()
    args = list(map(int, config_string.split(",")))
    player.depth = int(args[0])
    main(args[1:])

import chess
import chess.engine
import time
import sys

from player import Player

STOCKFISH_PATH = r"C:\Users\Ned\Documents\Year-3\FinalProject\stockfish\stockfish-windows-x86-64-avx2.exe"


class Stockfish(Player):
    def __init__(self, name, color, gui, depth):
        self.name = name
        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        self.depth = depth
        self.human = False
        self.next_moves = []

    def get_move(self, board, explain=False):
        """use Stockfish to find the best move."""

        result = self.engine.play(board, chess.engine.Limit(depth=self.depth)) 
        # no explanation provided for stockfish
        move = result.move, None
        self.next_moves.append(move)

        return (move)  
    
    def get_top_moves(self, board, num_moves, depth):
        """Returns a list of the best moves in UCI format """
        info = self.engine.analyse(board, chess.engine.Limit(depth=depth), multipv=num_moves)

        # Extract only the move in UCI format from each analysis entry
        best_moves = [entry["pv"][0].uci() for entry in info if "pv" in entry]
        self.engine.quit()
        return best_moves
    
    def reset(self):
        self.next_moves = []

    def close(self):
        self.engine.close()


if __name__ == "__main__":
    depth = int(sys.stdin.readline())
    player = Stockfish("name", 1, None, depth)
    board = chess.Board()
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
            move, _ = player.get_move(board, explain=False)
            print(f"bestmove {move.uci()}")
        elif line == "quit":
            player.close()
            break
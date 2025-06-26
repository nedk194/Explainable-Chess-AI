import chess.pgn
import pandas as pd
from pathlib import Path

# CONFIG
pgn_path = Path("C:/Users/Ned/Documents/Year-3/FinalProject/explainable-chess-engine/testing/selfplay_results/Stockfish_gauntlet/refined/config_9-2-12-7-7")
output_csv_path = Path("C:/Users/Ned/Documents/Year-3/FinalProject/explainable-chess-engine/testing/pgn_results/pgn_analysis.csv")

# FUNCTION
def total_material(board):
    piece_values = {
        chess.PAWN: 100, 
        chess.KNIGHT: 280, 
        chess.BISHOP: 320, 
        chess.ROOK: 479, 
        chess.QUEEN: 929,
    }
    return sum(len(board.pieces(pt, chess.WHITE)) * val for pt, val in piece_values.items()) + \
           sum(len(board.pieces(pt, chess.BLACK)) * val for pt, val in piece_values.items())

# PROCESS
games_data = []

with open(pgn_path, encoding="utf-8") as pgn_file:
    while True:
        game = chess.pgn.read_game(pgn_file)
        if game is None:
            break

        board = game.board()
        plies = 0
        material_dropped = 0
        previous_material = total_material(board)

        for move in game.mainline_moves():
            board.push(move)
            plies += 1
            current_material = total_material(board)
            if current_material < previous_material:
                material_dropped += (previous_material - current_material)
            previous_material = current_material

        avg_material_exchange_per_move = material_dropped / plies if plies else 0

        games_data.append({
            "White": game.headers.get("White", "Unknown"),
            "Black": game.headers.get("Black", "Unknown"),
            "Result": game.headers.get("Result", "Unknown"),
            "Plies": plies,
            "AvgMaterialExchangePerMove": avg_material_exchange_per_move
        })

# Save results
df = pd.DataFrame(games_data)
df.to_csv(output_csv_path, index=False)

print(f"Saved analysis to {output_csv_path}")

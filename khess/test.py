from khess_tools import Board
from tools import move_to_alg, alg_to_move
WHITE = 0 
BLACK = 1

def test_legal_moves(fen, side=WHITE):
    print(f"Testing legal moves for {'WHITE' if side == WHITE else 'BLACK'}")
    print(f"FEN: {fen}")
    
    board = Board()
    board.set_fen(fen)

    legal_moves = board.moves(side)
    print(f"Legal move count: {len(legal_moves)}")
    print("baord:")
    print(board)
    
    for move in legal_moves:
        try:
            print(f"- {move_to_alg(move)}")
        except Exception as e:
            print(f"Error printing move {move}: {e}")

# Example usage
if __name__ == "__main__":
    board = Board()
    # Test a promotion-ready position
    fen = "rnbqk2r/pppp3p/4p1pn/2b2p2/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    board.set_fen(fen)
    test_legal_moves(fen, BLACK)
    board.play(WHITE, alg_to_move("e8h8", board))
    test_legal_moves(board.fen(), BLACK)

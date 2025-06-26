import chess
import PST

piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
            }

def evaluate_material(board):
    '''
    returns the material relative to white

    Parameters:
    - board: a chess.Board() object representign the players current board

    Returns:
     - an integer representing the material, in centipawns
    '''
    material_score = 0

    for square, piece in board.piece_map().items():
        value = piece_values[piece.piece_type]
        if piece.color == chess.WHITE:
            material_score += value
        else:
            material_score -= value

    return material_score # Positive = White is ahead, Negative = Black is ahead

def evaluate_mobility(board):
    """
    Returns the number of legal moves for a given player.
    
    ATM color doesnt affect the result, its always just for whos go it is 
    
    """
    white = board.turn
    current_moves = len(list(board.legal_moves))  # M
    board.push(chess.Move.null())  # Null move to get opponent's moves
    opponent_moves = len(list(board.legal_moves))  # M'
    board.pop()  # Undo null move

    mobility = current_moves - opponent_moves

    return mobility if white else mobility * -1

def evaluate_pst(board):
    """evaluates the pst of a given color"""
    pst_bonus = 0

    color = chess.WHITE if board.turn else chess.BLACK # turn bool into chess.WHITE/BLACK

    for square, piece in board.piece_map().items():
        if(piece.color == color):
            pst_value = get_pst_value(piece.piece_type, square, color)
            pst_bonus += pst_value


    return pst_bonus 

def get_pst_value(piece_type, square, color):
    """
    Returns the correct PST value for a given piece at a given square.
    """
    if color == chess.BLACK: 
        return PST.PIECE_SQUARE_TABLES_BLACK[piece_type][square]  # Direct lookup for Black
    else:
        return PST.PIECE_SQUARE_TABLES_WHITE[piece_type][square]

def find_pins(board, color):
    """
    Identifies pinned pieces for a given color. Needs refactoring, bit messy. Has not been tested for niche rules 
    Only finds absolute pins
    """
    pinned_squares = []
    pinned_pieces = {}


    for square in chess.SQUARES:
        if board.is_pinned(color, square):
            pinned_squares.append(square)
            print("pinned square: " + str(square))

    for square in pinned_squares:  # for each square that is pinned
        pinned_piece = board.piece_at(square)

        if pinned_piece:
            king_square = board.king(color)  # Find king's location

            piece_attackers = list(board.attackers(not color, square)) # which squares are attacking the pinned piece

            temp_pinned = board.remove_piece_at(square)  # Get the piece before removing
                                                         # temporarily remove pinned piece to accuratly get attackers on king
            king_attackers = list(board.attackers(not color, king_square))  # Find enemy attackers on the king

            board.set_piece_at(square, temp_pinned)# return board to original state

            pinning_pieces = list(set(piece_attackers) & set(king_attackers)) # pieces that attack the king when the pinned piece is removed

            for pinning_square in pinning_pieces:
                pinning_piece = board.piece_at(pinning_square)
                if pinning_piece and pinning_piece.piece_type in {chess.ROOK, chess.BISHOP, chess.QUEEN}:

                    pinned_pieces[square] = (pinned_piece.piece_type, pinning_piece.piece_type)

    return pinned_pieces

def find_skewers(board, color):
    """
    Identifies skewers for a given color.
    Very rough atm, does not account for whether skewered piece is en prise, but does work 
    """
    skewered_pieces = {}

    for square in chess.SQUARES:
        piece = board.piece_at(square)

        # Check if this piece belongs to the player and is a major piece
        if piece and piece.color == color and piece.piece_type in {chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP}:
            attackers = list(board.attackers(not color, square))  # Enemy pieces attacking this square

            for attacker_square in attackers:

                current_attacked_pieces = board.attacks(attacker_square)

                temp_skewered = board.remove_piece_at(square)  # Get the potentialy skewered piece before removing

                new_attacked_pieces = board.attacks(attacker_square) 

                board.set_piece_at(square, temp_skewered)# return board to original state

                shielded_pieces = list(set(current_attacked_pieces) & set(new_attacked_pieces)) # pieces that are under attack after removing major piece

                for shielded_piece in shielded_pieces: 
                    skewered_piece = board.piece_at(shielded_piece)
                    if skewered_piece:
                        skewered_pieces[square] = (piece.piece_type, skewered_piece.piece_type)


    return skewered_pieces

def get_piece_mobility(board, square):
    """
    Returns all legal moves for a piece on a given square.
    """
    piece = board.piece_at(square)
    original_turn = board.turn

    board.turn = piece.color
    
    if not piece:
        return []  # No piece at this square

    legal_moves = [move for move in board.legal_moves if move.from_square == square]

    board.turn = original_turn

    return len(legal_moves)

def king_virtual_mobility(board, color):
    """
    Returns the virtual mobility of the king, the mobility if that king became a queen 
    a higher value means a more vulnerable king
    """
    king_square = board.king(color) # square king is on

    board.set_piece_at(king_square, chess.Piece(chess.QUEEN, color) )

    piece_mobility = get_piece_mobility(board, king_square)

    board.set_piece_at(king_square, chess.Piece(chess.KING, color) )


    return piece_mobility

def evaluate_board_components(board):
    '''returns the relative score of the board for the given color'''
    '''Starting with claude shannon evaluation - only considering material and mobility and pawns'''
    evaluation = {"Material":0, "Mobility":0, "PST": 0}

    evaluation["Material"] =  evaluate_material(board) # already in centipawns
    evaluation["Mobility"] = evaluate_mobility(board) * 10 # each potential move is worth 10 centipawns
    evaluation["PST"] = evaluate_pst(board) # in centipawns
    
    return evaluation
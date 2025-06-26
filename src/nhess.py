
import chess
import evaluation
import time
import PST

piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
            }


def find_best_move(board, depth, is_white, personality):
    """Given a board, determines the best move - using python-chess for move generation"""
    global nodes
    nodes = 0
    t = time.time()
    original_color = chess.WHITE if is_white else chess.BLACK

    best_move = -100000 if is_white else 100000
    best_final = None

    for move in board.legal_moves:
        board.push(move)
        value = minimax(depth - 1, board, -10000, 10000, not is_white, original_color, personality)
        board.pop()
        
        if (is_white and value > best_move) or (not is_white and value < best_move):
            best_move = value
            best_final = move
    
    dt = time.time() - t

    print(f'Nodes: {nodes}, time: {dt:.2f} sec, nodes/sec: {nodes / dt:.2f}')

    return best_final

def minimax(depth, board, alpha, beta, is_maximizing, original_color, personality):
    global nodes


    if depth <= 0 or board.is_game_over():
        nodes += 1
        return evaluate_board_advanced(board, original_color, personality)

    if is_maximizing:
        best_move = -100000
        for move in board.legal_moves:
            board.push(move) # make move
            value = minimax(depth - 1, board, alpha, beta, False, original_color, personality)
            board.pop()
            best_move = max(best_move, value)
            alpha = max(alpha, best_move)
            if beta <= alpha:
                break
        return best_move
    else:
        best_move = 100000
        for move in board.legal_moves:
            board.push(move) # make move
            value = minimax(depth - 1, board, alpha, beta, True, original_color, personality)
            board.pop()
            best_move = min(best_move, value)
            beta = min(beta, best_move)
            if beta <= alpha:
                break

        return best_move
    

def evaluate_board(board):
    ''' returns the evaluation of the board in terms of white, -ve for black
        simple evaluation - material, pst, mobility
    '''

    if board.is_checkmate(): # to look for checkmate instead of just material etc. 
            print("checkmate found")
            print(board.turn)
            if board.turn:
                return -9999
            else:
                return 9999
            
    material_score = 0
    pst_bonus = 0
    mobility = 0
    value = 0

    for square, piece in board.piece_map().items():

        if piece:

            value = piece_values[piece.piece_type]
            
            pst_bonus = PST.PIECE_SQUARE_TABLES_WHITE[piece.piece_type][square] if piece.color == chess.WHITE else PST.PIECE_SQUARE_TABLES_BLACK[piece.piece_type][square]

            mobility = 10* len(board.attacks(square)) 

        value += pst_bonus + mobility
        if piece.color == chess.WHITE:
            material_score += value

        else:
            material_score -= value

    return material_score # Positive = White is ahead, Negative = Black is ahead


def evaluate_board_advanced(board, original_color, personality):
    ''' returns the evaluation of the board in terms of white, -ve for black
        More complex eval - finds king safety using virtual mobility
    '''
    temp_board = board.copy()


    material_score = {"mat":0, "pst":0, "mob":0, "kin": 0}
    pst_bonus = 0
    mobility = 0
    value = 0

    for square, piece in board.piece_map().items():

        if piece:

            value = piece_values[piece.piece_type]
            
            pst_bonus = PST.PIECE_SQUARE_TABLES_WHITE[piece.piece_type][square] if piece.color == chess.WHITE else PST.PIECE_SQUARE_TABLES_BLACK[piece.piece_type][square]

            mobility = len(board.attacks(square)) 

            if piece.piece_type == chess.KING and piece.color == original_color: # square king is on
                # turn king to queen and find mobility
                temp_board.set_piece_at(square, chess.Piece(chess.QUEEN, piece.color) )
                material_score["kin"] = len(temp_board.attacks(square)) # higher value is worse for score
                

        #print("square: " + str(square) + ", has a value of: " + str(value) + ", a pst bonus of: " +str(pst_bonus)+ ", and a mobility of: " + str(mobility))
        if piece.color == chess.WHITE:
            #print("plus "+str(value)+" for white, for square: " + str(square))
            material_score["mat"] += value
            material_score["pst"] += pst_bonus
            material_score["mob"] += mobility

        else:
            #print("minus "+str(value)+" for black, for square: " + str(square))
            material_score["mat"] -= value
            material_score["pst"] -= pst_bonus
            material_score["mob"] -= mobility

    material_norm = material_score['mat'] / 900  # Scale to -1 to +1 (assuming full queen = 900)
    piece_position_norm = material_score['pst'] / 900  # Scale based on material 
    mobility_norm = material_score['mob'] / 20  # Scale based on typical mobility differences
    king_safety_norm = material_score['kin'] / 20  #based on open files/attack factors

    value = personality[0] * material_norm + personality[1] * piece_position_norm + personality[2] * mobility_norm - personality[3] * king_safety_norm
    return value # Positive = White is ahead, Negative = Black is ahead

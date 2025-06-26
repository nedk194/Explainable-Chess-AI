import chess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout

import sys
import time

sys.path.append("khess\khess_old")

import evaluation
import khess 

from stockfish import Stockfish
from khessPlayer import KhessPlayer
from humanPlayer import HumanPlayer
from surge_player import surgePlayer

from gui import ChessGUI
from startMenu import StartMenu
import nhess
import PST

EXPLAIN = False

piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
            }

class ChessGame:
    def __init__(self, gui, player1, player2, autoplay, suggestion):
        """Initialize the chess board."""
        self.board = chess.Board()
        self.gui = gui  # Store GUI reference
        self.players = [player1, player2]
        self.current_player = 0  # Track whose turn it is
        self.next_move_pressed = False
        self.autoplay = autoplay
        self.suggestion = suggestion

    
    def is_game_over(self):
        """Checks if the game has ended (checkmate, stalemate, or draw)."""
        if self.board.is_checkmate():
            return "Checkmate!"
        elif self.board.is_stalemate():
            return "Stalemate!"
        elif self.board.is_insufficient_material():
            return "Draw by Insufficient Material!"
        elif self.board.is_seventyfive_moves():
            return "Draw by 75-Move Rule!"
        elif self.board.is_fivefold_repetition():
            return "Draw by Fivefold Repetition!"
        return None
    
    def play(self):
        '''Main game loop'''
        while not self.board.is_game_over():
            self.gui.update_board(self.board)
            QApplication.processEvents()  # Keep GUI responsive
            player = self.players[self.current_player]

            # if suggestion - both players are of type human - so we need to initialise the engine to provide explanation
            if self.suggestion:
                surge_player = surgePlayer("surge", self.board.turn, self.gui, player.depth)
                explanation = surge_player.get_move(self.board)[1]
                self.gui.log_message(explanation)

            if not player.next_moves : # Prevents search running every iteration
                move, explanation = player.get_move(self.board, explain = EXPLAIN)  
            else:
                move, explanation = player.next_moves[0]

            if explanation:
                self.gui.log_message(explanation) # sends text to the gui log

            if self.autoplay:
                self.next_move_pressed = True        

            if (move and player.human) or (move and not player.human and self.next_move_pressed):
                if self.autoplay and not player.human:
                    time.sleep(1)

                self.board.push(move)


                self.switch_turn()
                self.next_move_pressed = False
                player.reset()

            self.gui.update_board(self.board)
            
    

    def output_move(self, move):
        '''Method to handle the text output to the game log'''
        piece = self.board.piece_at(move.to_square)
        if piece != None:
            color_str = "White" if piece.color else "Black"

            output = str(color_str) + " moved " + str(piece.symbol()) + " from " + str(move)[:2] + " to " + str(move)[2:]

        else:
            output = "Error with piece, piece == None"
        game_over = self.is_game_over()
        if game_over:
            output += ("\n " + game_over)

        return output

    def switch_turn(self):
        '''Alternate player'''
        self.current_player = 1 - self.current_player

    def play_next(self):
        '''Is called from gui when play next button pressed'''
        self.next_move_pressed = True

    
def evaluate_board(board, original_color):
    '''
     ----------------- old method --------------------
        returns the evaluation of the board in terms of white, -ve for black. 

        Parameters:
        - board: a chess.Board() object representign the players current board

        Returns:
    - an integer representing the material, in centipawns
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
    king_safety_norm = material_score['kin'] / 20  # based on open files/attack factors

    value = material_score["mat"] + material_score["pst"] + material_score["mob"] - material_score["kin"]
    return material_score # Positive = White is ahead, Negative = Black is ahead

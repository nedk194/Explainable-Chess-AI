import chess
from PyQt5.QtWidgets import QApplication

import sys

# import player types
from stockfish import Stockfish
from khessPlayer import KhessPlayer
from humanPlayer import HumanPlayer
from surge_player import surgePlayer

from gui import ChessGUI
from startMenu import StartMenu
from chessGame import ChessGame

def start_game(white_choice, white_depth, black_choice, black_depth, starting_fen, autoplay, suggestion):
    """receives settings from StartMenu and initializes the game."""
    # create instance of ChessGUI passing player names
    gui = ChessGUI(str(white_choice), str(black_choice))

    if suggestion:
        # if suggestion - we make the moves manualy
        player1 = get_player_class("Human", chess.WHITE, gui, white_depth)
        player2 = get_player_class("Human", chess.BLACK, gui, black_depth)
    else:
        # initalise the players with the correct classes
        player1 = get_player_class(white_choice, chess.WHITE, gui, white_depth)
        player2 = get_player_class(black_choice, chess.BLACK, gui, black_depth)

    starting_fen = chess.STARTING_FEN if not starting_fen else starting_fen

    # game is an instance of ChessGame - handles all the game logic - uses python-chess
    game =  ChessGame(gui, player1, player2, autoplay, suggestion)
    game.board = chess.Board(starting_fen)

    # link gui to game instance
    gui.game = game  
    gui.show()  

    # start game loop
    game.play()  

def get_player_class(choice, color ,gui, depth):
    """returns the appropriate player class based on the selection."""
    if choice == "Human":
        return HumanPlayer('Human', color, gui, depth) # human player
    elif choice == "Stockfish":
        return Stockfish('Stockfish', color, gui, depth)  # Stockfish 
    elif choice == "Khess AI":
        return KhessPlayer('Khess', color, gui, depth)  # khess
    elif choice == "Surge AI":
        return surgePlayer('Surge AI', color, gui, depth)  # Surge


if __name__ == "__main__":
    '''Program runs from here'''

    app = QApplication(sys.argv) # event loop 
    start_menu = StartMenu()
    
    start_menu.game_settings_signal.connect(start_game)
    start_menu.show()

    sys.exit(app.exec_())

    

    
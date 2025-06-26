import sys
import chess
import chess.svg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QApplication, QTextEdit
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent

from humanPlayer import HumanPlayer

class ChessGUI(QWidget):
    def __init__(self, white_player_name, black_player_name):
        super().__init__()
        self.setWindowTitle("Explainable Chess AI")
        self.setGeometry(100, 100, 1200, 800)

        # Main Layout (Horizontal)
        self.main_layout = QHBoxLayout()

        # Left Section (Chessboard & Labels)
        self.left_layout = QVBoxLayout()

        self.black_label = QLabel(black_player_name)
        self.white_label = QLabel(white_player_name)
        self.black_label.setStyleSheet("font-size: 14px;")
        self.white_label.setStyleSheet("font-size: 14px;")

        self.chessboard = QSvgWidget()
        self.chessboard.setMinimumSize(600, 600)

        self.next_move_button = QPushButton("Next Move")
        self.next_move_button.setMaximumWidth(100)
        self.next_move_button.clicked.connect(self.play_next_move)

        self.left_layout.addWidget(self.black_label)
        self.left_layout.addWidget(self.chessboard)
        self.left_layout.addWidget(self.next_move_button)
        self.left_layout.addWidget(self.white_label)

        # Right Section (Move Breakdown)
        self.right_layout = QVBoxLayout()

        self.move_display = QTextEdit()
        self.move_display.setReadOnly(True)
        self.move_display.setStyleSheet("font-size: 14px;")
        self.move_display.setMinimumWidth(500)
        self.right_layout.addWidget(self.move_display)

        self.navigation_layout = QHBoxLayout()

        self.up_button = QPushButton("⬆️ Previous Move")
        self.up_button.clicked.connect(self.show_previous_move)
        self.navigation_layout.addWidget(self.up_button)

        self.down_button = QPushButton("⬇️ Next Move")
        self.down_button.clicked.connect(self.show_next_move)
        self.navigation_layout.addWidget(self.down_button)

        self.right_layout.addLayout(self.navigation_layout)

        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addLayout(self.right_layout, stretch=1)

        self.setLayout(self.main_layout)

        # Initialize game logic
        self.game = None
        self.selected_square = None
        self.moves = []
        self.current_move_index = -1

    def update_board(self, board):
        board_svg = chess.svg.board(chess.Board(board.fen()), size=400,
                                    squares=[self.selected_square] if self.selected_square else [])
        self.chessboard.load(bytearray(board_svg, encoding="utf-8"))

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            x, y = event.x(), event.y()
            col = (x - self.chessboard.x()) // (self.chessboard.width() // 8)
            row = 7 - ((y - self.chessboard.y()) // (self.chessboard.height() // 8))
            clicked_square = chess.square(col, row)

            if self.selected_square is None:
                if self.game.board.piece_at(clicked_square):
                    self.selected_square = clicked_square
            else:
                from_square = self.selected_square
                to_square = clicked_square
                move = chess.Move(from_square, to_square)

                piece = self.game.board.piece_at(from_square)
                if piece and piece.piece_type == chess.PAWN and (chess.square_rank(to_square) == 0 or chess.square_rank(to_square) == 7):
                    move = chess.Move(from_square, to_square, promotion=chess.QUEEN)

                if move in self.game.board.legal_moves:
                    player = self.game.players[self.game.current_player]
                    if isinstance(player, HumanPlayer):
                        player.set_move(move)

                    self.selected_square = None
                else:
                    self.selected_square = clicked_square
            self.update_board(self.game.board)

    def play_next_move(self):
        self.game.play_next()

    def processEvents(self):
        QApplication.processEvents()


    def log_message(self, message):
        if type(message) is dict:
            if message["type"] == 0:
                # Full component breakdown (Original, Chosen, Next Best)
                original, chosen_move, chosen_comp, chosen_fen, next_move, next_comp, next_fen = message["body"]

                
                formatted = (
                    "<b>Original Position Evaluation:</b><br>"
                    + original.replace("\n", "<br>") + "<br><br>" +
                    f"<b>Chosen Move Evaluation: {chosen_move}</b><br>"
                    + chosen_comp.replace("\n", "<br>") + f"<br>{chosen_fen}<br>" + "<br><br>" +
                    
                    f"<b>Next Best Move Evaluation: {next_move}</b><br>"
                    + next_comp.replace("\n", "<br>")+
                    f"<br>{chosen_fen}<br>"
                )

            elif message["type"] == 1:
                body = message["body"]

                if len(body) == 1:
                    # Agreement case
                    formatted = f"<b>Playstyle Agreement:</b><br>{body[0]}"
                else:
                    # Disagreement case
                    formatted = (
                        "<b>Playstyle Disagreement:</b><br>"
                        + body[0] + "<br><br>"  # "The aggressive and passive playstyles disagree"
                        + "<b>Aggressive Playstyle:</b><br>"
                        + body[1] + "<br>"
                        + body[2].replace("\n", "<br>") + "<br><br>"
                        + "<b>Passive Playstyle:</b><br>"
                        + body[3] + "<br>"
                        + body[4].replace("\n", "<br>")
                    )
            elif message["type"] == 2:
                body = message["body"]  # This is a list of explanation strings

                formatted = "<b>Contextual Explanation:</b><br><br>"

                for entry in body:
                    formatted += entry.replace("\n", "<br>") + "<br><br>"
            
            self.moves.append(formatted)
        else:
            self.moves.append(message)

        self.current_move_index = len(self.moves) - 1  # Always point to latest move
        self.update_move_display()


    def update_move_display(self):
        if 0 <= self.current_move_index < len(self.moves):
            self.move_display.setText(self.moves[self.current_move_index])
        else:
            self.move_display.setText("")

    def show_previous_move(self):
        if self.current_move_index > 0:
            self.current_move_index -= 1
            self.update_move_display()

    def show_next_move(self):
        if self.current_move_index < len(self.moves) - 1:
            self.current_move_index += 1
            self.update_move_display()

def format_board_str(board_str): # come back to this, does not work currently
    ''' returns a 8x8 display of the baord in text format'''
    output = ""
    for i in range(len(board_str)):
        if i % 8 == 0:
            output += "\n"
        output += board_str[i]
    return output
        

def main():
    app = QApplication(sys.argv)
    window = ChessGUI("White", "Black")
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
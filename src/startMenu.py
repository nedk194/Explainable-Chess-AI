from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QSpinBox, QCheckBox
from PyQt5.QtCore import pyqtSignal

class StartMenu(QWidget):
    game_settings_signal = pyqtSignal(str, int, str, int, str, bool, bool)  
    # Signal now includes (white, white_depth, black, black_depth, fen, auto_play)

    def __init__(self):
        """initialise the start menu."""
        super().__init__()
        self.setWindowTitle("Chess Game Setup")
        self.setGeometry(500, 300, 300, 350)  # Set size of start menu

        layout = QVBoxLayout()

        # White player selection
        self.white_label = QLabel("White Player:")
        self.white_dropdown = QComboBox()
        self.white_dropdown.addItems(["Human", "Stockfish", "Khess AI", "Surge AI"])
        layout.addWidget(self.white_label)
        layout.addWidget(self.white_dropdown)

        # White player depth selection
        self.white_depth_label = QLabel("White Search Depth:")
        self.white_depth = QSpinBox()
        self.white_depth.setRange(1, 20)  
        self.white_depth.setValue(3)  
        layout.addWidget(self.white_depth_label)
        layout.addWidget(self.white_depth)

        # Black player selection
        self.black_label = QLabel("Black Player:")
        self.black_dropdown = QComboBox()
        self.black_dropdown.addItems(["Human", "Stockfish", "Khess AI", "Surge AI"])
        layout.addWidget(self.black_label)
        layout.addWidget(self.black_dropdown)

        # Black player depth selection
        self.black_depth_label = QLabel("Black Search Depth:")
        self.black_depth = QSpinBox()
        self.black_depth.setRange(1, 20)
        self.black_depth.setValue(3)
        layout.addWidget(self.black_depth_label)
        layout.addWidget(self.black_depth)

        # FEN Input
        self.fen_label = QLabel("Custom FEN (Leave blank for default):")
        self.fen_input = QLineEdit()
        layout.addWidget(self.fen_label)
        layout.addWidget(self.fen_input)

        # Auto Play Toggle
        self.auto_play_checkbox = QCheckBox("Auto Play")
        layout.addWidget(self.auto_play_checkbox)

        # Suggestion Toggle
        self.suggestion_checkbox = QCheckBox("Suggestion")
        layout.addWidget(self.suggestion_checkbox)

        # Start Game Button
        self.start_button = QPushButton("Start Game")
        self.start_button.clicked.connect(self.send_game_settings)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def send_game_settings(self):
        """Send game settings and close the menu."""
        white_choice = self.white_dropdown.currentText()
        black_choice = self.black_dropdown.currentText()
        starting_fen = self.fen_input.text().strip()
        white_depth = self.white_depth.value()
        black_depth = self.black_depth.value()
        auto_play = self.auto_play_checkbox.isChecked()  # Get auto-play status
        suggestion = self.suggestion_checkbox.isChecked()

        self.game_settings_signal.emit(white_choice, white_depth, black_choice, black_depth, starting_fen, auto_play, suggestion)
        self.close()

from player import Player

class HumanPlayer(Player):
    
    def __init__(self, name, color, gui, depth):
        self.name = name
        self.gui = gui  # Store reference to GUI
        self.move = None  # Store move selected by GUI
        self.color = color
        self.human = True
        self.next_moves = []
        self.depth = depth # only needed when suggestion = true
    
    def get_move(self, board, explain):
        """wait for the user to make a move in the gui"""
        # reset move
        self.move = None  

        while self.move is None:
            # keep the board updated
            self.gui.update_board(board) 
            # process gui events 
            self.gui.processEvents()  

        self.next_moves.append(self.move)

        return (self.move, None)


    def set_move(self, move):
        """called by gui when the user selects a move."""
        # store the move for retrieval
        self.move = move  

    def reset(self):
        '''resets the moves generated'''
        self.next_moves = []

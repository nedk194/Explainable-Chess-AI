import subprocess
import json
from player import Player
import chess
from stockfish import Stockfish
import sys
# material/pst, bad pawns, good pawns, mobility, king_safety
#weights = [1, 7, 7, 1, 1]
# change this to toggle explanation
explains = True

class surgePlayer(Player):
    def __init__(self, name, color, gui, depth):
        self.name = name
        self.gui = gui
        self.color = color
        self.human = False
        self.next_moves = []
        self.depth = depth

        """Start pypy process"""
        self.process = subprocess.Popen(
            ["pypy3", "khess\pypy_process.py"],  # Ensure PyPy3 runs this
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )


    def _send_command(self, method, board, args=[]):
        ''' Send command via subprocess to engine running in pypy3 '''
        # ensures args is a list - even if len(list) = 1
        if not isinstance(args, list):
            args = [args]

        # go - find best move - calls on stockfish class to return top 8 moves
        # this ensures a minimum level of play and also fixes errors in illeagal move generation
        if args[0] == "go":
            stockfish = Stockfish("Stockfish", board.turn, None, 8)
            stockfish_moves = stockfish.get_top_moves(board, 8, 8)
            args.append(stockfish_moves)
        else:
            args.append([])

        # send command via json - properly flush stdin 
        command = json.dumps({"method": method, "args": args}) + "\n"
        self.process.stdin.write(command)
        self.process.stdin.flush()

        while True:
            response = self.process.stdout.readline().strip()

            if not response:
                raise RuntimeError("Received empty response from PyPy3 process")

            try:
                # return the response
                return json.loads(response)
            except json.JSONDecodeError:
                # ignore and wait for the next valid line
                continue  

    def close(self):
        """ end the pypy3 process """
        if self.process:
            self.process.terminate()
            self.process.wait()  # ensure the process is fully closed
            self.process = None

    def get_move(self, board, weights=[7,0,0,0,0], explain = False):
        ''' set the board and find the best move '''
        if explain:
            move =  self.multiple_personalities(board)
        else:
            # the first command to the engine is to set the board to the correct position
            fen = board.fen()
            args = "position fen " + fen
            self._send_command("process", board, [args, self.depth, weights, explains])

            # The second command is to find the best move
            result_dict = self._send_command("process", board, ["go", self.depth, weights, explains])

            # the engine will return a dictionary - with the move and the explanation
            move_str = result_dict["result"]
            move = chess.Move.from_uci(move_str)

            # if explain = False - explanation value is just the score from the leaf node
            explanation = result_dict["explanation"]
            if type(explanation) == int:
                explanation = "Score: " + str(explanation)
            move = move, explanation

        # next moves is used to help handle the auto play feature
        self.next_moves.append(move)

        return move
    
    
    
    def multiple_personalities(self, board):
        personality_1 = [65, 10, 15, 10] # agressive
        personality_2 = [70, 15, 5, 30] # positional
        
        # initalise the board into the engine
        fen = board.fen()
        args = "position fen " + fen
        self._send_command("process", [args, self.depth, personality_1])

        # find personality 1's best move
        result_dict = self._send_command("process", ["go", self.depth, personality_1])
        move_str = result_dict["result"]
        personality_1_move = chess.Move.from_uci(move_str)

        # find personality 2's best move
        result_dict = self._send_command("process", ["go", self.depth, personality_2])
        move_str = result_dict["result"]
        personality_2_move = chess.Move.from_uci(move_str)

        explanation = ""

        # create a Stockfish object and return stockfish's best 5 moves from the board
        stockfish = Stockfish("Stockfish", board.turn, self.gui, self.depth)
        stockfish_moves = stockfish.get_top_moves(board, 5, 10)

        for move in stockfish_moves:
            print(move)
            
        if personality_1_move == personality_2_move:

            if personality_1_move in stockfish_moves:
                explanation = ("Both personalities agree that moving: " + str(personality_1_move) + " is the best move")
                return (personality_1_move, explanation)
            
            else:
                explanation = ("Both personalities agree that moving: " + str(personality_1_move) + " is the best move\n" +
                               "but this move is not a good move, so stockfish will move")

                return (personality_1_move, explanation)
        
        else:
            explanation = ("The two personalities dissagree on which move is best \n"
                            +"The more defensive personality preferes move: " + str(personality_2_move)
                            +". \nWhile the more agresive personality preferes move: " + str(personality_1_move))
            
            if personality_1_move in stockfish_moves and personality_2_move in stockfish_moves:
                explanation += "\nBoth moves are good moves, so personality 1 is chosen\n"
                return (personality_1_move, explanation)
            elif personality_1_move in stockfish_moves:
                explanation += "\nPersonality 2's move is not a good move, so personality 1 is chosen\n"
                return (personality_1_move, explanation)
            elif personality_2_move in stockfish_moves:
                explanation += "\nPersonality 1's move is not a good move, so personality 2 is chosen\n"
                return (personality_2_move, explanation)
            else:
                explanation += "\nNeither of these moves are good moves, so stockfish will move\n"
                return (stockfish_moves[0], explanation)

    
    def reset(self):
        '''Resets the next best moves'''
        self.next_moves = []
    
if __name__ == "__main__":
    wrapper = surgePlayer("Surge", "color", 5)

    #print("right here: " + str(wrapper._send_command("process", ["ucinewgame"])))
    #print("set board: " + str(wrapper._send_command("process", ["go"])))
    board = chess.Board()

    print(wrapper.get_move(board))

    wrapper.close()
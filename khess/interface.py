import chess
from tools import output, log, WHITE, BLACK, alg_to_move
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from khess_tools import Board

class Interface:
    def __init__(self, think):
        self.think = think
        self.stack = []
        self.board = Board()
        self.board.set_fen(chess.STARTING_FEN)
        self.side = WHITE

    def exec(self, command, depth, weights, explain, stock_moves): # added depth as parameter
        '''Execute command received from GUI.'''
        self.stack.append(command) #ned changed this, should have .lower() on command
        while self.stack:
            command = self.stack.pop()
            log(f'>>> {command} ')
            if command == 'quit':
                # GUI wants to quit playing.
                return False

            elif command == 'uci':
                # GUI wants to know if we support UCI interface.
                # We respond with information about the engine and acknowledge
                # that we support UCI.
                output('id name Khess')
                output('id author Kirill Sidorov')
                output('uciok')

            elif command == 'isready':
                # GUI wants to check if we are initialised. We simply acknowledge.
                output('readyok')

            elif command == 'ucinewgame':
                # GUI wants to reset the position and start a new game.
                # We command ourselves to set up the initial position
                self.stack.append('position fen ' + chess.STARTING_FEN)

            elif command.startswith('position'):
                # GUI wants us to set up a position.
                params = command.split(' ')  # Parameters are space-separated
                idx = command.find('moves')  # Did the GUI send the 'moves' keyword?

                if idx >= 0:
                    # The keyword 'moves' was sent. What follows are the moves that we need to
                    # 'play' in algebraic notation.
                    moves_list = command[idx:].split()[1:]
                else:
                    # Otherwise we have no moves to 'play'.
                    moves_list = []

                if params[1] == 'fen':
                    # After 'position' the GUI can specify 'fen' that we need to set up.
                    if idx >= 0:
                        # If within this command there was also a list of moves,
                        # we extract the part of the command upto the keyword 'moves'.
                        fenpart = command[:idx]
                    else:
                        fenpart = command

                    # Extract the FEN string.
                    _, _, fen = fenpart.split(' ', 2)

                elif params[1] == 'startpos':
                    # Instead of a FEN, the GUI can ask to set up the initial position.
                    # In which case we just treat it like the FEN request with the FEN for the initial position.
                    fen = chess.STARTING_FEN

                else:
                    # Other cases are not handled at the moment.
                    log('Cannot handle command', command)

                # Initialise the board, set up commanded FEN, and 'play' the commanded moves.
                self.board = Board()
                self.board.set_fen(fen)
                self.side = WHITE if fen.split()[1] == 'w' else BLACK # changed from side.BACK

                # 'Play' the moves that we were asked to play as part of position set up.
                for move in moves_list:
                    self.board.play(self.side, alg_to_move(move, self.board))
                    self.side = not self.side

            elif command.startswith('go'):
                # GUI wants us to think and return the best move.
                #depth = 5 dont need as its passed as param

                _, *params = command.split(' ')  # Take remaining arguments without "go"
                for param, val in zip(*2*(iter(params),)):  # Iterate over parameter/value pairs
                    if param == 'depth':
                        depth = int(val)
                    else:
                        log('Ignoring parameter', param)

                log(f'Starting search. Side: {self.side}, depth: {depth}')

                # Call the thinking function.
                score_explanation, best_move = self.think(self.board, depth, self.side, weights, explain, stock_moves)

                # Send best move to engine.
                output('bestmove ' + best_move)
                return(best_move, score_explanation)

            else:
                log('Ignoring command', command)

        return ("passed")

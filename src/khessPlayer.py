from player import Player
import khess
import khess_2
import nhess
import time
from stockfish import Stockfish


class KhessPlayer(Player):
    def __init__(self, name, color, gui, depth):
        self.name = name
        
        self.depth = depth  
        self.color = color
        self.human = False
        self.next_moves = []
        self.gui = gui

    def get_move(self, board, explain):
        ''' return the best move - option to add an explanation '''
        ####
        personality_1 = [65, 10, 15, 10]
        personality_2 = [70, 15, 5, 10]
        ####
        if explain:
            best_move = self.multiple_personalities(board)
        else:
            if board.turn:
                best_move = (nhess.find_best_move(board, self.depth, self.color, personality_1), None)
            else:
                best_move = (nhess.find_best_move(board, self.depth, self.color, personality_2), None)

        self.next_moves.append(best_move)

        return best_move
    
    def multiple_personalities(self, board):
        '''
        given a board, produce the next best move, by comparing the moves of two different personalities

        returns the move, and also an explanation, as a tuple
        '''
        personality_1 = [65, 10, 15, 10] # agressive
        personality_2 = [70, 15, 5, 10] # positional

        personality_1_move = nhess.find_best_move(board, self.depth, self.color, personality_1)
        personality_2_move = nhess.find_best_move(board, self.depth, self.color, personality_2)
        explanation = ""

        stockfish = Stockfish("Stockfish", board.turn, self.gui, self.depth)
        stockfish_moves = stockfish.get_top_moves(board, 5, 10)

        
        if personality_1_move == personality_2_move and personality_1 in stockfish_moves:
            explanation = ("Both personalities agree that moving: " + str(personality_1_move) + " is the best move")
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
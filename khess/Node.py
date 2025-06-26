class Node:
    def __init__(self, total, depth, weights, components = None, fen=None, move = None, child_eval = None,  capture = (None, None)):
        self.total = total
        self.components = components if isinstance(components, dict) else {}        
        self.fen = fen 
        self.move = move # move from previous board to get here
        self.child_eval = child_eval
        self.depth = depth
        self.weights = weights
        self.capture = capture

    def as_dict(self):
        return {
            "total": self.total,
            "components": self.components,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "fen": self.fen
        }
    
    def weights_breakdown(self):
        # maybe come back to this, for now i need to focus on other stuff
        sorted_weights = sorted(self.weights.items(), key=lambda x: x[1])
        output = f"This particular evaluation values the components in this order, from most to least significant"

    
    def print_components(self):
        if self.components:
            if self.total == 1000000000 or self.total == -1000000000:
                return self.components['reason']
            else:
                return (
                    f"Total Score: {self.total} \n"
                    f"  Material: {self.components['material']} x{self.weights['material']}\n"
                    f"  Piece Square Table Bonus: {self.components['pst']} x{self.weights['pst']}\n"
                    f"  Mobility: {self.components['mobility']*3} x{self.weights['mobility']}\n"
                    f"  Passed Pawns: {self.components['passed']} x{self.weights['passed']}\n"
                    f"  Isolated Pawns: {self.components['isolated']*12} x{self.weights['isolated']}\n"
                    f"  Doubled Pawns: {self.components['doubled']*12} x{self.weights['doubled']}\n"
                    f"  Backward Pawns: {self.components['backward']*12} x{self.weights['backward']}\n"
                    f"  King Safety: {self.components['king_safety']} x{self.weights['king_safety']}\n"
                )
        return "No components"
    
    def get_total(self):
        return self.total
    
    def get_moves(self):
        if self.child_eval == None:
            return []
        else:
            return self.child_eval.get_moves() + [str(self.move)]
        
    def get_captures(self):
        """returns the line of moves captures or not """
        if self.child_eval == None:
            return []
        else:
            return self.child_eval.get_captures() + [self.capture]
        
    def moves_to_str(self, moves_list):
        output = ""
        for move in moves_list:
            output = move + " -> "+ output
        return output
        
    def get_child(self, depth): 
        # this method doesnt work, not sure why
        # getting: AttributeError: 'NoneType' object has no attribute 'child_eval'\n"
        if depth == 0 or not self.child_eval:
            return self
        
        depth -= 1
        return self.child_eval.get_child(depth)
    
    def explain_score_impact(self, comparison, top_n=8):
        if not self.components or self.total in (1000000000, -1000000000):
            return "This position represents a forced checkmate. no component breakdown is available."

        explanation = f"\nThe move {self.move} is chosen\n" if self.move else ""
        explanation += f"If we play this move, and the opponent plays optimaly, the expected line is: {self.moves_to_str(self.get_moves())}\n"

        explanation += f"Following this line leads to a position of score : {round(self.total, 2)}\n"
        explanation += f"Compared to the score of the position before this move: {round(comparison.total, 2)}\n\n"

        # filter out near-zero components 
        non_zero = {k: v for k, v in self.components.items() if abs(v) > 0.01 and k != 'reason'}
        
        if not non_zero:
            return explanation + "No components had a significant impact on the evaluation."

        # Sort by impact magnitude
        sorted_components = sorted(non_zero.items(), key=lambda x: abs(x[1]), reverse=True)

        explanation += "Key contributing factors:\n"
        for i, (name, value) in enumerate(sorted_components[:top_n]):
            if value > 0:
                explanation += f"{name.replace('_', ' ').capitalize()} improved the score by {round(value, 2)}.\n"
            else:
                explanation += f"{name.replace('_', ' ').capitalize()} reduced the score by {round(abs(value), 2)}.\n"

        return explanation


    def update_minmax(self, child_eval):
        self.min_score = min(self.min_score, child_eval.total)
        self.max_score = max(self.max_score, child_eval.total)
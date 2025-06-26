#!env python3

import sys
import chess
import chess.engine
from tools import output, logging, log, WHITE, BLACK, move_to_alg, alg_to_move, move_flags, NO_PIECE, is_capture
import move_flags as flags
from khess_tools import Board
from time import time
from interface import Interface
from Node import Node
sys.path.append("../src/")
from stockfish import Stockfish
import csv
INF = 1000000000
VERBOSE = True

nodes = 0
# types are: full component, personalities, contextual
explanation_type = 2
performance_csv = []
file_path = "C:/Users/Ned/Documents/Year-3/FinalProject/explainable-chess-engine/testing/performance.csv"

# this dictionary isnt used in current build
component_significance = {
        "material":50,
        "pst":40,
        "mobility":5,
        "passed":2,
        "isolated":-0.1,
        "doubled":-0.1,
        "backward":-0.1,
        "king_safety":5
        }

# provides a natuaral language explanation as to what a component increase means
component_explanation = {
        "material":"material can be improved",
        "pst":"our pieces are better positioned",
        "mobility":"we can make more moves than our opponent",
        "passed":"our pawns are more likely to be promoted than theirs",
        "isolated":"our pawns are better structured",
        "doubled":"our pawns are better structured",
        "backward":"our pawns are better structured",
        "king_safety":"our king is safer than theirs",
        "Checkmate or stalemate":"there is a chackmate or stalemate"
        }



# @profile
def eval_position(board):
    ''' old evaluation method '''
    score = board.score_material()
    score += board.score_pst()
    # eval_hash[board.hash] = score
    return score

def eval_position_adv(board, weights, move, depth):
    ''' A more advanced evaluation of the position - uses evaluation class instead of just a number '''
    # weights order: material/pst, bad pawns, good pawns, mobility, king_safety

    material = board.score_material()
    pst = board.score_pst()
    isolated = board.isolated_pawns(WHITE) - board.isolated_pawns(BLACK)
    doubled = board.doubled_pawns(WHITE) - board.doubled_pawns(BLACK)
    backward = board.backward_pawns(WHITE) - board.backward_pawns(BLACK)
    mobility = len(board.moves(WHITE)) - len(board.moves(BLACK))
    passed = board.passed_score(WHITE) - board.passed_score(BLACK)
    king_safety = board.king_safety(WHITE) - board.king_safety(BLACK)

    # score is a product of each component and its weight summed
    score = 0
    score += weights[0] * (material + pst)
    score -= weights[1] * 12 * (isolated + backward + doubled)
    score += weights[2] * passed
    score += weights[3] * 3 * mobility
    score += weights[4] * king_safety

    components = {
        "material":material,
        "pst":pst,
        "mobility":mobility,
        "passed":passed,
        "isolated":isolated,
        "doubled":doubled,
        "backward":backward,
        "king_safety":king_safety
        }
    
    weights = {"material":weights[0], "pst":weights[0] , "isolated":weights[1],"backward":weights[1],"doubled":weights[1],
                        "passed":weights[2],"mobility":weights[3],"king_safety":weights[4]} 
    
    # these selection statements determine if the move is a capture
    if move:
        if is_capture(move):
            capture = (True, depth)
        else:
            capture = (False, depth)
    else:
        capture = ("No Move", depth)

    move = move_to_alg(move) if move else "none"

    # each node is an evualtion object - offering more insight than just a number
    # a leaf node is determined as self.child_node == null. 
    return Node(
        total=score,
        depth = depth, 
        components = components,
        fen=board.fen(),
        move = move,
        weights = weights,
        capture = capture
        )


# @profile
def minimax_ab(board, depth, max_depth, alpha, beta, side, weights, explain=False, move_passed=None, top_moves_uci = None):
    global nodes  # This is for debugging: how many nodes have we evaluated

    # Keep track of the best score and move so far
    best_move = None
    best_score = None

    top_level_moves = [] if depth == 0 else None

    if depth >= max_depth:  # Depth exceeded
        nodes += 1
        return eval_position_adv(board, weights, move_passed, depth)
    else:  # Depth not exceeded, go deeper
        # Evaluate all legal moves in this position
        moves = board.moves(side)

        # filter out so only stockfish moves are considered in first layer
        if top_moves_uci is not None: 
            moves = [move for move in moves if move_to_alg(move) in top_moves_uci]

        for move in moves:
            board.play(side, move)
            
            # Evaluate the resulting position from the other side's point of view
            score_obj = minimax_ab(board, depth + 1, max_depth, alpha, beta, 1 - side, weights, move)
            score = score_obj.total
            # Revert the tentative move
                
            board.pop(side, move)
            

            if depth == 0:
                # Save all top-level move evaluations
                # this is for move comparisons
                move_alg = move_to_alg(move)
                top_level_moves.append((move_alg, score_obj))
                

            if not score:
                score = 0
            # Remember the best score so far (maximising for white, minimising for black)
            if (best_score is None or (side == WHITE and score > best_score.total) or (side == BLACK and score < best_score.total)):
                best_score = score_obj
                best_move = move  # Also remember the best move

            

            # to add maybe: if score_obj.flags: create a dictionary of flags indicating where the event happens (depth and/or move chain)
            # and also what it was, e.g. material change, passed pawn, check, promotion.
            
            # Alpha-beta
            if side == WHITE:
                if best_score.total >= beta:
                    break
                alpha = max(alpha, best_score.total)
            else:
                if best_score.total <= alpha:
                    break
                beta = min(beta, best_score.total)
            
            if depth == 0 and VERBOSE:
                output(f'info {move_to_alg(move)} {score} {best_score.total}')

        # if game over - either check mate or stalemate - a leaf node needs to be created
        if best_move is None:
            if board.in_check(side):
                # checkmate leaf node
                best_score = Node(
                    total=-INF if side == WHITE else INF,
                    depth = depth, 
                    components={"reason": "checkmate",
                                "material": -INF if side == WHITE else INF,},
                    fen=board.fen(),
                    weights = weights,
                    capture = ("Checkmate", depth)
                )
            else:
                # stalemate leaf node
                best_score = Node(
                    total=0, # might need to adjuct this score to avoid stalemates
                    depth = depth, 
                    components={"reason": "stalemate",
                                "material": 0},
                    fen=board.fen(),
                    weights = weights,
                    capture = ("Stalemate", depth)
                )

    # as only leaf nodes are evaluated fully, we need to check for captures for every node
    if best_move:
        if is_capture(best_move):
            capture = (True, depth)
        else:
            capture = (False, depth)
    else:
        if best_score:
            if best_score.capture[0] == "Checkmate" or best_score.capture[0] == "Stalemate":
                capture = best_score.capture
        
    # instead of propogating the score, we are using a chain of nodes - or evaluation objects
    # each recursion of minimax, we return the new object for that node - along with a link to the node that follows it
    # for the sake of efficiency, we dont evaluate every position - only the leaf nodes
    # this means each node only holds a component breakdown about the final node in the chosen line of play
    next_node = Node(total=best_score.total,
                           depth= depth,
                            components = best_score.components,
                            fen=board.fen(),
                            move = move_to_alg(best_move) if best_move != None else "none",
                            child_eval=best_score,
                            weights = best_score.weights,
                            capture = capture)
    
    # if explain: we are expecting a list to be returned as we need top_level_moves
    if explain and depth == 0:
        return [next_node, best_move, top_level_moves]
    # if not explain: we only expect a tuple
    else:
        return (next_node, best_move) if depth == 0 else next_node


def find_best_move(board, depth, side, weights, explain, stock_moves):
    log(weights)
    global nodes 
    logging.debug(board)
    logging.debug(side)

    # if an explanation is needed - call the explain function
    if explain:
        return explain_move(board, depth, side, weights, stock_moves)
    
    t = time()
    result_obj, move = minimax_ab(board, 0, depth, -INF, INF, side, weights, top_moves_uci=stock_moves)

    score = result_obj.total
    dt = time() - t
        
    
    # catches error of div by 0
    if dt == 0:
        dt = 0.00001

    output_str = str(nodes) + " in " + str(dt) + " seconds "+ str(nodes/dt) + " nodes/second"
    ########## to measure performance over a game
    output(output_str)
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([nodes, dt])
    ##########
    
    nodes = 0
    return score, move_to_alg(move)

def explain_move(board, depth, side, weights, stock_moves):
    global nodes 

    explanation = {"type":explanation_type,
                   "body":[]}
    
    move = None

    if explanation["type"] == 0: # if not multiple personalities
        
        output_list = minimax_ab(board, 0, depth, -INF, INF, side, weights, explain=True, top_moves_uci=stock_moves)

        score_obj, move, top_level_moves = output_list[0], output_list[1], output_list[2]

        # eval object of current board state
        current_eval = eval_position_adv(board, weights, None, depth)

        # for every top level move - turn it into an evaluation object, so we can compare them to other moves
        top_level_move_obj = []
        for move_tup in top_level_moves:
            top_level_move_obj.append(top_level_moves_to_obj(move_tup[0], move_tup[1], board))

        # sort the possible moves from best to worse
        top_level_move_obj = sorted(top_level_move_obj, key=lambda x: x.total, reverse=(side == WHITE))

        
        # summary
        #explanation["body"].append(top_component_comparison(current_eval, score_obj, side, top_n=9))

        # original board before move
        explanation["body"].append(current_eval.print_components())

        # chosen move
        explanation["body"].append(score_obj.moves_to_str(score_obj.get_moves()))
        explanation["body"].append(score_obj.print_components())
        explanation["body"].append(score_obj.get_child(depth).fen)

        # next best move
        explanation["body"].append(top_level_move_obj[1].moves_to_str(top_level_move_obj[1].get_moves()))
        explanation["body"].append(top_level_move_obj[1].print_components())
        explanation["body"].append(top_level_move_obj[1].get_child(depth).fen)
            

    # multiple personality as type = 1
    if explanation["type"] == 1:
        # agressive
        weights = [11,3,6,8,8]
        output_list_agg = minimax_ab(board, 0, depth, -INF, INF, side, weights, explain=False, top_moves_uci=stock_moves)
        score_obj_agg, move_agg = output_list_agg[0], output_list_agg[1]

        # passive
        weights = [8,6,6,3,15]
        output_list_pass = minimax_ab(board, 0, depth, -INF, INF, side, weights, explain=False, top_moves_uci=stock_moves)
        score_obj_pass, move_pass = output_list_pass[0], output_list_pass[1]

        if move_pass == move_agg:
            explanation["body"].append(f"Both playstyles agree that {move_to_alg(move_pass)} is the best move")

        else:
            explanation["body"].append(f"The aggresive and passive playstyles dissagree")
            explanation["body"].append(f"The more aggressive playstle preferes {move_to_alg(move_agg)}")
            explanation["body"].append(explain_capture_line(score_obj_agg))
            explanation["body"].append(f"The more passive playstle preferes {move_to_alg(move_pass)}")
            explanation["body"].append(explain_capture_line(score_obj_pass))
    
        move = move_agg


    # Hybrid
    if explanation["type"] == 2:

        output_list = minimax_ab(board, 0, depth, -INF, INF, side, weights, explain=True, top_moves_uci=stock_moves)

        score_obj, move, top_level_moves = output_list[0], output_list[1], output_list[2]

        # eval object of current board state
        current_eval = eval_position_adv(board, weights, None, depth)

        # for every top level move - turn it into an evaluation object, so we can compare them to other moves
        top_level_move_obj = []
        for move_tup in top_level_moves:
            top_level_move_obj.append(top_level_moves_to_obj(move_tup[0], move_tup[1], board))

        # sort the possible moves from best to worse
        top_level_move_obj = sorted(top_level_move_obj, key=lambda x: x.total, reverse=(side == WHITE))

        # we want to know the best move first
        explanation["body"].append(f"<b>{top_level_move_obj[0].get_moves()[-1]}</b> is the best move")

        explanation["body"].append(f"expecting to follow this line {top_level_move_obj[0].moves_to_str(top_level_move_obj[0].get_moves())}")

        # if theres only one move
        if len(top_level_move_obj) < 2:
            explanation["body"].append("This is the only legal move available (forced from check).")

        else:
            # identify forced moves
            forced_moves = identify_forced_moves(top_level_move_obj, side)
            # handle forced moves only if the chosen move is in there - it should always be
            if forced_moves and top_level_move_obj[0] in forced_moves:
                # filter the list of moves
                top_level_move_obj = forced_moves
                explanation["body"].append(explain_forced_moves(forced_moves)[0])  # natural language explanation

            if len(top_level_move_obj) > 1:
                # resort them - as forced moves may have shuffled
                top_level_move_obj = sorted(top_level_move_obj, key=lambda x: x.total, reverse=(side == WHITE))
                top_components = top_component_comparison(top_level_move_obj[0], current_eval, side)

                if top_components:
                    explanation["body"].append("This move leads to an advantageous position where:")
                    for comp in top_components:
                        explanation["body"].append(
                            f"• {component_explanation[comp[0]]} — <i>{comp[0]} +{comp[1]}</i> (weighted x{score_obj.weights[comp[0]]})"
                        )
                else:
                    explanation["body"].append("There is no significant strategic advantage, but this move maintains balance.")

                explanation["body"].append(explain_capture_line(top_level_move_obj[0]))
    
    nodes = 0

    # returns a string instead of score (int)
    return explanation, move_to_alg(move)


def top_level_moves_to_obj(move, obj, board):
    '''This method is for dealing with top level moves, correctly turning them into Eval objects'''
    if is_capture(alg_to_move(move, board)):
        capture_tup = (True, 0)
    else:
        capture_tup = (False, 0)
    return Node(total=obj.total,
                           depth= 0,
                            components = obj.components,
                            fen=board.fen(),
                            move = move,
                            child_eval=obj,
                            weights = obj.weights,
                            capture = capture_tup)

def identify_forced_moves(moves, side):
    # sort by material
    all_moves_sorted = sorted(moves, key=lambda x: x.components["material"], reverse=(side == WHITE))
        
    best_material = all_moves_sorted[0].components["material"]

    safe_moves = []
    bad_moves = []
    for move in moves:
        # if 
        if (best_material - move.components["material"]) <= 100:
            # if <= a knight difference in mat its a safe move
            safe_moves.append(move)
            
        else:
            bad_moves.append(move)

    log("safe moves----")
    for move in safe_moves:
        log(move.get_moves()[-1])
        log(move.components["material"])


    if len(safe_moves) <= 2: # may need to adjust value
        return safe_moves
    
    else:
        return None
    # r1b1k1nr/pppp1ppp/2n1p3/1B6/3PP2q/2PQ4/P1P2PPP/R1B1K1NR b KQkq - 0 6

def explain_forced_moves(forced_moves):

    if not forced_moves:
        return ""
    
    
    explanation = ["---FORCED MOVE---\n"]

    if len(forced_moves) == 1:
        explanation.append(f"{forced_moves[0].get_moves()[-1]} Is forced")
        explanation.append("as all other moves result in a significant material loss")
        explanation.append(explain_capture_line(forced_moves[0]))
        return (", ".join(explanation), forced_moves)
    else:
    
        moves = []
        moves_fr = []
        moves_to = []
        # extract the move
        for f_move in forced_moves:
                move = f_move.get_moves()[-1]
                moves.append(move)
                moves_fr.append(move[:2])
                moves_to.append(move[2:])
        
        from_map = {}
        to_map = {}

        for i, (fr, to) in enumerate(zip(moves_fr, moves_to)):
            from_map.setdefault(fr, []).append(i)
            to_map.setdefault(to, []).append(i)

        shared_from = {k: v for k, v in from_map.items() if len(v) > 1}
        shared_to = {k: v for k, v in to_map.items() if len(v) > 1}


        if shared_from:
            explanation.append( "\nThese moves are forced: ")
            for sq, indices in shared_from.items():
                explanation.append( (f"{[moves[i] for i in indices]}"))
            explanation.append("\nLikely as they are trying to avoid a capture")
            return (" ".join(explanation), forced_moves)

        if shared_to:
            explanation += "\nThese moves are forced: "
            for sq, indices in shared_to.items():
                explanation.append(f"{[moves[i] for i in indices]}")
            explanation.append("\nLikely as they are making a capture")
            return (" ".join(explanation), forced_moves)

        if (not shared_from or not shared_to):
            move_str = ", ".join(move for move in moves)
            explanation.append(f"One of these moves are forced: {move_str}")
            explanation.append("Not playing one of these will result in significant material loss\n")
            return (" ".join(explanation), forced_moves)

def compare_close_moves(move1, move2, side):
    explanations = []

    if side == WHITE: # could probably clean this up 
        winner = move1 if move1.total > move2.total else move2
        loser = move1 if move1.total < move2.total else move2
    else:
        loser = move1 if move1.total > move2.total else move2
        winner = move1 if move1.total < move2.total else move2

    explanations.append(f"\nMove {winner.get_moves()[-1]} is chosen over {loser.get_moves()[-1]}\n")

    top_components = top_component_comparison(move1, move2, side)

    for comp in top_components:
        component_name = comp[0]
        move1_val = move1.components.get(component_name, "N/A")
        move2_val = move2.components.get(component_name, "N/A")

        explanations.append(
            f"{move1.get_moves()[-1]} is preferred because it improves {component_name} "
            f"({move1_val} vs {move2_val}) compared to {move2.get_moves()[-1]}."
        )
        

    """val1 = winner.components.get(key, 0)
    val2 = loser.components.get(key, 0)
    diff = val1 - val2 if side == WHITE else val2 - val1

    if abs(diff) < component_significance[key]:  # Skip small differences relative to the component
        continue

    if diff > 0:
        explanations.append(
            f"{move1.get_moves()[-1]} is preferred because it improves {key} "
            f"({val1} vs {val2}) compared to {move2.get_moves()[-1]}."
        )
    else:
        explanations.append(
            f"Although {move2.get_moves()[-1]} has better {key} ({val2} vs {val1}), "
            f"{move1.get_moves()[-1]} is still preferred overall due to other factors."
        )"""

    capture_line_1 = explain_capture_line(winner)
    capture_line_2 = explain_capture_line(loser)

    if len(capture_line_1) != len(capture_line_2): # temp fix
        explanations.append(capture_line_1)
        explanations.append(capture_line_2)
    else:
        explanations.append("Both moves have similar capture lines\n")
        explanations.append(capture_line_1)

    return "\n".join(explanations) if explanations else "The moves are evaluated very similarly."

def explain_capture_line(move_obj):
    # raw output looks like: [('No move', 3), (False, 2), (False, 1), (False, 0)]
    raw_capture_line = move_obj.get_captures()
    log(raw_capture_line)
    capture_line_tup = sorted(raw_capture_line, key=lambda x: x[1]) 
    capture_line = [val for val, _ in capture_line_tup]
    explanations = [f"Capture line in playing {move_obj.get_moves()[-1]}: \n"]
    explanations.append(f"{capture_line}\n")


    if "Checkmate" in capture_line: # explain the checkmate move
        index = str(capture_line.index("Checkmate"))
        explanations.append(f"We can liekly force a Checkmate in {index} moves")

    if any(capture_line[:-1]) : # at least one capture not including last move
        explanations.append("This is an aggressive line")
        # if its aggressive - explain how
        if capture_line[0]:
            explanations.append("This move is a capture,")
            if capture_line[1]:
                explanations.append("And we expect a trade,")
        else:
            # not an initial capture but could be setting up capture
            if capture_line[1]: # if we dont capture, but expect them to capture next move
                explanations.append("We are expecting to sacrifice a piece")
            if capture_line[2]:
                explanations.append("This move is likely setting up a capture")

    else:
        explanations.append("This is a positional play - There are no expected captures")

    return ", ".join(explanations)

def top_component_comparison(current_eval, original_eval, side, top_n=2):
    if "reason" in current_eval.components:
        return [("Checkmate or stalemate", 0)]

    diffs = {}
    
    for key in current_eval.components:
        if key in original_eval.components:
            # Multiplier scaling by component type
            multiplier = 1
            if key == "mobility":
                multiplier = 3
            elif key in {"isolated", "backward", "doubled"}:
                multiplier = -12  

            # Direction of comparison based on side
            diff = (current_eval.components[key]  - original_eval.components[key]) * multiplier * current_eval.weights[key] # this assumes oth ecals use the same weights
            if side == BLACK:
                diff *= -1  # Reverse perspective for black

            #if diff > 0:  # Only include improvements
            diffs[key] = diff


    # Sort by impact magnitude and return the top N
    top_components = sorted(diffs.items(), key=lambda item: item[1], reverse=True)[:top_n]
    log(top_components)
    top_components = [(x[0] ,(x[1] / current_eval.weights[x[0]])) for x in top_components]
    log(top_components)
    return top_components


def main():
    depth = 3
    weights = [1, 1, 1, 1, 1]
    explain = False
    interface = Interface(think=find_best_move)
    done = False
    while True:
        done = interface.exec(input(), depth, weights, explain)
        


def test_move():
    global nodes
    board = Board()
    board.set_fen(chess.STARTING_FEN)
    side = WHITE
    t = time()
    score, move = find_best_move(board, 7, side)
    dt = time() - t
    print(nodes, dt, 'seconds', nodes / dt, 'nodes/second')

if __name__ == '__main__':
    # test_move()
    main()

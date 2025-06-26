# khess_engine.py

import sys
from interface import Interface
from khess import find_best_move

''' this wrapper is used for khess_engine.bat - from previous build where i didnt use stockfish threshold '''
DEFAULT_WEIGHTS = [1, 1, 1, 1, 1]

if __name__ == "__main__":
    interface = Interface(find_best_move)

    while True:
        try:
            line = input()
        except EOFError:
            break

        if not line:
            continue

        if line.strip() == "quit":
            break

        # Call your interface with each command
        interface.exec(line.strip(), depth=4, weights=DEFAULT_WEIGHTS, explain=False)

import sys
import os
sys.path.append(os.path.abspath("../khess/khess_tools"))
import khess_tools

print(dir(khess_tools.Board))

# pypy3 khess/khess_tools/setup.py build_ext --inplace

# path to khess: "C:\Users\Ned\Documents\Year-3\FinalProject\explainable-chess-engine\khess\khess.py"

# path to stockfish: "C:\Users\Ned\Documents\Year-3\FinalProject\stockfish\stockfish-windows-x86-64-avx2.exe"

# run stockfish vs stockfish: cutechess-cli.exe -engine cmd=C:\Users\Ned\Documents\Year-3\FinalProject\stockfish\stockfish-windows-x86-64-avx2.exe name=MyEngine -engine cmd=C:\Users\Ned\Documents\Year-3\FinalProject\stockfish\stockfish-windows-x86-64-avx2.exe name=Stockfish -each proto=uci tc=50/60 -games 1 -concurrency 1 -pgnout results.pgn

# run stockfish vs surge: cutechess-cli.exe -engine cmd=C:\Users\Ned\Documents\Year-3\FinalProject\explainable-chess-engine\khess\uci_wrapper.py name=MyEngine -engine cmd=C:\Users\Ned\Documents\Year-3\FinalProject\stockfish\stockfish-windows-x86-64-avx2.exe name=Stockfish -each proto=uci tc=50/60 -games 1 -concurrency 1 -pgnout results.pgn
'''
cutechess-cli.exe -engine cmd="C:\Users\Ned\Documents\Year-3\FinalProject\explainable-chess-engine\src\surge_uci.bat" initstr="5,1,2,3,4,5,6" name=MyEngine -engine cmd="C:\Users\Ned\Documents\Year-3\FinalProject\stockfish\stockfish-windows-x86-64-avx2.exe" name=Stockfish -each proto=uci tc=5/60 -games 1 -concurrency 1 -pgnout results.pgn
 
cutechess-cli.exe -engine name=config_000 cmd=C:/Users/Ned/Documents/Year-3/FinalProject/explainable-chess-engine/src/surge_uci.bat initstr=4,100,3,5,8,12 -engine name=config_000 cmd=C:/Users/Ned/Documents/Year-3/FinalProject/explainable-chess-engine/src/surge_uci.bat initstr=4,100,3,5,8,12 -each proto=uci tc=5/60 -games 1 -concurrency 1 -pgnout results.pgn
 '''

'''r1b1k2r/pppq1ppp/2nb1n2/1B2p3/8/1QN1PN2/PP1P1PPP/R1B1K2R w KQkq - 6 8 for showing different move choices'''
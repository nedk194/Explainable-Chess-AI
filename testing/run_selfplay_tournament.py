import subprocess
import shlex
from pathlib import Path
import json

# SET THESE PATHS
CUTE_CHESS = "C:/Users/Ned/Documents/Year-3/FinalProject/cutechess-1.4.0-beta3-win64/cutechess-cli.exe"
ENGINE_PATH = "C:/Users/Ned/Documents/Year-3/FinalProject/explainable-chess-engine/src/surge_uci.bat"
CONFIG_DIR = Path("C:/Users/Ned/Documents/Year-3/FinalProject/explainable-chess-engine/testing/test_eval_configs/")
OUTPUT_DIR = Path("C:/Users/Ned/Documents/Year-3/FinalProject/explainable-chess-engine/testing/selfplay_results/")
OPENINGS_FILE = ""  # Optional: "/absolute/path/to/openings.pgn"

# SETTINGS
TIME_CONTROL = "5/60"
GAMES_PER_PAIR = 1
CONCURRENCY = 1

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Get all config files
config_files = sorted(CONFIG_DIR.glob("config_*.json"))

# Run all pairwise matches
for i in range(1):
    for j in range(1):
        json1 = config_files[i]
        json2 = config_files[j]

        with open(json1) as f:
            cfg1_json = json.load(f)

        with open(json2) as f:
            cfg2_json = json.load(f)
        
        cfg1 = ",".join(str(v) for v in cfg1_json.values())
        cfg2 = ",".join(str(v) for v in cfg2_json.values())

        name1 = json1.stem
        name2 = json2.stem

        print(f"=== Running match: {name1} vs {name2} ===")

        pgn_out = OUTPUT_DIR / f"{name1}_vs_{name2}.pgn"
        log_out = OUTPUT_DIR / f"{name1}_vs_{name2}.log"

        cmd = [
            CUTE_CHESS,
            "-engine", f"name={name1}", f"cmd={ENGINE_PATH} initstr={cfg1}",
            "-engine", f"name={name2}", f"cmd={ENGINE_PATH} initstr={cfg2}",
            "-each", "proto=uci", f"tc={TIME_CONTROL}",
            "-games", str(GAMES_PER_PAIR),
            "-concurrency", str(CONCURRENCY),
            "-resign", "score=800",
            "-pgnout", str(pgn_out)
        ]

        if OPENINGS_FILE:
            cmd.extend(["-openings", f"file={OPENINGS_FILE}", "format=pgn", "order=random"])
        
        # Run the command
        with open(log_out, "w") as log_file:
            subprocess.run(shlex.split(" ".join(cmd)), stdout=log_file, stderr=subprocess.STDOUT)

print("🏁 All self-play matches complete.")

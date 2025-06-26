import json
from pathlib import Path

# Create a small test config directory
test_config_dir = Path("C:/Users/Ned/Documents/Year-3/FinalProject/explainable-chess-engine/testing/initial_eval_configs")
test_config_dir.mkdir(parents=True, exist_ok=True)

# depth, material/pst, bad pawns, good pawns, mobility, king_safety
initial_configs = [
    {"depth": 5, "material": 10, "bad_pawns": 3, "good_pawns": 10, "mobility": 4, "king_safety": 10},

    # Aggressive
    {"depth": 5, "material": 9, "bad_pawns": 2, "good_pawns": 12, "mobility": 7, "king_safety": 7},

    # Defensive
    {"depth": 5, "material": 8, "bad_pawns": 4, "good_pawns": 8, "mobility": 3, "king_safety": 14},

    # Materialist
    {"depth": 5, "material": 14, "bad_pawns": 2, "good_pawns": 6, "mobility": 3, "king_safety": 9},

    # Passed pawn pusher
    {"depth": 5, "material": 9, "bad_pawns": 3, "good_pawns": 15, "mobility": 4, "king_safety": 8},

    # Structure-focused
    {"depth": 5, "material": 10, "bad_pawns": 6, "good_pawns": 10, "mobility": 2, "king_safety": 10},

    # King fortress
    {"depth": 5, "material": 8, "bad_pawns": 3, "good_pawns": 10, "mobility": 3, "king_safety": 15},

    # Tactical flair
    {"depth": 5, "material": 7, "bad_pawns": 2, "good_pawns": 12, "mobility": 8, "king_safety": 5},

    # Mobility spammer
    {"depth": 5, "material": 9, "bad_pawns": 3, "good_pawns": 8, "mobility": 8, "king_safety": 9},

    # Pawn-structure critic
    {"depth": 5, "material": 10, "bad_pawns": 7, "good_pawns": 8, "mobility": 3, "king_safety": 10},

    # Passive/slow
    {"depth": 5, "material": 10, "bad_pawns": 4, "good_pawns": 6, "mobility": 1, "king_safety": 13},

    # Wildcard
    {"depth": 5, "material": 9, "bad_pawns": 2, "good_pawns": 14, "mobility": 8, "king_safety": 6}
]

# Save them as individual JSON files
for config in initial_configs:

    mat = config["material"]
    bad = config["bad_pawns"]
    good = config["good_pawns"]
    mob = config["mobility"]
    ks = config["king_safety"]

    filename = f"config_{mat}-{bad}-{good}-{mob}-{ks}.json"

    config_path = test_config_dir / filename
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

test_config_dir

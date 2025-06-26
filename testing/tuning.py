import itertools
import json
import pandas as pd
from pathlib import Path

# Define the parameter grid
param_grid = {
    "material": [0.8, 1.0, 1.2],
    "doubled_pawns": [-0.5, -0.3, -0.1],
    "passed_pawns": [0.4, 0.6, 0.8],
    "king_safety": [1.0, 1.2, 1.4],
    "mobility": [0.6, 0.8, 1.0],
}

# Create all combinations of parameters
keys, values = zip(*param_grid.items())
configurations = [dict(zip(keys, v)) for v in itertools.product(*values)]

# Create a folder to save configurations
output_dir = Path("/mnt/data/eval_configs")
output_dir.mkdir(parents=True, exist_ok=True)

# Save each configuration as a JSON file and collect metadata
config_records = []
for idx, config in enumerate(configurations):
    config_name = f"config_{idx:03d}"
    config_path = output_dir / f"{config_name}.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    config_records.append({
        "config_name": config_name,
        **config
    })

# Save a summary CSV for reference
df = pd.DataFrame(config_records)
csv_path = output_dir / "grid_search_summary.csv"
df.to_csv(csv_path, index=False)

f"Saved {len(configurations)} evaluation configurations and summary to: {output_dir}"

import yaml
from pathlib import Path
from collections import defaultdict

TEMPLATE_DIR = Path("templates")

for file in TEMPLATE_DIR.glob("*.yaml"):
    with open(file) as f:
        items = yaml.safe_load(f)

    if isinstance(items, list):
        grouped = defaultdict(list)
        for entry in items:
            section = entry.get("section", "Misc")
            grouped[section].append(entry["item"])
        with open(file, "w") as f:
            yaml.dump(dict(grouped), f, sort_keys=False)
        print(f"Converted: {file.name}")
    else:
        print(f"Skipped (already grouped): {file.name}")

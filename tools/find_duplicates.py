import yaml
from pathlib import Path
from collections import defaultdict

templates_dir = Path("templates")
item_sources = defaultdict(list)

for path in templates_dir.glob("*.yaml"):
    with open(path) as f:
        items = yaml.safe_load(f) or []
        for entry in items:
            key = entry["item"].strip().lower()
            item_sources[key].append(path.name)

duplicates = {k: v for k, v in item_sources.items() if len(v) > 1}
if duplicates:
    for item, sources in duplicates.items():
        print(f"Duplicate: '{item}' found in {sources}")
else:
    print("No duplicates found.")

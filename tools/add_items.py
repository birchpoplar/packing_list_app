import argparse
import yaml
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--topic", required=True)
parser.add_argument("--section", required=True)
parser.add_argument("input_file")
args = parser.parse_args()

topic_file = Path("templates") / f"{args.topic}.yaml"
with open(args.input_file) as f:
    new_items = [line.strip() for line in f if line.strip()]

data = {}
if topic_file.exists():
    with open(topic_file) as f:
        data = yaml.safe_load(f) or {}

section_items = data.get(args.section, [])
for item in new_items:
    if item not in section_items:
        section_items.append(item)

data[args.section] = section_items

with open(topic_file, "w") as f:
    yaml.dump(data, f, sort_keys=False)

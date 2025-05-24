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
    items = [line.strip() for line in f if line.strip()]

entries = [{"item": item, "section": args.section} for item in items]

existing = []
if topic_file.exists():
    with open(topic_file) as f:
        existing = yaml.safe_load(f) or []

with open(topic_file, "w") as f:
    yaml.dump(existing + entries, f, sort_keys=False)

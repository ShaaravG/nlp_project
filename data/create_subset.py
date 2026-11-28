"""
Create a stratified subset of any HotpotQA JSON dataset

Usage: python create_subset.py {input_file} --split {percentage}
"""

import argparse
import json
import random
import sys
from pathlib import Path

# HotpotQA questions are either "bridge" or "comparison", so we stratify by this
COLUMN = "type"
SEED = 42


def load_json_list(path):
  # Read a JSON file and make sure it contains a list

  with open(path, encoding="utf-8") as f:
    data = json.load(f)

  if not isinstance(data, list):
    print("Error: the JSON file must contain a list at the top level.")
    sys.exit(1)

  return data


def group_by_column(items, column):
  # Put items into groups, one group for each value in the column

  groups = {}
  for item in items:
    # Every item must have the column we are grouping by

    if column not in item:
      print(f"Error: an item is missing the column '{column}'.")
      sys.exit(1)

    value = item[column]

    # Start a new group the first time we see this value
    if value not in groups:
      groups[value] = []

    groups[value].append(item)

  return groups


def stratified_subset(items, column, percentage, seed):
  # Select a given percentage of items from each group to be in the subset

  groups = group_by_column(items, column)
  random.seed(seed)

  subset = []
  for value in sorted(groups, key=str):
    group = groups[value]

    # How many items to take from this group (at least 1)
    how_many = round(len(group) * percentage / 100)
    if how_many < 1:
      how_many = 1

    # Add the selected items to the subset
    subset.extend(random.sample(group, how_many))
    print(f"  {value}: {how_many} / {len(group)}")

  # Shuffle the subset to avoid order bias
  random.shuffle(subset)
  return subset


def main():
  # --- Read the command line arguments ----

  parser = argparse.ArgumentParser(description="Create a stratified subset of a HotpotQA JSON file")
  parser.add_argument("input_file", help="path to the HotpotQA JSON file")
  parser.add_argument("--split", type=float, required=True, help="percentage of each group to keep (0-100)")
  args = parser.parse_args()

  input_path = Path(args.input_file)
  percentage = args.split

  if not input_path.is_file():
    print(f"Error: file not found: {input_path}")
    sys.exit(1)

  if percentage <= 0 or percentage > 100:
    print("Error: split percentage must be between 0 and 100.")
    sys.exit(1)

  # The output goes next to the input, with "_subset" added to the name
  output_path = input_path.with_name(input_path.stem + "_subset.json")


  # --------------------------- Build the subset ---------------------------

  items = load_json_list(input_path)
  print(f"Loaded {len(items)} items from {input_path}")
  print(f"Taking {percentage}% from each '{COLUMN}' group:")

  subset = stratified_subset(items, COLUMN, percentage, seed=SEED)
  print(f"Total: {len(subset)} / {len(items)} items")

  # Save the subset
  with open(output_path, "w", encoding="utf-8") as f:
    json.dump(subset, f, indent=2)

  print(f"Saved to {output_path}")


if __name__ == "__main__":
  main()



# ----------- Commands used -----------

# Dev subset: python data/create_subset.py "data/hotpot_dev_fullwiki_v1.json" --split 10
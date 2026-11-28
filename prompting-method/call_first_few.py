"""
Ask Mistral the first few questions from the dev subset (one API call each)

Prerequisite: Create a subset of the dev set using data/create_subset.py

Usage: python call_first_few.py
"""

import sys
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parent

# Let Python find helpers.py in the project root
sys.path.append(str(ROOT))

from helpers import load_questions, call_mistral, get_evals, save_report

# The data to run the method on, and where to save the results
DATA_PATH = ROOT / "data" / "hotpot_dev_fullwiki_v1_subset.json"
OUTPUT_FILE = FOLDER / "call_first_few_results.md"

# From the start of the dataset
NUM_QUESTIONS = 5

PROMPT_TEMPLATE = """Answer the question below. Keep the answer as short as possible
(yes/no, a name, a date, a few words). Reply with ONLY the answer.

Question: {question}"""


def main():
  items = load_questions(DATA_PATH, NUM_QUESTIONS)

  # --------------------------- Ask each question ---------------------------

  results = []
  for item in items:
    prompt = PROMPT_TEMPLATE.format(question=item["question"])
    answer = call_mistral(prompt).strip()

    # Score the answer against the gold answer
    evals = get_evals(answer, item["answer"])

    results.append({
      "question": item["question"],
      "answer": answer,
      "gold": item["answer"],
      **evals,
    })

  # --------------------------- Save the report ---------------------------

  save_report(OUTPUT_FILE, "Mistral answers on first few dev-subset questions", results, prompt=PROMPT_TEMPLATE)


if __name__ == "__main__":
  main()

"""
Asks Mistral to give short reasons behind its answers, gets evals, saves a MD report

Prerequisite: Create a subset of the dev set using data/create_subset.py

Usage: python basic-prompting.py
"""


import sys
from pathlib import Path
from helpers import load_questions, call_mistral, get_evals, save_report


FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parent
sys.path.append(str(ROOT))


# The data to run the method on, and where to save the results
DATA_PATH = ROOT / "data" / "hotpot_dev_fullwiki_v1_subset.json"
OUTPUT_FILE = FOLDER / "basic-prompting_results.md"

# From the start of the dataset
NUM_QUESTIONS = 5

PROMPT_TEMPLATE = """You answer factual questions that may need information from two or
more Wikipedia articles.

1. Reason briefly (at most three short sentences): name the
   intermediate fact you need first, then use it to reach the answer.
2. Then write the answer on a new line starting with "Final answer:".

The final answer must be as short as possible: a name, date, number,
place or short phrase, never a full sentence. For yes/no questions,
write only "yes" or "no". If unsure, give your best guess; never
refuse.

Question: {question}"""


def split_response(response):
  # Split the response into (reasoning, final answer)

  response = response.strip()
  marker = "final answer:"

  # Find the last "Final answer:" (ignoring upper/lower case)
  position = response.lower().rfind(marker)

  if position == -1:
    # No marker: treat the last line as the answer
    lines = response.splitlines()
    reasoning = "\n".join(lines[:-1]).strip()
    answer = lines[-1] if lines else ""
  else:
    reasoning = response[:position].strip()
    answer = response[position + len(marker):].strip()

  # Keep only the first line of the answer and drop a trailing full stop
  answer = answer.splitlines()[0].strip() if answer else ""
  answer = answer.rstrip(".")

  return reasoning, answer


def main():
  items = load_questions(DATA_PATH, NUM_QUESTIONS)

  # --------------------------- Ask each question ---------------------------

  results = []
  for item in items:
    prompt = PROMPT_TEMPLATE.format(question=item["question"])
    response = call_mistral(prompt)
    reasoning, answer = split_response(response)

    # Score the final answer against the gold answer
    evals = get_evals(answer, item["answer"])

    results.append({
      "question": item["question"],
      "reasoning": reasoning,
      "answer": answer,
      "gold": item["answer"],
      **evals,
    })

  # --------------------------- Save the report ---------------------------
  TITLE = "Zero-shot brief-reasoning prompt on first few dev-subset questions"
  save_report(OUTPUT_FILE, TITLE, results, prompt=PROMPT_TEMPLATE)


if __name__ == "__main__":
  main()

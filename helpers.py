"""
Helper functions that can be used to implement a method for answering HotpotQA questions
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from mistralai.client import Mistral
from eval import hotpot_evaluate_v1 as eval


MODEL = "mistral-small-latest"

# Set up the Mistral client
load_dotenv()
API_KEY = os.getenv("MISTRAL_API_KEY")


def load_questions(data_path, num_questions):
  # Load the first few questions from a HotpotQA JSON file

  with open(data_path, encoding="utf-8") as f:
    items = json.load(f)

  return items[:num_questions]


def call_mistral(prompt):
  # Send one prompt to Mistral and return the text of its reply

  if not API_KEY:
    raise SystemExit("MISTRAL_API_KEY is not set (check your .env file).")

  client = Mistral(api_key=API_KEY)
  response = client.chat.complete(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
  )

  return response.choices[0].message.content


def get_evals(prediction, gold):
  # Score one answer with the official HotpotQA exact match and F1

  em = eval.exact_match_score(prediction, gold)
  f1, _precision, _recall = eval.f1_score(prediction, gold)

  return {"em": int(em), "f1": f1}


def average_evals(results):
  # Average EM and F1 over all results

  avg_em = sum(r["em"] for r in results) / len(results)
  avg_f1 = sum(r["f1"] for r in results) / len(results)

  return avg_em, avg_f1


def table_cell(text):
  # Escape characters that would break a markdown table

  return str(text).replace("|", "\\|").replace("\n", " ")


def save_report(path, title, results, prompt=None):
  """
  Save the results as a markdown report.

  Each result is a dict with: question, answer, gold, em, f1
  and optionally "reasoning" (adds a reasoning section to the report).
  """

  avg_em, avg_f1 = average_evals(results)

  # Header with the overall scores
  lines = [
    f"# {title}",
    "",
    f"- Model: `{MODEL}`",
    f"- Questions: {len(results)}",
    f"- **Answer EM: {avg_em:.3f}**",
    f"- **Answer F1: {avg_f1:.3f}**",
    "",
  ]

  # The prompt that was used (if given)
  if prompt:
    lines += ["## Prompt", "", "```text", prompt, "```", ""]

  # One table row per question
  lines += [
    "## Summary",
    "",
    "| # | Question | Answer | Gold | EM | F1 |",
    "|---|----------|--------|------|----|----|",
  ]
  for number, r in enumerate(results, start=1):
    question = table_cell(r["question"])
    answer = table_cell(r["answer"])
    gold = table_cell(r["gold"])
    lines.append(f"| {number} | {question} | {answer} | {gold} | {r['em']} | {r['f1']:.2f} |")

  # The reasoning behind each answer (if the method produced any)
  if "reasoning" in results[0]:
    lines += ["", "## Reasoning per question", ""]
    for number, r in enumerate(results, start=1):
      lines += [
        f"### {number}. {r['question']}",
        "",
        f"**Reasoning:** {r['reasoning']}",
        "",
        f"**Final answer:** {r['answer']} (gold: {r['gold']}; EM={r['em']}, F1={r['f1']:.2f})",
        "",
      ]

  Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
  print(f"EM={avg_em:.3f} F1={avg_f1:.3f}")
  print(f"Saved to {path}")


def save_predictions(path, answers_by_id):
  # Save answers ({question id: answer}) in the format the official HotpotQA eval script reads

  predictions = {"answer": answers_by_id, "sp": {}}

  with open(path, "w", encoding="utf-8") as f:
    json.dump(predictions, f, indent=2)

  print(f"Saved predictions to {path}")

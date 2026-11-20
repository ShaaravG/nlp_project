from mistralai.client import Mistral
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv


# Initialize the Mistral client
env = load_dotenv()
API_KEY = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=API_KEY)


# Send a prompt to Mistral API and get a response
def basic_prompt(question: str, model: str="mistral-small-latest") -> str:
  messages = [
    {
      "role": "user",
      "content": question
    }
  ]

  response = client.chat.complete(
    model=model,
    messages=messages
  )

  return response.choices[0].message.content


# Save the API response as a markdown file
def save_response_as_markdown(question: str, api_response: str) -> Path:
  MARKDOWN_FILE = "response.md"
  path = Path(MARKDOWN_FILE)
  content = f"# Question\n\n{question}\n\n## Answer\n\n{api_response}\n"
  path.write_text(content, encoding="utf-8")
  return path



# ----------- Main Script -----------

question = "What are the three laws of thermodynamics? Explain each briefly."
response = basic_prompt(question)
save_response_as_markdown(question, response)

print(f"Question: {question}")
print("Mistral response saved to response.md")
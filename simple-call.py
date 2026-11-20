from mistralai.client import Mistral
import os
import json
import time
from dotenv import load_dotenv


# Initialize the Mistral client
env = load_dotenv()
API_KEY = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=API_KEY)


# Send a prompt to Mistral API and get a response
def basic_prompt(question, model="mistral-small-latest"):

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

# Example usage

print(f"RUNNING THE SCRIPT...\nAPI KEY: {API_KEY}")

question = "What are the three laws of thermodynamics? Explain each briefly."
print(f"\nQuestion: {question}\n")

answer = basic_prompt(question)
print(f"Answer:\n{answer}\n")


"""
Args:
    question (str): The question to ask, or prompt to send
    model (str): The model to use

Returns:
    str: The model's response
"""
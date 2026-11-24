import json

# Path to your HotpotQA dataset file
file_path = "hotpot_dev_fullwiki_v1.json"

# Open and load the dataset
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Print total number of entries
print(f"Total examples: {len(data)}\n")

# Print the questions
for i, item in enumerate(data[:10]):  # print first 10 questions for demo
    print(f"Question {i+1}: {item['question']}")
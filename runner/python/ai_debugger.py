import os

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_ai(error_text):

    prompt = f"""
You are a senior software engineer.
Explain this error in simple Bangla and give fix:

ERROR:
{error_text}

Return format:
- Problem
- Why it happens
- Fix step by step
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response["choices"][0]["message"]["content"]


report = []

if os.path.exists("errors.txt"):
    with open("errors.txt", "r") as f:
        lines = f.readlines()

    for line in lines:
        ai_response = ask_ai(line)
        report.append(f"""
========================
ERROR: {line.strip()}
------------------------
{ai_response}
""")

with open("report.txt", "w") as f:
    f.write("\n".join(report))

print("AI Debug Report Ready 🚀")
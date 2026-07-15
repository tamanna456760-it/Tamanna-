#!/usr/bin/env python3
import glob
import os

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def refactor_file(path):
    with open(path) as f:
        code = f.read()
    if len(code) > 10000:
        print(f"Skipping {path} (too large)")
        return
    prompt = f"Refactor this Python code for readability, performance, and modern patterns (3.10+). Keep functionality identical. Output only code:\n{code}"
    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4-turbo-preview"),
        messages=[{"role": "user", "content": prompt}]
    )
    new_code = response.choices[0].message.content
    with open(path, 'w') as f:
        f.write(new_code)
    print(f"Refactored {path}")

def main():
    py_files = glob.glob("**/*.py", recursive=True)
    # Exclude test files and venv
    py_files = [f for f in py_files if "test_" not in f and "venv" not in f]
    max_files = 200
    for i, path in enumerate(py_files):
        if i >= max_files:
            break
        refactor_file(path)
    # Git add all changed files
    os.system("git add .")
    os.system("git commit -m '🧠 AI full refactor' || true")

if __name__ == "__main__":
    main()
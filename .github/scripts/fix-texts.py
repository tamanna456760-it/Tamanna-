#!/usr/bin/env python3
import os, subprocess, json
from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def main():
    # Get list of failing tests from pytest cache
    if not os.path.exists(".pytest_cache/v/cache/lastfailed"):
        print("No failing tests found")
        return
    with open(".pytest_cache/v/cache/lastfailed") as f:
        failed = json.load(f)
    for test_file in failed.keys():
        with open(test_file, 'r') as fp:
            code = fp.read()
        prompt = f"Fix this failing test. Return the entire fixed file:\n{code}"
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4-turbo-preview"),
            messages=[{"role": "user", "content": prompt}]
        )
        fixed = response.choices[0].message.content
        with open(test_file, 'w') as fp:
            fp.write(fixed)
        print(f"Fixed {test_file}")

if __name__ == "__main__":
    main()
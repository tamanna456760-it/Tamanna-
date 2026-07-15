#!/usr/bin/env python3
import os
import sys

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def main():
    input_file = None
    output_file = None
    for i, arg in enumerate(sys.argv):
        if arg == "--input":
            input_file = sys.argv[i+1]
        if arg == "--output":
            output_file = sys.argv[i+1]
    if not input_file or not output_file:
        print("Usage: evolve_workflow.py --input <file> --output <file>")
        sys.exit(1)
    with open(input_file) as f:
        content = f.read()
    prompt = f"Improve this GitHub Actions workflow: add error handling, better parallelization, caching. Return only valid YAML.\n\n{content}"
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": prompt}]
    )
    improved = response.choices[0].message.content
    with open(output_file, 'w') as f:
        f.write(improved)
    print("✅ Workflow evolved")

if __name__ == "__main__":
    main()
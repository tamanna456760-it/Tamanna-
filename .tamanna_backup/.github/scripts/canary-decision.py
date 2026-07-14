#!/usr/bin/env python3
import json
import os
import sys

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def main():
    metrics_file = None
    for i, arg in enumerate(sys.argv):
        if arg == "--metrics":
            metrics_file = sys.argv[i + 1]
    if not metrics_file or not os.path.exists(metrics_file):
        print("No metrics, assuming success")
        sys.exit(0)
    with open(metrics_file) as f:
        metrics = json.load(f)
    prompt = f"Based on these canary metrics, should we roll out (true) or rollback (false)? Metrics: {metrics}"
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview", messages=[{"role": "user", "content": prompt}]
    )
    decision = response.choices[0].message.content.strip().lower()
    if "false" in decision:
        print("Rolling back canary")
        subprocess.run(["kubectl", "rollout", "undo", "deployment/tamanna-canary"])
        sys.exit(1)
    else:
        print("Rolling out canary to full traffic")
        subprocess.run(
            [
                "kubectl",
                "set",
                "image",
                "deployment/tamanna-ai",
                f"app={os.environ['REGISTRY']}/tamanna:{os.environ['GITHUB_SHA']}",
            ]
        )
        sys.exit(0)


if __name__ == "__main__":
    import subprocess

    main()

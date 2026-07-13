#!/usr/bin/env python3
import json, sys, numpy as np
def main():
    cost_file = None
    for i, arg in enumerate(sys.argv):
        if arg == "--input":
            cost_file = sys.argv[i+1]
        if arg == "--output":
            output_file = sys.argv[i+1]
    with open(cost_file) as f:
        data = json.load(f)
    costs = [run['cost'] for run in data if 'cost' in run]
    avg_cost = np.mean(costs) if costs else 0
    sug = f"Average cost per run: ${avg_cost:.2f}\n"
    if avg_cost > 10:
        sug += "**Recommendation**: Switch to larger but fewer runners (e.g., 8-core) to reduce overhead.\n"
    else:
        sug += "Current configuration is cost‑effective.\n"
    with open(output_file, 'w') as f:
        f.write(sug)

if __name__ == "__main__":
    main()
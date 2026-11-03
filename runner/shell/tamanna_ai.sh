#!/usr/bin/env bash
# Safe interactive Tamanna AI helper. Does not execute arbitrary user input.
set -Eeuo pipefail

show_help() {
  printf '%s\n' 'Commands: help, code, joke, sarcasm, exit'
}

while true; do
  IFS= read -r -p "You>> " input || break
  case "$input" in
    help) show_help ;;
    code) sed -n '1,160p' "$0" ;;
    joke) printf '%s\n' 'Why did the script pass? It had no syntax errors.' ;;
    sarcasm) printf '%s\n' 'Excellent plan. Let us keep the shell safe, too.' ;;
    exit|quit) break ;;
    "") ;;
    *) printf 'Unknown command: %s (type help)\n' "$input" ;;
  esac
done

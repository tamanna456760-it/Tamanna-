"""Explicitly-run demo for Tamanna's optional chaos/sarcasm engine."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chaos import chaos  # noqa: E402


def main() -> None:
    print("Tamanna AI demo activated.")
    chaos.unleash_sarcasm()


if __name__ == "__main__":
    main()

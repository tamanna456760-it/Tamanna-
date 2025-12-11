Auto Fix & Build
=================

Run the auto-fix and build helpers locally:

- `make fix` — installs dev tools, formats, lints, and runs tests (best-effort, non-fatal)
- `make test` — runs tests
- `bash scripts/auto_build_and_fix.sh` — same as `make fix` but explicit

CI: `.github/workflows/auto_fix_build.yml` runs the auto-fix script on push and every 5 minutes.

Notes:
- The script will attempt to auto-format and auto-fix many files but some files (e.g., shell snippets saved as .py) may produce parsing errors that require manual review.
- If native build dependencies are missing (e.g., PortAudio headers for `pyaudio`), install them in the environment before running `pip install -r requirements.txt`.

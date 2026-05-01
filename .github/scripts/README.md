🤖 BD-King-R7 Universal Auto Code Fixer

A powerful, multi-language auto code fixing engine designed to analyze, format, lint, and improve code quality across different programming languages automatically.

---

🚀 Supported Languages

Language| Extensions
Python| ".py"
JavaScript| ".js"
TypeScript| ".ts"
Go| ".go"
Rust| ".rs"
C / C++| ".c", ".cpp"
Java| ".java"
Ruby| ".rb"
Shell| ".sh"
Markdown| ".md"
JSON| ".json"
YAML| ".yaml", ".yml"

---

⚙️ Features

🧠 Intelligent Auto Fixing

- Detects errors using language-specific tools
- Automatically fixes formatting & lint issues
- Supports safe, aggressive, and full modes

---

⚡ Parallel Processing

- Uses multi-core processing ("ProcessPoolExecutor")
- Speeds up fixing for large projects

---

📊 Issue Tracking

- Counts issues before and after fixing
- Shows how many issues were resolved

---

📄 JSON Report Export

- Generate machine-readable reports
- Useful for CI/CD pipelines

---

🎨 Rich CLI UI (Optional)

- Beautiful terminal output using "rich"
- Progress bar + tables + summary panel

---

🛠 Requirements

Python

- Python 3.9+

Install dependencies

pip install rich

---

External Tools (Important ⚠️)

You must install tools depending on your languages:

Python

pip install ruff autoflake

JS / TS

npm install -g eslint prettier

Go

go install golang.org/x/tools/cmd/goimports@latest
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

Rust

rustup component add rustfmt

C/C++

sudo apt install clang-format

Java

brew install google-java-format

Ruby

gem install rubocop

Shell

sudo apt install shfmt

---

▶️ Usage

Basic Run

python auto_code_fixer.py .

---

With Level Options

python auto_code_fixer.py . --level safe

python auto_code_fixer.py . --level aggressive

python auto_code_fixer.py . --level full

---

Dry Run (No Changes)

python auto_code_fixer.py . --dry-run

---

Parallel Jobs

python auto_code_fixer.py . --jobs 8

---

Export JSON Report

python auto_code_fixer.py . --json-report report.json

---

📊 Output Example

AUTO-FIX REPORT
------------------------------------------------
OK   app.py (Python): 10 → 2 (fixed 8)
FAIL main.js (JavaScript): 5 → 5 (fixed 0)

Total: 2 files, 1 succeeded, 1 failed
Issues fixed: 8

---

📂 Project Structure

.github/
 ├── workflows/
 │   └── bd-king-r7-auto-sync.yml
 └── scripts/
     └── auto_code_fixer.py

---

🧠 How It Works

1. Collects all supported files
2. Detects language by extension
3. Runs language-specific fixers
4. Counts issues before/after
5. Generates report
6. (Optional) Outputs JSON

---

⚠️ Important Notes

- Tools must be installed manually
- Some fixers may modify code structure
- Use "--dry-run" before full execution

---

🔥 Power Mode Levels

Level| Description
safe| Basic lint + format
aggressive| Removes unused imports/variables
full| Deep cleaning + extra fixers

---

🚀 Future Improvements

- AI-based fixing (LLM integration)
- Web dashboard
- GitHub PR auto review
- Error classification system

---

👑 Author

BD-King-R7 Intelligent Automation System
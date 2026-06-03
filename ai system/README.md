# AI File Serial Manager – Advanced Edition

A professional, feature‑rich Python tool to **rename (or copy) files** with sequential numbering, while **saving original names** for full traceability.

---

## ✨ Key Features

- 🔢 **Sequential renaming** – `File_001.txt`, `File_002.jpg` … (custom prefix and start number)
- 💾 **Save original names** – exports `original_names.txt` and `original_names.csv` before any change
- 🔁 **Undo / Rollback** – revert any session using the generated `undo_*.json` file
- 🧪 **Copy mode** – keep original files, create numbered copies
- 🧩 **Regex renaming** – modify names before numbering (e.g., remove prefixes)
- 📊 **Multiple sort orders** – by name (natural), size, modified date, creation date
- ⚡ **Parallel processing** – ultra‑fast for thousands of files
- 🚫 **Exclude patterns** – skip files/folders by name or glob patterns
- ✅ **Dry‑run & interactive confirmation** – preview and approve changes
- 📁 **CSV mapping** – `rename_mapping.csv` with old → new names
- 📝 **Markdown + JSON reports** – human and machine readable
- 🧾 **Persistent log file** – audit trail of every operation

---

## 📦 Requirements

- **Python 3.6+** (no extra libraries required for basic functionality)
- Optional: `tqdm` for a nicer progress bar  
  `pip install tqdm`

---

## 🚀 Quick Start

### 1. Download the script

Save the advanced script as `ai_file_serial_manager_advanced.py`.

### 2. Create a configuration file (optional but recommended)

Create `config.json` in the same folder:

```json
{
  "folder": "./files",
  "prefix": "File",
  "start": 1,
  "recursive": false,
  "extensions": null,
  "dry_run": false,
  "create_folder": true,
  "exclude_patterns": [],
  "sort_by": "name",
  "regex_pattern": null,
  "regex_replacement": null,
  "copy_mode": false,
  "parallel": false,
  "save_names_only": false,
  "log_file": "./renamer.log"
}
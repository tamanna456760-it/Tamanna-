# ⚙️ `settings.md` – Master Configuration for bd‑king‑r7

> **Purpose:** Centralize all environment variables, file paths, API keys, sync rules, and runtime settings across the entire codebase.  
> **Usage:** Every script (`*.py`, `*.js`, `*.sh`, `*.yaml`) should read its config from the sources defined below.

---

## 🌍 Global Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BD_KING_ENV` | `production` | Environment: `development`, `staging`, `production` |
| `BD_KING_LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `BD_KING_SYNC_INTERVAL` | `30` | Seconds between auto‑sync cycles |
| `BD_KING_MAX_RETRY` | `3` | Retry count for failed operations |
| `BD_KING_SECRET_KEY` | *auto‑generated* | Master key for encryption (set in `.env`) |
| `BD_KING_DB_URL` | `sqlite:///data/bd-king-r7.db` | Database connection string |
| `BD_KING_PORT` | `8080` | Main HTTP server port |

---

## 📁 Critical File & Folder Paths

All paths are relative to **project root** unless absolute.

| Purpose | Path | Config file / format |
|---------|------|----------------------|
| **Main AI engine** | `src/core/ai_engine.py` | reads `config/ai_sync_config.json` |
| **Sync engine** | `src/core/syncengine.py` | uses `src/sync/*.yaml` for rules |
| **Nmap scanner** | `src/nmap/` | config in `nmap/automated_upgrade.py` |
| **Wireshark automation** | `src/wireshark/` | capture filters: `capture_filter.py` |
| **Tamanna AI modules** | `src/tamanna/` | settings in `tamanna_memory.json` |
| **PowerHub service** | `src/powerhub/` | systemd service: `autometick.service` |
| **Web frontend (React)** | `website/frontend/` | `.env` file for Vite |
| **Web backend (Node)** | `website/backend/` | `config.js`, `package.json` |
| **Database schema** | `IT/database/schema.sql` | used by `BD_KING_DB_URL` |
| **Backup directory** | `backup/` | all `.sql`, `.py`, `.sh` backup scripts |
| **Log files** | `logs/` (auto‑created) | `bd-king.log`, `sync.log`, `error.log` |

---

## 🔐 Security & Hardening

| Setting | Value / Recommendation |
|---------|------------------------|
| Default SSL certificate | `backup/ssl.sh` generates self‑signed certs |
| Hardening script | `Cybersecurity/security_hardening.sh` |
| API keys (third‑party) | store in `config/secrets.json` (ignored by git) |
| Network defence | `Cybersecurity/network_defence.py` – set `DEFENCE_MODE = "strict"` |
| Forensic mode | `Cybersecurity/Digital_forensics.py` – enable with `--forensic` flag |

---

## 🔄 Sync Configuration

All sync behaviour is controlled by YAML files inside `src/sync/`.

### Main sync rules (`add.yaml`, `fix.yaml`, `git.yaml`)

| Setting | Description |
|---------|-------------|
| `sync.enabled` | `true` / `false` – master on/off switch |
| `sync.source_dirs` | list of folders to monitor (e.g., `["src/", "IT/"]`) |
| `sync.destination` | remote URL or local backup path |
| `sync.auto_commit` | `true` – automatically git commit changes |
| `sync.conflict_resolution` | `"ours"`, `"theirs"`, or `"manual"` |

### Real‑time code sync

- Script: `src/code synce/real_time_code_power.py`
- Config: `src/code synce/docar.yml`
- Watches all `*.py`, `*.js`, `.yaml` files and pushes to `powerhub` service.

---

## 🤖 AI Models & Training

| Model Type | Config File | Location |
|------------|-------------|----------|
| CNN pattern detector | `cnn_config.json` | `data/models/pattern_recognition/configs/` |
| Transformer engine | `transformer_config.json` | same folder |
| LSTM anomaly detector | `lstm_config.json` | `data/models/anomaly_detection/config/` |
| Autoencoder | `autoencoder_config.json` | same |
| GAN detector | `gan_config.json` | same |

**Default training parameters** (from `config/training_configs/default_training.json`):

```json
{
  "batch_size": 32,
  "epochs": 100,
  "learning_rate": 0.001,
  "validation_split": 0.2
}
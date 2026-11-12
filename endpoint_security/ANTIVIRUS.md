# Tamanna AI Antivirus

Tamanna AI provides an optional, read-only malware scan integration using
[ClamAV](https://www.clamav.net/). It does not claim to replace a full endpoint
protection suite.

## Install ClamAV

- Debian/Ubuntu: `sudo apt-get update && sudo apt-get install -y clamav clamav-freshclam`
- Alpine: `apk add clamav clamav-libunrar` (package availability varies by Alpine release)

Update signatures before scanning. Depending on the system, use
`freshclam` (or the platform's ClamAV signature-update service).

## Run a scan

From the repository root:

```bash
python - <<'PY'
from endpoint_security.antivirus import AntivirusScanner

scanner = AntivirusScanner(timeout_seconds=120)
result = scanner.scan_file("path/to/file-to-check")
print(result)
if result["status"] == "infected":
    raise SystemExit("Malware detected; isolate the file and investigate.")
if result["status"] not in {"clean"}:
    raise SystemExit("Scan not verified; inspect scanner status.")
PY
```

Statuses:
- `clean`: ClamAV scanned the file and reported no detection.
- `infected`: ClamAV reported a malware signature.
- `engine_unavailable`: ClamAV is not installed or not on PATH.
- `skipped`: symlink or configured file-size limit prevented scanning.
- `error`: scan could not be completed.

The scanner never executes, deletes, or quarantines a file. A `clean` result
means only that the installed ClamAV engine and signatures did not detect
malware; it is not a guarantee that a file is safe.

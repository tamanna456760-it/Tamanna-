import hashlib
import json
import os
import pathlib
import time

import import
import Path

==============================

Tamanna Radar - File & Code Detector

==============================

Features:

- Scan files and folders

- Detect suspicious extensions

- Detect dangerous keywords in code

- SHA256 hash generator

- Save scan report to JSON

- Real-time terminal output

==============================

SUSPICIOUS_EXTENSIONS = { '.exe', '.bat', '.cmd', '.vbs', '.ps1', '.sh', '.apk', '.jar', '.py', '.php', '.js' }

DANGEROUS_KEYWORDS = [ 'os.system', 'subprocess', 'eval(', 'exec(', 'base64', 'socket', 'requests', 'wget', 'curl', 'rm -rf', 'chmod 777', 'nc -e', 'powershell', 'token', 'webhook', 'cryptography' ]

SCAN_RESULTS = []

def sha256_hash(file_path): """Generate SHA256 hash of file""" sha256 = hashlib.sha256()

try:
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

except Exception as e:
    return f'Hash Error: {e}'

def analyze_code(file_path): """Analyze file content for suspicious code""" findings = []

try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read().lower()

    for keyword in DANGEROUS_KEYWORDS:
        if keyword.lower() in content:
            findings.append(keyword)

except Exception as e:
    findings.append(f'Read Error: {e}')

return findings

def scan_directory(target_dir): """Scan all files in directory""" print(f'\n[+] Scanning Started: {target_dir}\n')

total_files = 0
suspicious_files = 0

for root, dirs, files in os.walk(target_dir):
    for file in files:
        total_files += 1

        full_path = os.path.join(root, file)
        ext = Path(full_path).suffix.lower()

        file_info = {
            'file': full_path,
            'extension': ext,
            'size_kb': round(os.path.getsize(full_path) / 1024, 2),
            'sha256': sha256_hash(full_path),
            'suspicious_keywords': []
        }

        if ext in SUSPICIOUS_EXTENSIONS:
            findings = analyze_code(full_path)
            file_info['suspicious_keywords'] = findings

            if findings:
                suspicious_files += 1
                print(f'[!] Suspicious File Detected: {full_path}')
                print(f'    Keywords: {findings}')
                print('-' * 60)

        SCAN_RESULTS.append(file_info)

print(f'\n[✓] Scan Completed')
print(f'Total Files: {total_files}')
print(f'Suspicious Files: {suspicious_files}')

def save_report(output_file='tamanna_radar_report.json'): """Save scan report to JSON file"""

report = {
    'scanner': 'Tamanna Radar',
    'scan_time': time.ctime(),
    'total_results': len(SCAN_RESULTS),
    'results': SCAN_RESULTS
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=4)

print(f'\n[+] Report Saved: {output_file}')

def main(): print('=' * 60) print('        Tamanna Radar - File & Code Detector') print('=' * 60)

target = input('\nEnter folder path to scan: ').strip()

if not os.path.exists(target):
    print('[X] Invalid Path!')
    return

scan_directory(target)
save_report()

if name == 'main': main()
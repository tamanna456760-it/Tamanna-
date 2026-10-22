#!/usr/bin/env python3
"""
Tamanna AI — Release Manifest Validator
Owner: HM INSAN ALI
Validates a supplied release manifest.
Read-only: does not deploy, pull, or modify Docker images.
"""
import argparse
import json
import re
from pathlib import Path
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")
GIT_COMMIT_RE = re.compile(r"^(?:[a-fA-F0-9]{40}|[a-fA-F0-9]{64})$")
def validate_manifest(manifest):
    findings = []
    if not isinstance(manifest, dict):
        return {
            "project": PROJECT,
            "owner": OWNER,
            "status": "REVIEW_REQUIRED",
            "findings": ["Manifest must be a JSON object."],
            "read_only": True,
        }
    if manifest.get("project") != PROJECT:
        findings.append("Project identity mismatch.")
    if manifest.get("owner") != OWNER:
        findings.append("Owner identity mismatch.")
    release_id = manifest.get("release_id")
    if not isinstance(release_id, str) or not release_id.strip():
        findings.append("release_id must be a non-empty string.")
    commit = manifest.get("git_commit")
    if not isinstance(commit, str) or not GIT_COMMIT_RE.fullmatch(commit):
        findings.append("git_commit must be a full 40- or 64-character hash.")
    images = manifest.get("images")
    if not isinstance(images, dict) or not images:
        findings.append("images must be a non-empty object.")
    else:
        for name, reference in images.items():
            if not isinstance(name, str) or not name.strip():
                findings.append("Image name must be a non-empty string.")
                continue
            if not isinstance(reference, str) or "@" not in reference:
                findings.append(
                    f"{name}: image must use an immutable digest reference."
                )
                continue
            repository, digest = reference.rsplit("@", 1)
            if not repository or not digest.startswith("sha256:"):
                findings.append(f"{name}: invalid image digest reference.")
            elif not SHA256_RE.fullmatch(digest.removeprefix("sha256:")):
                findings.append(f"{name}: SHA-256 digest must contain 64 hex characters.")
    scan_status = manifest.get("security_scan_status")
    if scan_status != "PASS":
        findings.append("Security scan status must be PASS.")
    approval = manifest.get("approved_by")
    if not isinstance(approval, str) or not approval.strip():
        findings.append("approved_by must identify the approving operator.")
    return {
        "project": PROJECT,
        "owner": OWNER,
        "release_id": release_id,
        "status": "PASS" if not findings else "REVIEW_REQUIRED",
        "findings": findings,
        "read_only": True,
        "note": (
            "Validates manifest structure only. Does not verify the Git "
            "commit, image provenance, scan authenticity, or approval."
        ),
    }
def main():
    parser = argparse.ArgumentParser(
        description="Validate a Tamanna AI release manifest."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the release manifest JSON",
    )
    args = parser.parse_args()
    try:
        with Path(args.input).open("r", encoding="utf-8") as file:
            manifest = json.load(file)
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        print(json.dumps({
            "project": PROJECT,
            "owner": OWNER,
            "status": "REVIEW_REQUIRED",
            "findings": [f"Cannot read manifest: {exc}"],
            "read_only": True,
        }, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    result = validate_manifest(manifest)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
if __name__ == "__main__":
    main()
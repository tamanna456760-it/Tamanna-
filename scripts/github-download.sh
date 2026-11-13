#!/usr/bin/env bash
# Download public GitHub repository archives or individual files.
# Downloads are never executed automatically.
set -Eeuo pipefail

usage() {
  cat <<'USAGE'
Tamanna GitHub Downloader

Usage:
  bash scripts/github-download.sh repo OWNER/REPO [REF] [OUTPUT.zip]
  bash scripts/github-download.sh file OWNER/REPO PATH [REF] [OUTPUT]

Examples:
  bash scripts/github-download.sh repo octocat/Hello-World main
  bash scripts/github-download.sh file octocat/Hello-World README.md main README.md

Environment:
  GITHUB_TOKEN  Optional token for higher GitHub API rate limits (never printed).

Notes:
  Only public GitHub repository archives and raw files are supported.
  Downloads are saved as data and are never executed by this script.
USAGE
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
need_cmd() { command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"; }

valid_repo() {
  [[ "$1" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die "Invalid OWNER/REPO: $1"
}
valid_ref() {
  [[ -n "$1" && "$1" != -* && "$1" != *..* && "$1" != *$'\n'* ]] || die "Invalid ref"
}
valid_path() {
  [[ -n "$1" && "$1" != /* && "$1" != -* && "$1" != *$'\n'* ]] || die "Invalid file path"
  case "/$1/" in */../*|*/./*) die "Path traversal is not allowed" ;; esac
}

download() {
  local url="$1" output="$2"
  [[ ! -e "$output" ]] || die "Refusing to overwrite existing file: $output"
  mkdir -p "$(dirname "$output")"
  local tmp
  tmp="$(mktemp "${output}.part.XXXXXX")"
  trap 'rm -f "${tmp:-}"' EXIT
  printf 'Downloading from: %s\n' "$url"
  curl --fail --location --silent --show-error \
    --retry 3 --retry-delay 2 --connect-timeout 15 \
    --max-time 600 --proto '=https' --tlsv1.2 \
    --output "$tmp" "$url" || die "Download failed"
  [[ -s "$tmp" ]] || die "Downloaded file is empty"
  mv -- "$tmp" "$output"
  trap - EXIT
  printf 'Saved: %s\n' "$output"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$output"
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$output"
  fi
}

main() {
  need_cmd curl
  need_cmd mktemp
  need_cmd mv
  need_cmd mkdir
  [[ $# -ge 2 ]] || { usage; exit 2; }

  local mode="$1"
  shift
  case "$mode" in
    repo)
      [[ $# -ge 1 && $# -le 3 ]] || { usage; exit 2; }
      local repo="$1" ref="${2:-main}" output="${3:-}"
      valid_repo "$repo"
      valid_ref "$ref"
      if [[ -z "$output" ]]; then
        output="${repo##*/}-${ref//\//_}.zip"
      fi
      download "https://codeload.github.com/$repo/zip/refs/heads/$ref" "$output"
      ;;
    file)
      [[ $# -ge 2 && $# -le 4 ]] || { usage; exit 2; }
      local repo="$1" path="$2" ref="${3:-main}" output="${4:-}"
      valid_repo "$repo"
      valid_path "$path"
      valid_ref "$ref"
      if [[ -z "$output" ]]; then
        output="${path##*/}"
      fi
      download "https://raw.githubusercontent.com/$repo/$ref/$path" "$output"
      ;;
    *)
      usage
      die "Unknown mode: $mode"
      ;;
  esac
}

main "$@"

#!/usr/bin/env bash
# Read-only domain/DNS/HTTPS audit for Tamanna AI.
set -u

DOMAIN="bd-king-r7.com"
WWW="www.bd-king-r7.com"
PASS=0
WARN=0
FAIL=0

ok()   { printf 'PASS: %s\n' "$1"; PASS=$((PASS + 1)); }
warn() { printf 'WARN: %s\n' "$1"; WARN=$((WARN + 1)); }
bad()  { printf 'FAIL: %s\n' "$1"; FAIL=$((FAIL + 1)); }

echo "=== BD-KING-R7 DOMAIN AUDIT (READ ONLY) ==="
echo "Canonical website: https://$WWW"
echo "Apex domain: https://$DOMAIN"
echo

if ! command -v curl >/dev/null 2>&1; then
  bad "curl is required; install curl and rerun."
  exit 2
fi

if command -v dig >/dev/null 2>&1; then
  for host in "$DOMAIN" "$WWW"; do
    echo "--- DNS: $host ---"
    for type in A AAAA CNAME; do
      answer="$(dig +time=4 +tries=1 +short "$host" "$type" 2>/dev/null | sed '/^$/d')"
      if [ -n "$answer" ]; then
        printf '%s %s\n' "$type" "$answer"
      else
        printf '%s: no record returned\n' "$type"
      fi
    done
  done
  echo "--- Authoritative nameservers ---"
  dig +time=4 +tries=1 +short "$DOMAIN" NS 2>/dev/null || true
  echo "--- DNSSEC DS ---"
  dig +time=4 +tries=1 +short "$DOMAIN" DS 2>/dev/null || true
else
  warn "dig is unavailable; DNS records were not checked. Install dnsutils/bind-tools."
fi

echo
for url in "https://$WWW/" "https://$DOMAIN/" "http://$WWW/" "http://$DOMAIN/"; do
  echo "--- HTTP check: $url ---"
  result="$(curl -sSIL --max-time 20 --connect-timeout 8 -o /dev/null \
    -w 'HTTP=%{http_code} FINAL=%{url_effective} REDIRECTS=%{num_redirects} TLS_VERIFY=%{ssl_verify_result}\n' \
    "$url" 2>&1)"
  rc=$?
  if [ "$rc" -eq 0 ]; then
    printf '%s\n' "$result"
    case "$result" in
      *"HTTP=200"*) ok "$url returned HTTP 200." ;;
      *"HTTP=301"*|*"HTTP=302"*|*"HTTP=307"*|*"HTTP=308"*) warn "$url redirects; verify the final canonical host and HTTPS target." ;;
      *) warn "$url responded, but check its HTTP status and destination." ;;
    esac
  else
    printf '%s\n' "$result"
    bad "$url request failed (curl exit $rc)."
  fi
done

if command -v openssl >/dev/null 2>&1; then
  echo
  echo "--- TLS certificate: $WWW ---"
  cert="$(echo | openssl s_client -connect "$WWW:443" -servername "$WWW" -verify_return_error 2>&1)"
  if printf '%s' "$cert" | grep -q 'Verify return code: 0 (ok)'; then
    ok "TLS certificate verifies for $WWW."
    printf '%s\n' "$cert" | openssl x509 -noout -subject -issuer -dates 2>/dev/null || true
  else
    warn "TLS verification did not return success; inspect certificate, DNS, and Cloudflare SSL mode."
    printf '%s\n' "$cert" | tail -n 8
  fi
else
  warn "openssl is unavailable; certificate details were not checked."
fi

echo
echo "--- Repository domain configuration ---"
if [ -f CNAME ]; then
  configured="$(tr -d '\r\n' < CNAME)"
  if [ "$configured" = "$WWW" ]; then
    ok "CNAME file contains only $WWW."
  else
    bad "CNAME contains '$configured'; expected '$WWW'."
  fi
else
  warn "CNAME file is missing from the current directory."
fi

echo
echo "SUMMARY: PASS=$PASS WARN=$WARN FAIL=$FAIL"
echo "This audit is read-only; it does not change DNS, Cloudflare, GitHub, or server settings."
[ "$FAIL" -eq 0 ]

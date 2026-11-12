# Tamanna AI Cyber Security Center

Owner: HM INSAN ALI

The Cyber Security Center combines existing defensive checks into one read-only
command. It does not exploit targets, discover ports, brute-force credentials,
delete files, quarantine uploads, or change server configuration.

## Run local repository checks

From the repository root:

```bash
python3 -m endpoint_security.cyber_security_center
```

The default run performs local repository posture checks and offline dependency
declaration checks. It does not make network requests.

## Optional TLS certificate check

Only when you are authorized to check the named host:

```bash
python3 -m endpoint_security.cyber_security_center --tls-host www.example.com --tls-port 443
```

The optional network check contacts only the specified hostname and port to
validate its TLS certificate. Supply a hostname, not a URL. Do not use this
option for third-party systems without permission.

## Result interpretation

- `PASS`: configured checks completed without reported findings.
- `REVIEW_REQUIRED`: at least one check needs human review.
- `ERROR`: a check could not complete.

The dependency declaration check verifies version pinning only; it does not
identify known vulnerable packages. A repository audit does not certify the
live website, VPS, or running application. Use CodeQL and dependency advisory
scanning in CI for additional coverage, and verify production systems separately.

## Safety model

All local checks are read-only. The TLS option is a single explicit certificate
check, not a port scan. Findings are reports only; remediation requires a
separate reviewed change and test.

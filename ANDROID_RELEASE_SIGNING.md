# Tamanna Android release signing

The Android CI workflow can produce either a signed release APK or an unsigned
release APK. Signing is optional so CI remains usable before repository secrets
are configured. A release APK is suitable for distribution only after signing.

## 1. Create a release keystore

Run this on a trusted computer with Java's `keytool` installed. Keep the
keystore and passwords in a secure password manager or encrypted backup.

```sh
keytool -genkeypair -v \
  -keystore tamanna-release.jks \
  -alias tamanna-release \
  -keyalg RSA -keysize 4096 -validity 10000
```

Do not commit the keystore, put it in the repository, or send it in chat.
Losing the keystore may prevent publishing updates under the same signing
identity. Never replace it casually after distributing an app.

## 2. Encode the keystore

Linux:

```sh
base64 -w 0 tamanna-release.jks
```

macOS:

```sh
base64 < tamanna-release.jks | tr -d '\\n'
```

Copy the resulting Base64 value locally; do not paste it into a source file.

## 3. Add GitHub Actions repository secrets

Open **Settings → Secrets and variables → Actions → New repository secret**
for this repository and add all four:

| Secret name | Value |
|---|---|
| `ANDROID_KEYSTORE_BASE64` | Base64 output from step 2 |
| `ANDROID_KEYSTORE_PASSWORD` | Keystore password |
| `ANDROID_KEY_ALIAS` | `tamanna-release` (or the alias you chose) |
| `ANDROID_KEY_PASSWORD` | Password for that key |

Settings URL:
https://github.com/tamanna456760-it/Tamanna-/settings/secrets/actions

Do not add these as repository variables, workflow literals, or committed
`.env` entries. Configure all four secrets together. If none are configured,
CI intentionally builds an unsigned release APK; if only some are configured,
CI fails rather than silently producing an unexpected artifact.

## 4. Verify the signed artifact

After the workflow completes, download the artifact whose name ends in
`-signed`. The workflow runs Android `apksigner verify --verbose` against
the release APK before upload when signing is enabled.

The signing key is written only to the GitHub-hosted runner's temporary
directory and is not uploaded as an artifact.

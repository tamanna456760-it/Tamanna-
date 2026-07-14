#!/usr/bin/env bash

echo "========================================"
echo " Tamanna System Token Checker"
echo "========================================"

TOKENS=(
  "GITHUB_TOKEN"
  "OPENAI_API_KEY"
  "DATABASE_URL"
)

FOUND=0

for VAR in "${TOKENS[@]}"; do
    VALUE="${!VAR}"

    if [ -n "$VALUE" ]; then
        echo "✅ $VAR : Configured"
        FOUND=$((FOUND + 1))
    else
        echo "❌ $VAR : Not configured"
    fi
done

echo ""
echo "Configured: $FOUND / ${#TOKENS[@]}"

if [ "$FOUND" -eq "${#TOKENS[@]}" ]; then
    echo "🎉 All required environment variables are configured."
else
    echo "⚠️ Some required environment variables are missing."
fi

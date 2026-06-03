#!/bin/bash
# SAFE GCP SECURITY AUDIT (READ-ONLY)
# User: tamanna456760-it
# Purpose: Configuration & permission review ONLY

echo "========================================"
echo " 🛡️ GCP SECURITY AUDIT (READ-ONLY)"
echo " Project: $(gcloud config get-value project)"
echo "========================================"

echo ""
echo "🔍 IAM POLICY (PUBLIC ACCESS CHECK)"
gcloud projects get-iam-policy $(gcloud config get-value project) \
  --format="table(bindings.role, bindings.members)" | \
  grep -E "allUsers|allAuthenticatedUsers" || echo "✅ No public IAM roles"

echo ""
echo "🔥 FIREWALL RULES (OPEN TO INTERNET)"
gcloud compute firewall-rules list \
  --format="table(name, direction, allowed, sourceRanges)" | \
  grep "0.0.0.0/0" || echo "✅ No open firewall rules"

echo ""
echo "🪣 STORAGE BUCKET ACCESS"
gsutil ls | while read bucket; do
  echo "Bucket: $bucket"
  gsutil iam get "$bucket" | grep -E "allUsers|allAuthenticatedUsers" || echo "  ✅ Private"
done

echo ""
echo "🧾 AUDIT LOGS STATUS"
gcloud logging sinks list

echo ""
echo "✅ AUDIT COMPLETE (NO ATTACKS PERFORMED)"
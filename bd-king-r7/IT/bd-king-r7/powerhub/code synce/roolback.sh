#!/usr/bin/env bash
set -euo pipefail
IMAGE="${1:-your.registry/bd-king-r7-powerhub:previous-tag}"
echo "Rolling back to $IMAGE"
docker pull "$IMAGE"
docker stop powerhub || true
docker rm powerhub || true
docker run -d --name powerhub -p 8080:8080 --restart unless-stopped "$IMAGE"
# health-check
for i in {1..10}; do
  if curl -s http://127.0.0.1:8080/health | grep -q '"status":"ok"'; then
    echo "Rollback succeeded"
    exit 0
  fi
  sleep 2
done
echo "Rollback failed"
exit 2
#!/bin/bash
echo "🔗 Syncing OneNote to Tamanna AI..."
curl -H "Authorization: Bearer $TOKEN" \
     https://graph.microsoft.com/v1.0/me/onenote/pages \
     | jq '.value[] | {title, contentUrl}' > /tamanna/onenote_sync.log

# Optional: convert to .tam format
python3 serialize_to_tamanna.py /tamanna/onenote_sync.log
echo "✅ OneNote sync complete. Echo inscribed."

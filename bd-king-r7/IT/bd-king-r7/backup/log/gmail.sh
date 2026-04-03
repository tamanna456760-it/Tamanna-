#!/bin/bash

# Sovereign Identity
EMAIL="hminsun23@gmail.com"
PASSWORD="your_app_password_here"  # Use Gmail App Password, not your main password
SEARCH_SUBJECT="Security File"     # Change to match your email subject
DOWNLOAD_DIR="$HOME/TamannaDownloads"

# Ritual Start
echo "🔐 Starting Tamanna Secure Download Ritual..."
mkdir -p "$DOWNLOAD_DIR"

# Fetch using curl and IMAP
curl --url "imaps://imap.gmail.com/INBOX" \
     --user "$EMAIL:$PASSWORD" \
     --output "$DOWNLOAD_DIR/security_file.eml" \
     --request "SEARCH SUBJECT \"$SEARCH_SUBJECT\""

# Ritual Completion
if [ -f "$DOWNLOAD_DIR/security_file.eml" ]; then
    echo "✅ File downloaded to $DOWNLOAD_DIR"
else
    echo "⚠️ No matching file found. Check subject or credentials."
fi

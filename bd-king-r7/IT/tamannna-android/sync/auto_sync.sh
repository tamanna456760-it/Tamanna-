#!/bin/bash

echo "🔄 Pulling latest code..."
git pull origin main

echo "📦 Adding changes..."
git add .

echo "📝 Committing..."
git commit -m "Auto sync $(date)"

echo "🚀 Pushing to Git..."
git push origin main

echo "✅ ALL SYSTEMS SYNCED"
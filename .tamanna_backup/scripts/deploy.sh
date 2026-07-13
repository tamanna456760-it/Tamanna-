#!/bin/bash

echo "Deploying Tamanna Site..."

cd /var/www/tamanna

git pull origin main

sudo systemctl reload nginx

echo "Deployment Done!"
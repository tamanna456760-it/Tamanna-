#!/bin/bash

TOKEN="tamanna"

res=$(curl -s -o /dev/null -w "%{http_code}" \
-H "Authorization: token $TOKEN" https://api.github.com/user)

if [ "$res" = "200" ]; then
  echo "✅ Token is valid"
else
  echo "❌ Token invalid or expired"
fi
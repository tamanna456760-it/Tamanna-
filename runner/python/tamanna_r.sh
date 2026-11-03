#!/usr/bin/env bash
set -Eeuo pipefail

# Interactive password prompt; the database dump is written to the current directory.
mysqldump -u root -p tamanna_db > tamanna_db_backup.sql

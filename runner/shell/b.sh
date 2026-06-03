# Postgres: dump and upload (example)
PGPASSWORD=$DB_PASS pg_dump -h localhost -U dbuser dbname | gzip > /backups/db-$(date +%F).sql.gz
# Then upload to S3 using awscli with IAM role
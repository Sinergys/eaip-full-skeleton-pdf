#!/bin/bash
# Скрипт для создания .env.local файла

cat > .env.local <<'ENV'
POSTGRES_USER=eaip_user
POSTGRES_PASSWORD=local_secure_pass
POSTGRES_DB=eaip_db
POSTGRES_HOST=postgres

MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
ENV

echo "✅ Created .env.local"

cat > monitoring/.env.local.monitoring <<'ENV'
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin
PROM_RETENTION=7d
PROM_MEMORY_TARGET=1GB
LOKI_RETENTION_DAYS=7
DOMAIN=localhost

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
ENV

echo "✅ Created monitoring/.env.local.monitoring"


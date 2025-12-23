#!/bin/bash
set -e

echo "💾 EAIP PostgreSQL Backup Setup"
echo "================================"
echo ""

STAGING_DIR="/opt/eaip"
ENV_FILE="$STAGING_DIR/.env"
BACKUP_DIR="/var/backups/eaip"
CRON_FILE="/etc/cron.d/eaip-pg-backup"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Load environment variables
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo -e "${RED}❌ .env file not found at $ENV_FILE${NC}"
    exit 1
fi

# Create backup directory
echo "📁 Creating backup directory..."
sudo mkdir -p "$BACKUP_DIR"
sudo chown $USER:$USER "$BACKUP_DIR"
echo -e "${GREEN}✅ Backup directory created: $BACKUP_DIR${NC}"
echo ""

# Create backup script
echo "📝 Creating backup script..."
BACKUP_SCRIPT="/usr/local/bin/eaip-pg-backup.sh"

sudo tee "$BACKUP_SCRIPT" > /dev/null <<EOF
#!/bin/bash
# EAIP PostgreSQL Backup Script
# Generated on $(date)

BACKUP_DIR="$BACKUP_DIR"
POSTGRES_USER="$POSTGRES_USER"
POSTGRES_DB="$POSTGRES_DB"
CONTAINER_NAME="infra-postgres-1"

# Create backup
BACKUP_FILE="\${BACKUP_DIR}/eaip_\$(date +%F_%H%M%S).sql.gz"

docker exec \$CONTAINER_NAME pg_dump -U \$POSTGRES_USER \$POSTGRES_DB | gzip > \$BACKUP_FILE

# Check if backup was successful
if [ \$? -eq 0 ]; then
    echo "✅ Backup successful: \$BACKUP_FILE"
    
    # Keep only last 7 days of backups
    find \$BACKUP_DIR -name "eaip_*.sql.gz" -mtime +7 -delete
    
    # Log backup
    echo "\$(date): Backup completed - \$BACKUP_FILE" >> \$BACKUP_DIR/backup.log
else
    echo "❌ Backup failed: \$BACKUP_FILE"
    echo "\$(date): Backup failed" >> \$BACKUP_DIR/backup.log
    exit 1
fi
EOF

sudo chmod +x "$BACKUP_SCRIPT"
echo -e "${GREEN}✅ Backup script created: $BACKUP_SCRIPT${NC}"
echo ""

# Create cron job (daily at 2:00 AM)
echo "⏰ Setting up cron job (daily at 2:00 AM)..."
echo "0 2 * * * root $BACKUP_SCRIPT" | sudo tee "$CRON_FILE" > /dev/null
sudo chmod 644 "$CRON_FILE"
echo -e "${GREEN}✅ Cron job created: $CRON_FILE${NC}"
echo ""

# Test backup script
echo "🧪 Testing backup script..."
if docker ps | grep -q "infra-postgres-1"; then
    sudo "$BACKUP_SCRIPT"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Test backup successful${NC}"
        ls -lh "$BACKUP_DIR" | tail -5
    else
        echo -e "${RED}❌ Test backup failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  PostgreSQL container not running, skipping test${NC}"
fi
echo ""

echo -e "${GREEN}✅ Backup setup completed!${NC}"
echo ""
echo "Backup schedule: Daily at 2:00 AM"
echo "Backup location: $BACKUP_DIR"
echo "Retention: 7 days"


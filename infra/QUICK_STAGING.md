# ⚡ Quick Staging Deployment Guide

## 🚀 Быстрый старт

### 1. Развертывание

```bash
# На staging сервере
cd /opt/eaip
bash deploy-staging.sh
```

### 2. Hardening (после развертывания)

```bash
# Все шаги сразу
sudo bash harden-staging.sh

# Или пошагово:
bash post-deploy-checks.sh
bash setup-minio.sh
sudo bash setup-firewall.sh
sudo bash setup-backups.sh
```

### 3. Обновление версии

```bash
bash update-version.sh v0.4.0
```

### 4. Откат

```bash
bash rollback-staging.sh
```

---

## ✅ Чеклист

- [ ] Развертывание выполнено
- [ ] Health checks проходят
- [ ] MinIO bucket создан
- [ ] Firewall настроен
- [ ] Бэкапы настроены
- [ ] Все скрипты исполняемые (`chmod +x *.sh`)

---

## 📋 Команды для проверки

```bash
# Статус контейнеров
docker compose -f docker-compose.staging.yml ps

# Health check
curl -fsS http://127.0.0.1/health

# Логи
docker compose -f docker-compose.staging.yml logs -f

# Статус firewall
sudo ufw status

# Проверка бэкапов
ls -lh /var/backups/eaip/
```

---

**Подробная документация:** `STAGING_DEPLOYMENT.md`


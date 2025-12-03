# 🚀 EAIP Full Skeleton - Быстрый старт для нового окна

**Проект:** EAIP Full Skeleton  
**Версия:** v0.3.0  
**Статус:** ✅ Все настроено и работает

---

## 📋 Что уже готово

✅ **GitHub CI/CD:** Автоматическая сборка Docker образов при push в main и тегах  
✅ **Docker Hub:** Все 7 сервисов опубликованы (`ecosinergys/eaip-full-skeleton-{service}:v0.3.0`)  
✅ **Staging Deployment:** Полная конфигурация и скрипты для staging  
✅ **Monitoring:** Prometheus, Grafana, Loki, Alertmanager настроены  
✅ **Локальная инфраструктура:** Запущена и работает

---

## 🔑 Важные данные

- **GitHub:** `Sinergys/eaip-full-skeleton-pdf`
- **Docker Hub:** `ecosinergys` (токен в GitHub Secrets)
- **GitHub Token:** В переменной окружения `GITHUB_TOKEN` (User)
- **Локальная инфраструктура:** `infra/.env` настроен

---

## 📁 Ключевые файлы

- `SESSION_SUMMARY.md` - полное резюме сессии
- `NEW_SESSION_START.md` - детальная инструкция для нового окна
- `infra/STAGING_DEPLOYMENT.md` - staging guide
- `infra/MONITORING.md` - monitoring guide

---

## 🚀 Быстрые команды

**Локально:**
```bash
cd infra && docker compose up -d
```

**Создать релиз:**
```bash
git tag v0.4.0 -m "Release" && git push origin v0.4.0
```

**Staging:**
```bash
cd /opt/eaip && bash deploy-staging.sh
```

---

**Для подробностей:** Откройте `SESSION_SUMMARY.md` или `NEW_SESSION_START.md`


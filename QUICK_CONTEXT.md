# 🧭 EAIP Full Skeleton v0.3.0 - Quick Context

**Status:** ✅ All configured

## ✅ Ready

- **GitHub CI/CD:** Auto Docker builds (7 services → Docker Hub: `ecosinergys/eaip-full-skeleton-{service}:v0.3.0`)

- **Staging:** Full deployment config (`infra/docker-compose.staging.yml`, `deploy-staging.sh`)

- **Production Monitoring:** Complete observability stack (`infra/monitoring/`, HTTPS via Caddy, Telegram alerts)

- **Local Mini-Prod:** Ready (`infra/docker-compose.local.yml`, `launch-local-mini-prod.sh`)

## 🔑 Key

- **GitHub:** `Sinergys/eaip-full-skeleton-pdf`
- **Docker Hub:** `ecosinergys` (token in GitHub Secrets)
- **Services:** gateway-auth(8000), ingest(8001), validate(8002), analytics(8003), recommend(8004), reports(8005), management(8006)

## 🚀 Quick Commands

### Local Mini-Prod
```bash
cd infra && bash launch-local-mini-prod.sh
```

### Staging Deployment
```bash
cd /opt/eaip && bash deploy-staging.sh
```

### Production Monitoring
```bash
cd /opt/eaip/infra/monitoring && bash launch-prod-observability.sh
```

## 📚 Docs

- `SESSION_SUMMARY.md` - Full session summary
- `infra/STAGING_DEPLOYMENT.md` - Staging deployment guide
- `infra/monitoring/PRODUCTION_DEPLOYMENT.md` - Production monitoring guide
- `infra/LOCAL_MINI_PROD.md` - Local mini-prod guide

---

**Version:** v0.3.0  
**Last Updated:** 2025-11-08


@echo off
echo 🚀 Запуск Enterprise Monitoring Stack...
echo.
cd /d C:\eaip\eaip_full_skeleton\infra
echo 📦 Обновление образов...
docker-compose -f docker-compose.monitoring.yml pull
echo.
echo ▶️ Запуск мониторинга...
docker-compose -f docker-compose.monitoring.yml up -d
echo.
echo ⏳ Ожидание запуска сервисов...
timeout /t 30
echo.
echo 🧪 Проверка health endpoints:
echo.
echo 📊 Prometheus: http://localhost:9090/-/healthy
curl -s http://localhost:9090/-/healthy
echo.
echo 🎨 Grafana: http://localhost:3000/api/health  
curl -s http://localhost:3000/api/health
echo.
echo 🚨 Alertmanager: http://localhost:9093/api/v2/status
curl -s http://localhost:9093/api/v2/status
echo.
echo 📋 Loki: http://localhost:3100/ready
curl -s http://localhost:3100/ready
echo.
echo ✅ Мониторинг запущен!
echo.
echo 🌐 Доступные URL:
echo - Grafana: http://localhost:3000 (admin/admin)
echo - Prometheus: http://localhost:9090  
echo - Alertmanager: http://localhost:9093
echo - Loki: http://localhost:3100
echo - cAdvisor: http://localhost:8080
echo.
pause
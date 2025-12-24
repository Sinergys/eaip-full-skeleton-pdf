# 🐧🔄 **Миграция проекта EAIP: Windows → Linux + Podman**

**Дата создания:** 24.12.2025
**Автор:** AI Assistant (Cline)
**Цель:** Полная миграция проекта EAIP с Windows на Linux с переходом на Podman

---

## 📋 **Оглавление**

1. [Подготовка к миграции](#подготовка-к-миграции)
2. [Установка Linux](#установка-linux)
3. [Перенос проекта](#перенос-проекта)
4. [Установка Podman](#установка-podman)
5. [Настройка окружения](#настройка-окружения)
6. [Запуск и тестирование](#запуск-и-тестирование)
7. [Устранение проблем](#устранение-проблем)
8. [Дополнительные настройки](#дополнительные-настройки)

---

## 🎯 **Обзор миграции**

### **Что будет сделано:**
- ✅ Переход с Windows на Linux (Ubuntu 22.04 LTS)
- ✅ Замена Docker на Podman
- ✅ Полная настройка окружения разработки
- ✅ Тестирование всех компонентов проекта

### **Преимущества после миграции:**
- 🚀 Лучшая производительность Docker/Podman
- 🔒 Повышенная безопасность (rootless режим)
- 🐧 Нативная Linux совместимость
- 📦 Production-ready окружение

---

## 1. 🔧 **Подготовка к миграции**

### **Шаг 1.1: Очистка проекта на Windows**

```powershell
# Перейти в папку проекта
cd C:\eaip

# Удалить временные файлы (уже сделано)
# Проверить размер проекта
Get-ChildItem -Recurse | Measure-Object -Property Length -Sum

# Создать архив проекта
Compress-Archive -Path . -DestinationPath "C:\eaip_backup_2025.zip" -Force
```

### **Шаг 1.2: Финализация Git**

```bash
# Проверить статус
git status
git log --oneline -3

# Создать тег (если нужно)
git tag -a v1.2.6 -m "Pre-migration version"

# Примечание: Push на GitHub сделать после очистки репозитория
```

### **Шаг 1.3: Подготовка данных для переноса**

**Копировать на внешний носитель:**
- ✅ Архив проекта (`eaip_backup_2025.zip`)
- ✅ Важные документы и настройки
- ✅ SSH ключи (если есть)
- ✅ Данные баз данных (если нужно)

---

## 2. 🐧 **Установка Linux**

### **Рекомендация: Ubuntu 22.04 LTS**

### **Шаг 2.1: Создание загрузочной флешки**

```bash
# Скачать Ubuntu 22.04 LTS ISO
# Создать загрузочную флешку с Rufus (Windows) или dd (Linux)
```

### **Шаг 2.2: Установка Ubuntu**

1. **Загрузка с флешки**
2. **Выбор языка:** English (рекомендуется для разработки)
3. **Установка:** Minimal installation + updates
4. **Создание пользователя** с sudo правами

### **Шаг 2.3: Базовая настройка системы**

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка основных инструментов
sudo apt install -y curl wget git vim htop neofetch

# Настройка Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Создание папки проектов
mkdir -p ~/projects
cd ~/projects
```

---

## 3. 📦 **Перенос проекта**

### **Вариант A: Через внешний носитель**

```bash
# Подключить USB диск
# Скопировать архив
cp /media/user/USB/eaip_backup_2025.zip ~/projects/

# Распаковать
cd ~/projects
unzip eaip_backup_2025.zip
mv eaip eaip-project  # Переименовать для ясности
```

### **Вариант B: Через Git (после очистки)**

```bash
cd ~/projects
git clone https://github.com/Sinergys/eaip-full-skeleton-pdf.git eaip-project
cd eaip-project
```

### **Проверка целостности:**

```bash
# Проверить структуру
ls -la
tree -L 2  # Если установлен

# Проверить Git
git status
git log --oneline -5
```

---

## 4. 🐳 **Установка Podman**

### **Шаг 4.1: Установка Podman и podman-compose**

```bash
# Обновить пакеты
sudo apt update

# Установить Podman
sudo apt install -y podman podman-compose

# Проверить установку
podman --version
podman-compose --version
```

### **Шаг 4.2: Настройка rootless режима**

```bash
# Включить lingering (для автоматического запуска)
sudo loginctl enable-linger $USER

# Инициализировать Podman
podman system service --time=0 &

# Проверить
podman info
podman version
```

### **Шаг 4.3: Алиасы для совместимости (опционально)**

```bash
# Добавить в ~/.bashrc
echo "alias docker=podman" >> ~/.bashrc
echo "alias docker-compose=podman-compose" >> ~/.bashrc
source ~/.bashrc
```

---

## 5. ⚙️ **Настройка окружения**

### **Шаг 5.1: Python виртуальное окружение**

```bash
cd ~/projects/eaip-project

# Создать venv
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### **Шаг 5.2: Настройка переменных окружения**

```bash
cd eaip_full_skeleton/infra

# Скопировать пример
cp .env.example .env

# Редактировать при необходимости
nano .env
```

### **Шаг 5.3: Права доступа к скриптам**

```bash
# Сделать скрипты исполняемыми
chmod +x ../scripts/*.sh
chmod +x ../scripts/*.ps1  # Для совместимости

# Проверить
ls -la ../scripts/
```

---

## 6. 🚀 **Запуск и тестирование**

### **Шаг 6.1: Запуск сервисов**

```bash
cd eaip_full_skeleton/infra

# Запуск всех сервисов
podman-compose up -d

# Или с podman напрямую
podman play kube docker-compose.yml

# Проверить статус
podman-compose ps
podman ps
```

### **Шаг 6.2: Тестирование API**

```bash
# Проверить основные эндпоинты
curl -s http://localhost:8000/health
curl -s http://localhost:8001/health
curl -s http://localhost:8002/health

# Проверить все сервисы
curl -s http://localhost:8003/health  # analytics
curl -s http://localhost:8004/health  # recommend
curl -s http://localhost:8005/health  # reports
curl -s http://localhost:8006/health  # management
```

### **Шаг 6.3: Проверка инфраструктуры**

```bash
# PostgreSQL
psql -h localhost -U eaip_user -d eaip_db -c "SELECT version();"

# Redis
redis-cli ping

# MinIO
curl -s http://localhost:9000/minio/health/live
```

---

## 7. 🔧 **Устранение проблем**

### **Проблема: Podman не запускается**

```bash
# Проверить статус сервиса
sudo systemctl status podman

# Перезапустить
sudo systemctl restart podman

# Проверить логи
journalctl -u podman -f
```

### **Проблема: Контейнеры не стартуют**

```bash
# Проверить логи конкретного сервиса
podman-compose logs gateway-auth

# Проверить порты
netstat -tulpn | grep :800

# Проверить ресурсы
df -h  # Диск
free -h  # Память
```

### **Проблема: Ошибки зависимостей Python**

```bash
# Переустановить зависимости
source venv/bin/activate
pip install --force-reinstall -r requirements.txt

# Проверить Python версию
python3 --version
pip --version
```

### **Проблема: Git проблемы**

```bash
# Проверить remote
git remote -v

# Переустановить origin
git remote set-url origin https://github.com/Sinergys/eaip-full-skeleton-pdf.git

# Push (после очистки репозитория)
git push origin main
```

---

## 8. 🎨 **Дополнительные настройки**

### **Шаг 8.1: Установка VS Code для Linux**

```bash
# Скачать и установить VS Code
wget -O vscode.deb "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64"
sudo dpkg -i vscode.deb

# Установить расширения
code --install-extension ms-python.python
code --install-extension ms-vscode.vscode-json
code --install-extension redhat.vscode-yaml
```

### **Шаг 8.2: Настройка терминала**

```bash
# Установить zsh и oh-my-zsh (опционально)
sudo apt install zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Настройка алиасов в ~/.zshrc
echo "alias dc='podman-compose'" >> ~/.zshrc
echo "alias k='kubectl'" >> ~/.zshrc
```

### **Шаг 8.3: Мониторинг и логи**

```bash
# Установить monitoring tools
sudo apt install htop iotop ncdu

# Просмотр логов
podman-compose logs -f  # Все сервисы
podman logs -f eaip-infra-gateway-auth-1  # Конкретный контейнер
```

### **Шаг 8.4: Резервное копирование**

```bash
# Создать скрипт бэкапа
cat > ~/backup_eaip.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/backups/eaip
mkdir -p $BACKUP_DIR

# Бэкап проекта
tar -czf $BACKUP_DIR/eaip_project_$DATE.tar.gz ~/projects/eaip-project

# Бэкап volumes (если нужно)
# podman volume export pgdata > $BACKUP_DIR/pgdata_$DATE.tar

echo "Backup completed: $BACKUP_DIR/eaip_project_$DATE.tar.gz"
EOF

chmod +x ~/backup_eaip.sh
```

---

## 📊 **Проверка после миграции**

### **Чек-лист готовности:**

- ✅ **Linux установлен** (Ubuntu 22.04 LTS)
- ✅ **Podman работает** (`podman --version`)
- ✅ **Проект перенесен** (структура файлов)
- ✅ **Python окружение** (`source venv/bin/activate`)
- ✅ **Сервисы запускаются** (`podman-compose up -d`)
- ✅ **API отвечает** (`curl localhost:8000/health`)
- ✅ **Git настроен** (`git status`)
- ✅ **VS Code установлен** (с расширениями)

### **Производительность:**

```bash
# Сравнение скорости
time podman run hello-world
time docker run hello-world  # Если Docker установлен
```

---

## 🎯 **Следующие шаги после миграции**

### **Короткий срок (1-2 дня):**
1. **Протестировать** все функции проекта
2. **Очистить** репозиторий для GitHub
3. **Закоммитить** изменения миграции

### **Средний срок (1 неделя):**
1. **Начать Stage 3** разработки
2. **Оптимизировать** конфигурацию Podman
3. **Настроить** CI/CD пайплайны

### **Долгосрочные планы:**
1. **Kubernetes** интеграция
2. **Production** развертывание
3. **Monitoring** и логирование

---

## 📞 **Поддержка и помощь**

### **Если возникли проблемы:**

1. **Проверить логи:**
   ```bash
   podman-compose logs
   journalctl -f
   ```

2. **Перезапустить сервисы:**
   ```bash
   podman-compose down
   podman-compose up -d
   ```

3. **Полная переустановка:**
   ```bash
   podman system reset
   podman-compose up -d
   ```

### **Полезные команды для отладки:**

```bash
# Статус системы
podman system info
podman version

# Управление контейнерами
podman ps -a
podman logs <container_name>
podman exec -it <container_name> /bin/bash

# Управление volumes
podman volume ls
podman volume inspect <volume_name>

# Управление networks
podman network ls
podman network inspect <network_name>
```

---

## 🎉 **Поздравляем с миграцией!**

**Linux + Podman** обеспечит:
- 🚀 **Высокую производительность**
- 🔒 **Повышенную безопасность**
- 🐧 **Нативную совместимость**
- 📦 **Production-ready окружение**

**Проект EAIP готов к дальнейшей разработке!** 🔥

---

*Документ создан: 24.12.2025*
*Обновлено: 24.12.2025*
*Версия: 1.0*

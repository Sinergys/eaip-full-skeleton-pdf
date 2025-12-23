# GitHub Authentication Guide

## Способ 1: Personal Access Token (PAT) - Рекомендуется

### Шаг 1: Создайте Personal Access Token на GitHub

1. Перейдите на https://github.com/settings/tokens
2. Нажмите **"Generate new token"** → **"Generate new token (classic)"**
3. Задайте имя токена (например: `eaip-full-skeleton-pdf`)
4. Выберите срок действия (рекомендуется: `90 days` или `No expiration`)
5. Выберите права доступа (scopes):
   - ✅ **repo** (полный доступ к репозиториям)
   - ✅ **workflow** (если используете GitHub Actions)
6. Нажмите **"Generate token"**
7. **ВАЖНО**: Скопируйте токен сразу! Он больше не будет показан.

### Шаг 2: Используйте токен для push

При следующем `git push` введите:
- **Username**: `EcoSinergys` (или ваш GitHub username)
- **Password**: вставьте ваш Personal Access Token (не пароль!)

## Способ 2: GitHub CLI (gh)

### Установка GitHub CLI

```powershell
# Через winget
winget install --id GitHub.cli

# Или через Chocolatey
choco install gh

# Или скачайте с https://cli.github.com/
```

### Авторизация через CLI

```powershell
gh auth login
# Выберите:
# - GitHub.com
# - HTTPS
# - Авторизовать через браузер
```

## Способ 3: SSH ключи

### Генерация SSH ключа

```powershell
ssh-keygen -t ed25519 -C "your_email@example.com"
# Нажмите Enter для сохранения в стандартное место
# Введите пароль (или оставьте пустым)
```

### Добавление ключа на GitHub

1. Скопируйте публичный ключ:
   ```powershell
   cat ~/.ssh/id_ed25519.pub
   ```

2. Перейдите на https://github.com/settings/keys
3. Нажмите **"New SSH key"**
4. Вставьте ключ и сохраните

5. Измените remote URL:
   ```powershell
   git remote set-url origin git@github.com:EcoSinergys/eaip-full-skeleton-pdf.git
   ```

## Проверка аутентификации

```powershell
# Для HTTPS
git ls-remote origin

# Для SSH
ssh -T git@github.com
```

## Устранение проблем

### Очистка сохраненных credentials

```powershell
# Windows Credential Manager
cmdkey /list
cmdkey /delete:git:https://github.com

# Или через git
git credential-manager-core erase
```

### Принудительное обновление credentials

```powershell
git config --global credential.helper manager-core
git push -u origin main
# Введите username и PAT при запросе
```


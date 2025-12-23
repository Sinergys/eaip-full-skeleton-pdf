# Настройка GitHub токена для автоматического создания релизов

## Зачем нужен токен?

С GitHub токеном можно создавать релизы автоматически через скрипт, без ручного заполнения формы в браузере.

## Шаг 1: Создать Personal Access Token

1. Откройте: https://github.com/settings/tokens
2. Нажмите **"Generate new token"** → **"Generate new token (classic)"**
3. Заполните:
   - **Note**: `EAIP Release Script` (или любое название)
   - **Expiration**: выберите срок (например, 90 дней или No expiration)
   - **Scopes**: отметьте **`repo`** (это даст права на создание релизов)
4. Нажмите **"Generate token"**
5. **ВАЖНО!** Скопируйте токен сразу (он больше не будет показан!)

## Шаг 2: Установить токен

### Вариант А: Временный (для текущей сессии PowerShell)
```powershell
$env:GITHUB_TOKEN = "ваш_токен_здесь"
```

### Вариант Б: Постоянный (для всех сессий)
```powershell
# Установить для текущего пользователя
[System.Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "ваш_токен_здесь", "User")
```

После этого перезапустите PowerShell.

## Шаг 3: Создать релиз

```powershell
cd eaip_full_skeleton
pwsh -ExecutionPolicy Bypass -File .\create_release.ps1
```

## Альтернатива: GitHub CLI

Если предпочитаете GitHub CLI:

```powershell
# Авторизация (один раз)
gh auth login

# Создание релиза
gh release create v0.2.0 --title "Заголовок" --notes "Описание"
```

---

## Проверка токена

```powershell
if ($env:GITHUB_TOKEN) {
    Write-Host "✅ Токен установлен" -ForegroundColor Green
} else {
    Write-Host "❌ Токен не установлен" -ForegroundColor Red
}
```


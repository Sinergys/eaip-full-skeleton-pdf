# Быстрое создание релиза

## Для следующего релиза (v0.3.0, v0.4.0 и т.д.)

### Шаг 1: Обновите тег и информацию в `create_release.ps1`
Отредактируйте файл `create_release.ps1` и измените:
- `$tag = "v0.2.0"` → `$tag = "v0.3.0"` (или нужная версия)
- `$title = "..."` → ваш новый заголовок
- `$releaseNotes = @"...` → ваши release notes

### Шаг 2: Создайте тег и запушите
```powershell
git tag v0.3.0 -m "Описание версии"
git push origin v0.3.0
```

### Шаг 3: Запустите скрипт
```powershell
pwsh -ExecutionPolicy Bypass -File .\create_release.ps1
```

Готово! ✅ Релиз создан автоматически.

---

## Или через GitHub CLI (если авторизован)

```powershell
gh release create v0.3.0 --title "Заголовок" --notes "Описание"
```

---

## Токен уже сохранен!

Токен GitHub сохранен в переменной окружения `GITHUB_TOKEN` для вашего пользователя.

**Примечание:** Если скрипт не находит токен после перезапуска PowerShell, выполните:
```powershell
$env:GITHUB_TOKEN = [System.Environment]::GetEnvironmentVariable("GITHUB_TOKEN", "User")
```


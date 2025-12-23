# Инструкция: Создание релиза v0.2.0 на GitHub

## Вариант 1: Через веб-интерфейс GitHub (САМЫЙ ПРОСТОЙ)

1. Откройте в браузере: https://github.com/Sinergys/eaip-full-skeleton-pdf/releases/new

2. Заполните форму:
   - **Choose a tag**: выберите `v0.2.0` (должен быть в списке)
   - **Release title**: `EAIP Full Skeleton — Stable Cyrillic PDF Build`
   - **Description**: вставьте текст ниже

   ```
   ✅ Stable release v0.2.0

   What's new:

   - Added TTF font (DejaVuSans/Arial) for Cyrillic PDF generation
   - Improved reports service with full Unicode support
   - Added readiness check for reports (port 8005)
   - Updated analytics model with optional meterId
   - Updated documentation (README, CHANGELOG, PDF_GENERATION.md)
   - Cleaned up nested fonts and compose warnings
   ```

3. Нажмите кнопку **"Publish release"**

Готово! ✅

---

## Вариант 2: Через GitHub CLI (если авторизован)

1. Авторизуйтесь (если еще не авторизованы):
   ```powershell
   gh auth login
   ```
   - Выберите GitHub.com
   - Выберите HTTPS
   - Выберите "Login with a web browser"
   - Авторизуйтесь в браузере

2. Создайте релиз:
   ```powershell
   pwsh -ExecutionPolicy Bypass -File .\create_release.ps1
   ```

---

## Вариант 3: Через GitHub CLI напрямую

```powershell
gh release create v0.2.0 --title "EAIP Full Skeleton — Stable Cyrillic PDF Build" --notes "✅ Stable release v0.2.0

What's new:

- Added TTF font (DejaVuSans/Arial) for Cyrillic PDF generation
- Improved reports service with full Unicode support
- Added readiness check for reports (port 8005)
- Updated analytics model with optional meterId
- Updated documentation (README, CHANGELOG, PDF_GENERATION.md)
- Cleaned up nested fonts and compose warnings"
```


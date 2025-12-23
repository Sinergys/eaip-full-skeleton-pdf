# ⚡ БЫСТРЫЙ СТАРТ

## 🚀 Установка (1 команда)

```powershell
cd C:\eaip
.\install_word_validator.ps1
```

Скрипт автоматически:
- ✅ Создаст бэкап main.py
- ✅ Добавит новый endpoint
- ✅ Создаст документацию

## 📋 После установки

1. **Установить зависимость:**
```powershell
pip install python-docx
```

2. **Перезапустить сервис:**
```powershell
cd C:\eaip\eaip_full_skeleton\services\ingest
uvicorn main:app --reload --port 8001
```

3. **Протестировать:**
```powershell
cd C:\eaip
.\test_word_validator.ps1 -FilePath "C:\path\to\document.docx"
```

## ✅ Готово!

Endpoint: `POST /api/validate-word-document`
Проверяет: орфографию, структуру ПКМ-690, расчеты, соответствие нормативам

# ШАГ 3: БЫСТРЫЙ СТАРТ

**Проблема исправлена:** Скрипт больше не зависает на `input()`

---

## КАК ИСПОЛЬЗОВАТЬ

### Вариант 1: Указать файлы через аргументы командной строки

```bash
# Один файл
python tools/compare_recognition_results.py --manual "путь/к/файлу.json"

# Два файла (вариант 1 и вариант 2)
python tools/compare_recognition_results.py --manual1 "путь/к/вариант1.json" --manual2 "путь/к/вариант2.json"
```

---

### Вариант 2: Указать пути в чате

Просто напишите в чате:
```
Сравни с файлами:
- reports/ocr/manual_recognition_variant1.json
- reports/ocr/manual_recognition_variant2.json
```

И я запущу сравнение за вас.

---

## ФОРМАТ ФАЙЛОВ

Ваши файлы должны быть в формате JSON:

```json
{
  "tables": [
    {
      "rows": [
        ["№", "Колонка 1", "Колонка 2", ...],
        ["1", "Значение 1", "Значение 2", ...],
        ...
      ],
      "headers": ["№", "Колонка 1", "Колонка 2", ...]
    }
  ],
  "text": "Полный текст документа..."
}
```

---

## ГДЕ СОХРАНИТЬ ФАЙЛЫ

Рекомендуемые пути:
- `reports/ocr/manual_recognition_variant1.json`
- `reports/ocr/manual_recognition_variant2.json`

Или любой другой путь - просто укажите его при запуске.

---

## ЧТО ПОЛУЧИТЕ

После сравнения будут созданы:
- `reports/ocr/step3_comparison_вариант1.json` - детальный отчет в JSON
- `reports/ocr/step3_comparison_вариант1.md` - отчет в Markdown
- `reports/ocr/step3_comparison_summary.md` - сводный отчет (если несколько файлов)

---

**Готов к получению ваших файлов!** 🚀


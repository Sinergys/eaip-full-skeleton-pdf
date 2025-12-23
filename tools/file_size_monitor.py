"""Мониторинг размеров файлов контекста с периодической проверкой и отчётами"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.file_size_manager import check_all_context_files, check_file_size
from tools.context_loader import CRITICAL_FILES, OPTIONAL_FILES

HISTORY_FILE = PROJECT_ROOT / "docs" / "file_size_history.json"
REPORTS_DIR = PROJECT_ROOT / "reports" / "file_size_monitoring"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_history() -> Dict[str, Any]:
    """Загружает историю размеров файлов"""
    if not HISTORY_FILE.exists():
        return {
            "history": [],
            "last_check": None,
            "alerts": []
        }
    
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_history(data: Dict[str, Any]):
    """Сохраняет историю размеров файлов"""
    # Ограничиваем историю последними 100 записями
    if len(data.get("history", [])) > 100:
        data["history"] = data["history"][-100:]
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def record_file_sizes() -> Dict[str, Any]:
    """
    Записывает текущие размеры файлов в историю.
    
    Returns:
        Словарь с текущими размерами файлов
    """
    history_data = load_history()
    
    # Получаем текущие размеры
    current_check = {
        "timestamp": datetime.now().isoformat(),
        "files": {}
    }
    
    # Проверяем все файлы
    all_files = {**CRITICAL_FILES, **OPTIONAL_FILES}
    
    for key, file_path in all_files.items():
        if file_path.exists():
            file_info = check_file_size(file_path)
            current_check["files"][key] = {
                "path": str(file_path),
                "filename": file_path.name,
                "size_bytes": file_info["size_bytes"],
                "size_kb": file_info["size_kb"],
                "limit_bytes": file_info["limit_bytes"],
                "limit_kb": file_info["limit_kb"],
                "percentage_used": file_info["percentage_used"],
                "exceeds_limit": file_info["exceeds_limit"],
                "category": "critical" if key in CRITICAL_FILES else "optional"
            }
    
    # Добавляем в историю
    if "history" not in history_data:
        history_data["history"] = []
    
    history_data["history"].append(current_check)
    history_data["last_check"] = datetime.now().isoformat()
    
    # Сохраняем историю
    save_history(history_data)
    
    return current_check


def analyze_growth(period_days: int = 7) -> Dict[str, Any]:
    """
    Анализирует рост файлов за указанный период.
    
    Args:
        period_days: Количество дней для анализа
    
    Returns:
        Словарь с анализом роста
    """
    history_data = load_history()
    
    if not history_data.get("history"):
        return {
            "period_days": period_days,
            "analysis_date": datetime.now().isoformat(),
            "files_analyzed": 0,
            "growth": {}
        }
    
    # Фильтруем записи за период
    cutoff_date = datetime.now() - timedelta(days=period_days)
    recent_history = [
        entry for entry in history_data["history"]
        if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
    ]
    
    if len(recent_history) < 2:
        return {
            "period_days": period_days,
            "analysis_date": datetime.now().isoformat(),
            "files_analyzed": 0,
            "growth": {},
            "message": "Недостаточно данных для анализа (нужно минимум 2 записи)"
        }
    
    # Анализируем рост для каждого файла
    first_check = recent_history[0]
    last_check = recent_history[-1]
    
    growth_analysis = {}
    
    for file_key in first_check["files"]:
        if file_key not in last_check["files"]:
            continue
        
        first_size = first_check["files"][file_key]["size_bytes"]
        last_size = last_check["files"][file_key]["size_bytes"]
        
        size_diff = last_size - first_size
        size_diff_kb = round(size_diff / 1024, 2)
        percent_change = round((size_diff / first_size * 100) if first_size > 0 else 0, 2)
        
        growth_analysis[file_key] = {
            "filename": first_check["files"][file_key]["filename"],
            "first_size_kb": first_check["files"][file_key]["size_kb"],
            "last_size_kb": last_check["files"][file_key]["size_kb"],
            "growth_kb": size_diff_kb,
            "growth_percent": percent_change,
            "category": first_check["files"][file_key]["category"],
            "trend": "increasing" if size_diff > 0 else "decreasing" if size_diff < 0 else "stable"
        }
    
    return {
        "period_days": period_days,
        "analysis_date": datetime.now().isoformat(),
        "files_analyzed": len(growth_analysis),
        "growth": growth_analysis,
        "first_check": first_check["timestamp"],
        "last_check": last_check["timestamp"]
    }


def check_alerts() -> List[Dict[str, Any]]:
    """
    Проверяет условия для алертов и возвращает список активных алертов.
    
    Returns:
        Список активных алертов
    """
    alerts = []
    current_check = record_file_sizes()
    
    # Проверяем каждый файл
    for file_key, file_data in current_check["files"].items():
        # Алерт 1: Превышение лимита
        if file_data["exceeds_limit"]:
            alerts.append({
                "type": "exceeds_limit",
                "severity": "critical",
                "file_key": file_key,
                "filename": file_data["filename"],
                "size_kb": file_data["size_kb"],
                "limit_kb": file_data["limit_kb"],
                "percentage_used": file_data["percentage_used"],
                "timestamp": current_check["timestamp"],
                "message": f"Файл {file_data['filename']} превышает лимит: {file_data['size_kb']} КБ / {file_data['limit_kb']} КБ ({file_data['percentage_used']:.1f}%)"
            })
        
        # Алерт 2: Приближение к лимиту (>90%)
        elif file_data["percentage_used"] > 90:
            alerts.append({
                "type": "approaching_limit",
                "severity": "warning",
                "file_key": file_key,
                "filename": file_data["filename"],
                "size_kb": file_data["size_kb"],
                "limit_kb": file_data["limit_kb"],
                "percentage_used": file_data["percentage_used"],
                "timestamp": current_check["timestamp"],
                "message": f"Файл {file_data['filename']} близок к лимиту: {file_data['size_kb']} КБ / {file_data['limit_kb']} КБ ({file_data['percentage_used']:.1f}%)"
            })
        
        # Алерт 3: Быстрый рост (>50% за неделю)
        growth_analysis = analyze_growth(period_days=7)
        if file_key in growth_analysis.get("growth", {}):
            growth = growth_analysis["growth"][file_key]
            if growth["growth_percent"] > 50:
                alerts.append({
                    "type": "rapid_growth",
                    "severity": "warning",
                    "file_key": file_key,
                    "filename": file_data["filename"],
                    "growth_percent": growth["growth_percent"],
                    "growth_kb": growth["growth_kb"],
                    "period_days": 7,
                    "timestamp": current_check["timestamp"],
                    "message": f"Файл {file_data['filename']} быстро растёт: +{growth['growth_percent']:.1f}% за 7 дней (+{growth['growth_kb']} КБ)"
                })
    
    # Сохраняем алерты в историю
    history_data = load_history()
    history_data["alerts"] = alerts
    save_history(history_data)
    
    return alerts


def get_disk_usage_metrics() -> Dict[str, Any]:
    """
    Получает метрики использования дискового пространства.
    
    Returns:
        Словарь с метриками использования дискового пространства
    """
    import shutil
    
    # Получаем информацию о диске
    disk_usage = shutil.disk_usage(PROJECT_ROOT)
    
    # Получаем размеры всех контекстных файлов
    all_files = {**CRITICAL_FILES, **OPTIONAL_FILES}
    total_context_size = 0
    
    for file_path in all_files.values():
        if file_path.exists():
            total_context_size += file_path.stat().st_size
    
    # Размер истории
    history_size = HISTORY_FILE.stat().st_size if HISTORY_FILE.exists() else 0
    
    # Размер архивов
    archive_size = 0
    if (PROJECT_ROOT / "docs" / "archive").exists():
        for archive_file in (PROJECT_ROOT / "docs" / "archive").rglob("*"):
            if archive_file.is_file():
                archive_size += archive_file.stat().st_size
    
    # Размер отчётов мониторинга
    reports_size = 0
    if REPORTS_DIR.exists():
        for report_file in REPORTS_DIR.rglob("*"):
            if report_file.is_file():
                reports_size += report_file.stat().st_size
    
    total_context_related = total_context_size + history_size + archive_size + reports_size
    
    return {
        "timestamp": datetime.now().isoformat(),
        "disk_total_gb": round(disk_usage.total / (1024**3), 2),
        "disk_used_gb": round(disk_usage.used / (1024**3), 2),
        "disk_free_gb": round(disk_usage.free / (1024**3), 2),
        "disk_usage_percent": round((disk_usage.used / disk_usage.total) * 100, 2),
        "context_files_size_kb": round(total_context_size / 1024, 2),
        "history_size_kb": round(history_size / 1024, 2),
        "archive_size_kb": round(archive_size / 1024, 2),
        "reports_size_kb": round(reports_size / 1024, 2),
        "total_context_related_kb": round(total_context_related / 1024, 2),
        "context_usage_percent_of_disk": round((total_context_related / disk_usage.total) * 100, 6)
    }


def generate_report() -> Path:
    """
    Генерирует отчёт о размерах файлов и сохраняет в reports/file_size_monitoring/
    
    Returns:
        Путь к созданному отчёту
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"file_size_report_{timestamp}.json"
    
    # Получаем текущие размеры
    current_check = record_file_sizes()
    
    # Анализируем рост
    growth_7d = analyze_growth(period_days=7)
    growth_30d = analyze_growth(period_days=30)
    
    # Проверяем алерты
    alerts = check_alerts()
    
    # Получаем метрики дискового пространства
    disk_metrics = get_disk_usage_metrics()
    
    # Формируем отчёт
    report = {
        "report_date": datetime.now().isoformat(),
        "current_sizes": current_check,
        "growth_analysis_7d": growth_7d,
        "growth_analysis_30d": growth_30d,
        "alerts": alerts,
        "disk_metrics": disk_metrics,
        "summary": {
            "total_files": len(current_check["files"]),
            "files_exceeding_limit": sum(1 for f in current_check["files"].values() if f["exceeds_limit"]),
            "files_approaching_limit": sum(1 for f in current_check["files"].values() if 90 < f["percentage_used"] <= 100),
            "active_alerts": len(alerts),
            "critical_alerts": sum(1 for a in alerts if a["severity"] == "critical"),
            "warning_alerts": sum(1 for a in alerts if a["severity"] == "warning"),
            "total_context_size_kb": disk_metrics["total_context_related_kb"],
            "disk_usage_percent": disk_metrics["disk_usage_percent"]
        }
    }
    
    # Сохраняем отчёт
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report_path


if __name__ == "__main__":
    print("=" * 70)
    print("МОНИТОРИНГ РАЗМЕРОВ ФАЙЛОВ КОНТЕКСТА")
    print("=" * 70)
    
    # Записываем текущие размеры
    print("\n1. Запись текущих размеров файлов...")
    current_check = record_file_sizes()
    print(f"✅ Записано {len(current_check['files'])} файлов")
    
    # Анализируем рост
    print("\n2. Анализ роста файлов за 7 дней...")
    growth_7d = analyze_growth(period_days=7)
    if growth_7d.get("files_analyzed", 0) > 0:
        print(f"✅ Проанализировано {growth_7d['files_analyzed']} файлов")
        for file_key, growth_data in growth_7d["growth"].items():
            trend_icon = "📈" if growth_data["trend"] == "increasing" else "📉" if growth_data["trend"] == "decreasing" else "➡️"
            print(f"   {trend_icon} {growth_data['filename']}: {growth_data['growth_kb']:+.2f} КБ ({growth_data['growth_percent']:+.2f}%)")
    else:
        print(f"⚠️ {growth_7d.get('message', 'Недостаточно данных')}")
    
    # Проверяем алерты
    print("\n3. Проверка алертов...")
    alerts = check_alerts()
    if alerts:
        print(f"⚠️ Найдено {len(alerts)} алертов:")
        for alert in alerts:
            severity_icon = "🔴" if alert["severity"] == "critical" else "🟡"
            print(f"   {severity_icon} {alert['message']}")
    else:
        print("✅ Алертов не обнаружено")
    
    # Генерируем отчёт
    print("\n4. Генерация отчёта...")
    report_path = generate_report()
    print(f"✅ Отчёт сохранён: {report_path}")
    
    # Получаем метрики дискового пространства
    print("\n5. Метрики использования дискового пространства...")
    disk_metrics = get_disk_usage_metrics()
    print(f"✅ Диск: {disk_metrics['disk_used_gb']} ГБ / {disk_metrics['disk_total_gb']} ГБ ({disk_metrics['disk_usage_percent']}%)")
    print(f"   Контекстные файлы: {disk_metrics['total_context_related_kb']} КБ")
    print(f"   - Файлы: {disk_metrics['context_files_size_kb']} КБ")
    print(f"   - История: {disk_metrics['history_size_kb']} КБ")
    print(f"   - Архивы: {disk_metrics['archive_size_kb']} КБ")
    print(f"   - Отчёты: {disk_metrics['reports_size_kb']} КБ")
    
    # Выводим сводку
    print("\n" + "=" * 70)
    print("СВОДКА")
    print("=" * 70)
    print(f"Всего файлов: {len(current_check['files'])}")
    print(f"Превышают лимит: {sum(1 for f in current_check['files'].values() if f['exceeds_limit'])}")
    print(f"Активных алертов: {len(alerts)}")
    print(f"Использование диска: {disk_metrics['disk_usage_percent']}%")
    print("=" * 70)


"""Анализ файлов для чтения при старте работы агентов"""
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[0].parent
DOCS_DIR = PROJECT_ROOT / "docs"

FILES_TO_ANALYZE = [
    "AGENT_CONTEXT.json",
    "AGENT_KNOWLEDGE_BASE.md",
    "PROJECT_CRITICAL_SETTINGS.md",
    "AGENT_SESSION_STATE.json",
    "AGENT_TASK_STATUS.json",
    "AGENT_LOCKS.json",
    "AGENT_TASKS_UNIFIED.json"
]

def analyze_files():
    """Анализирует файлы для чтения при старте"""
    results = {
        "analysis_date": datetime.now().isoformat(),
        "files": [],
        "total_size_bytes": 0,
        "total_size_kb": 0,
        "categories": {
            "critical": [],
            "important": [],
            "optional": []
        }
    }
    
    for filename in FILES_TO_ANALYZE:
        filepath = DOCS_DIR / filename
        if filepath.exists():
            size = filepath.stat().st_size
            results["total_size_bytes"] += size
            results["total_size_kb"] += size / 1024
            
            file_info = {
                "filename": filename,
                "path": str(filepath),
                "size_bytes": size,
                "size_kb": round(size / 1024, 2),
                "exists": True
            }
            
            # Категоризация
            if filename in ["AGENT_CONTEXT.json", "AGENT_TASKS_UNIFIED.json"]:
                file_info["category"] = "critical"
                file_info["reason"] = "Критически необходим для работы агентов"
                results["categories"]["critical"].append(filename)
            elif filename in ["AGENT_TASK_STATUS.json", "AGENT_LOCKS.json", "AGENT_SESSION_STATE.json"]:
                file_info["category"] = "important"
                file_info["reason"] = "Важен для синхронизации и состояния"
                results["categories"]["important"].append(filename)
            else:
                file_info["category"] = "optional"
                file_info["reason"] = "Может быть загружен по требованию"
                results["categories"]["optional"].append(filename)
            
            results["files"].append(file_info)
        else:
            results["files"].append({
                "filename": filename,
                "exists": False
            })
    
    results["total_size_kb"] = round(results["total_size_kb"], 2)
    results["total_size_mb"] = round(results["total_size_kb"] / 1024, 2)
    
    return results

if __name__ == "__main__":
    analysis = analyze_files()
    
    print("=" * 70)
    print("АНАЛИЗ ФАЙЛОВ ДЛЯ ЧТЕНИЯ ПРИ СТАРТЕ РАБОТЫ АГЕНТОВ")
    print("=" * 70)
    print(f"\nДата анализа: {analysis['analysis_date']}")
    print(f"\nВсего файлов: {len(analysis['files'])}")
    print(f"Общий размер: {analysis['total_size_bytes']:,} байт ({analysis['total_size_kb']:.2f} КБ, {analysis['total_size_mb']:.2f} МБ)")
    
    print("\n" + "=" * 70)
    print("КРИТИЧЕСКИЕ (обязательные):")
    print("=" * 70)
    for filename in analysis["categories"]["critical"]:
        file_info = next(f for f in analysis["files"] if f["filename"] == filename)
        print(f"  ✅ {filename:40} {file_info['size_kb']:>8.2f} КБ - {file_info['reason']}")
    
    print("\n" + "=" * 70)
    print("ВАЖНЫЕ (рекомендуемые):")
    print("=" * 70)
    for filename in analysis["categories"]["important"]:
        file_info = next(f for f in analysis["files"] if f["filename"] == filename)
        print(f"  ⚠️  {filename:40} {file_info['size_kb']:>8.2f} КБ - {file_info['reason']}")
    
    print("\n" + "=" * 70)
    print("ОПЦИОНАЛЬНЫЕ (по требованию):")
    print("=" * 70)
    for filename in analysis["categories"]["optional"]:
        file_info = next(f for f in analysis["files"] if f["filename"] == filename)
        print(f"  💡 {filename:40} {file_info['size_kb']:>8.2f} КБ - {file_info['reason']}")
    
    # Сохранить результаты
    output_file = PROJECT_ROOT / "reports" / "startup_files_analysis.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Результаты сохранены: {output_file}")


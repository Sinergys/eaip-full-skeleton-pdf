"""Тестирование улучшенной классификации ресурсов"""
import sys
from pathlib import Path

# Добавляем родительскую директорию в sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.resource_classifier import ResourceClassifier

# Тестовые файлы (примеры проблемных названий)
TEST_FILES = [
    ("ЦЦР паспорт здании.xlsx", "envelope"),
    ("паспорт зданий.xlsx", "envelope"),
    ("pererashod.xlsx", "electricity"),
    ("gaz.xlsx", "gas"),
    ("voda.xlsx", "water"),
    ("schetchiki.xlsx", "nodes"),
    ("оборудование.xlsx", "equipment"),
    ("otoplenie.xlsx", "heat"),
    ("мазут.xlsx", "fuel"),
    ("уголь.xlsx", "coal"),
    ("энергопаспорт.xlsx", "other"),  # Должен быть other, так как это не ресурс
    ("реализация электроэнергии.xlsx", "electricity"),
    ("акт баланса.xlsx", "electricity"),
    ("коммерческий учет.xlsx", "electricity"),
]


def test_classification():
    """Тестирует классификацию файлов по именам"""
    print("=" * 70)
    print("🧪 ТЕСТИРОВАНИЕ КЛАССИФИКАЦИИ РЕСУРСОВ")
    print("=" * 70)
    print()

    passed = 0
    failed = 0
    results = []

    for filename, expected_type in TEST_FILES:
        # Тестируем только по имени файла (без содержимого)
        result_type = ResourceClassifier.classify(filename, None)
        result_type_with_confidence, confidence = ResourceClassifier.classify_with_confidence(
            filename, None
        )

        is_correct = result_type == expected_type
        status = "✅" if is_correct else "❌"

        if is_correct:
            passed += 1
        else:
            failed += 1

        results.append(
            {
                "filename": filename,
                "expected": expected_type,
                "got": result_type,
                "confidence": confidence,
                "correct": is_correct,
            }
        )

        print(
            f"{status} {filename:40} → Ожидалось: {expected_type:12} "
            f"Получено: {result_type:12} (уверенность: {confidence:.2f})"
        )

    print()
    print("=" * 70)
    print(f"📊 РЕЗУЛЬТАТЫ: {passed} успешно, {failed} ошибок из {len(TEST_FILES)}")
    print("=" * 70)

    if failed > 0:
        print("\n❌ ОШИБКИ КЛАССИФИКАЦИИ:")
        for result in results:
            if not result["correct"]:
                print(
                    f"  - {result['filename']}: ожидалось '{result['expected']}', "
                    f"получено '{result['got']}'"
                )

    return failed == 0


if __name__ == "__main__":
    success = test_classification()
    sys.exit(0 if success else 1)


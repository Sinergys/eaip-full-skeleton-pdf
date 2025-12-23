"""
Конфигурация шаблонов энергопаспортов
Мэппинг имен шаблонов к путям файлов
"""
from pathlib import Path
from typing import Dict, Optional

# Базовый путь к директории шаблонов
TEMPLATES_DIR = Path(__file__).parent

# Мэппинг имен шаблонов к путям файлов
TEMPLATE_MAPPING: Dict[str, Path] = {
    # Старый шаблон (Metin)
    "metin": TEMPLATES_DIR / "metin.xlsx",
    "template_metin": TEMPLATES_DIR / "metin.xlsx",
    
    # Новый шаблон
    "new_energy_passport": TEMPLATES_DIR / "new_energy_passport.xlsx",
    "new": TEMPLATES_DIR / "new_energy_passport.xlsx",
    
    # Дефолтный шаблон (для обратной совместимости)
    "default": TEMPLATES_DIR / "energy_passport_template.xlsx",
    "energy_passport_template": TEMPLATES_DIR / "energy_passport_template.xlsx",
}


def get_template_path(template_name: Optional[str] = None) -> Path:
    """
    Получить путь к шаблону по имени
    
    Args:
        template_name: Имя шаблона (например, "new_energy_passport", "metin", "default")
                      Если None, возвращается дефолтный шаблон
    
    Returns:
        Path к файлу шаблона
    
    Raises:
        FileNotFoundError: Если шаблон не найден
        ValueError: Если имя шаблона не существует в мэппинге
    """
    if template_name is None:
        template_name = "default"
    
    # Нормализация имени (lowercase, без пробелов)
    template_name = template_name.lower().strip()
    
    # Поиск в мэппинге
    if template_name not in TEMPLATE_MAPPING:
        available = ", ".join(TEMPLATE_MAPPING.keys())
        raise ValueError(
            f"Шаблон '{template_name}' не найден. "
            f"Доступные шаблоны: {available}"
        )
    
    template_path = TEMPLATE_MAPPING[template_name]
    
    # Проверка существования файла
    if not template_path.exists():
        raise FileNotFoundError(
            f"Файл шаблона не найден: {template_path}\n"
            f"Проверьте, что файл существует в директории {TEMPLATES_DIR}"
        )
    
    return template_path


def list_available_templates() -> Dict[str, str]:
    """
    Получить список доступных шаблонов
    
    Returns:
        Словарь {имя_шаблона: путь_к_файлу}
    """
    available = {}
    for name, path in TEMPLATE_MAPPING.items():
        if path.exists():
            available[name] = str(path)
    
    return available


def register_template(name: str, file_path: str) -> None:
    """
    Зарегистрировать новый шаблон
    
    Args:
        name: Имя шаблона
        file_path: Путь к файлу шаблона (может быть абсолютным или относительным)
    
    Raises:
        FileNotFoundError: Если файл не существует
        ValueError: Если имя уже используется
    """
    path = Path(file_path)
    
    # Если путь относительный, считаем относительно директории шаблонов
    if not path.is_absolute():
        path = TEMPLATES_DIR / path
    
    if not path.exists():
        raise FileNotFoundError(f"Файл шаблона не найден: {path}")
    
    name_lower = name.lower().strip()
    if name_lower in TEMPLATE_MAPPING:
        raise ValueError(f"Шаблон с именем '{name}' уже зарегистрирован")
    
    TEMPLATE_MAPPING[name_lower] = path


# Дефолтный шаблон для обратной совместимости
DEFAULT_TEMPLATE = "default"


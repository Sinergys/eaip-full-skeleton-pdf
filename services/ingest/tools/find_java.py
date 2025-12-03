"""
Скрипт для поиска Java в системе Windows
Проверяет стандартные пути установки и переменные окружения
"""

import os
import subprocess
import shutil
from pathlib import Path
import winreg

def check_java_in_path():
    """Проверяет наличие java в PATH"""
    java_path = shutil.which("java")
    if java_path:
        try:
            result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Java выводит версию в stderr, а не stdout
            if result.returncode == 0:
                return java_path, result.stdout or result.stderr
        except Exception as e:
            print(f"Ошибка при проверке java в PATH: {e}")
    return None, None

def check_java_home():
    """Проверяет переменную окружения JAVA_HOME"""
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        java_exe = Path(java_home) / "bin" / "java.exe"
        if java_exe.exists():
            try:
                result = subprocess.run(
                    [str(java_exe), "-version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    stderr=subprocess.STDOUT
                )
                if result.returncode == 0:
                    return str(java_exe), result.stdout or result.stderr
            except Exception as e:
                print(f"Ошибка при проверке JAVA_HOME: {e}")
    return None, None

def check_standard_paths():
    """Проверяет стандартные пути установки Java на Windows"""
    standard_paths = [
        Path("C:/Program Files/Java"),
        Path("C:/Program Files (x86)/Java"),
        Path("C:/Program Files/Amazon Corretto"),
        Path("C:/Program Files/Microsoft"),
        Path("C:/Program Files/AdoptOpenJDK"),
        Path("C:/Program Files/Eclipse Adoptium"),
        Path(os.path.expanduser("~/AppData/Local/Programs/Java")),
    ]
    
    found_java = []
    
    for base_path in standard_paths:
        if not base_path.exists():
            continue
            
        # Ищем подпапки с Java
        for item in base_path.iterdir():
            if item.is_dir():
                java_exe = item / "bin" / "java.exe"
                if java_exe.exists():
                    try:
                        result = subprocess.run(
                            [str(java_exe), "-version"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            # Java выводит версию в stderr
                            version_info = result.stderr or result.stdout
                            found_java.append({
                                "path": str(java_exe),
                                "home": str(item),
                                "version": version_info.split("\n")[0] if version_info else "unknown"
                            })
                    except Exception as e:
                        print(f"Ошибка при проверке {java_exe}: {e}")
    
    return found_java

def check_registry():
    """Проверяет реестр Windows на наличие Java"""
    java_installations = []
    
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\Java Runtime Environment"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\JavaSoft\Java Runtime Environment"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\Java Development Kit"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\JavaSoft\Java Development Kit"),
    ]
    
    for hkey, path in registry_paths:
        try:
            key = winreg.OpenKey(hkey, path)
            try:
                i = 0
                while True:
                    try:
                        version_key_name = winreg.EnumKey(key, i)
                        version_key = winreg.OpenKey(key, version_key_name)
                        try:
                            java_home = winreg.QueryValueEx(version_key, "JavaHome")[0]
                            java_exe = Path(java_home) / "bin" / "java.exe"
                            if java_exe.exists():
                                java_installations.append({
                                    "path": str(java_exe),
                                    "home": java_home,
                                    "version": version_key_name,
                                    "source": "registry"
                                })
                        finally:
                            winreg.CloseKey(version_key)
                        i += 1
                    except OSError:
                        break
            finally:
                winreg.CloseKey(key)
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Ошибка при чтении реестра {path}: {e}")
    
    return java_installations

def main():
    print("=" * 70)
    print("🔍 ПОИСК JAVA В СИСТЕМЕ")
    print("=" * 70)
    print()
    
    # 1. Проверка в PATH
    print("1️⃣ Проверка java в PATH...")
    java_path, version_output = check_java_in_path()
    if java_path:
        print(f"   ✅ Найдена в PATH: {java_path}")
        if version_output:
            print(f"   Версия: {version_output.split(chr(10))[0]}")
    else:
        print("   ❌ Java не найдена в PATH")
    print()
    
    # 2. Проверка JAVA_HOME
    print("2️⃣ Проверка переменной JAVA_HOME...")
    java_home_path, version_output = check_java_home()
    if java_home_path:
        print(f"   ✅ Найдена через JAVA_HOME: {java_home_path}")
        print(f"   JAVA_HOME = {os.environ.get('JAVA_HOME')}")
        if version_output:
            print(f"   Версия: {version_output.split(chr(10))[0]}")
    else:
        print("   ❌ JAVA_HOME не установлена или неверна")
        if os.environ.get("JAVA_HOME"):
            print(f"   (JAVA_HOME установлена, но java.exe не найден: {os.environ.get('JAVA_HOME')})")
    print()
    
    # 3. Проверка стандартных путей
    print("3️⃣ Проверка стандартных путей установки...")
    found_in_paths = check_standard_paths()
    if found_in_paths:
        print(f"   ✅ Найдено установок: {len(found_in_paths)}")
        for i, java in enumerate(found_in_paths, 1):
            print(f"   {i}. {java['path']}")
            print(f"      Home: {java['home']}")
            print(f"      Версия: {java.get('version', 'unknown')}")
    else:
        print("   ❌ Java не найдена в стандартных путях")
    print()
    
    # 4. Проверка реестра
    print("4️⃣ Проверка реестра Windows...")
    found_in_registry = check_registry()
    if found_in_registry:
        print(f"   ✅ Найдено в реестре: {len(found_in_registry)}")
        for i, java in enumerate(found_in_registry, 1):
            print(f"   {i}. {java['path']}")
            print(f"      Home: {java['home']}")
            print(f"      Версия: {java.get('version', 'unknown')}")
    else:
        print("   ❌ Java не найдена в реестре")
    print()
    
    # Итоги
    print("=" * 70)
    print("📊 ИТОГИ")
    print("=" * 70)
    
    all_found = []
    if java_path:
        all_found.append({"path": java_path, "source": "PATH"})
    if java_home_path and java_home_path != java_path:
        all_found.append({"path": java_home_path, "source": "JAVA_HOME"})
    for java in found_in_paths:
        if java["path"] not in [j["path"] for j in all_found]:
            all_found.append({"path": java["path"], "source": "standard_paths"})
    for java in found_in_registry:
        if java["path"] not in [j["path"] for j in all_found]:
            all_found.append({"path": java["path"], "source": "registry"})
    
    if all_found:
        print(f"✅ Всего найдено установок Java: {len(all_found)}")
        for i, java in enumerate(all_found, 1):
            print(f"   {i}. {java['path']} (источник: {java['source']})")
        print()
        print("💡 Рекомендация: Добавьте путь к bin в переменную PATH или установите JAVA_HOME")
    else:
        print("❌ Java не найдена в системе")
        print()
        print("📋 Для установки Java:")
        print("   Windows: https://www.java.com/download/")
        print("   Или через Chocolatey: choco install openjdk")
        print("   Или через winget: winget install Microsoft.OpenJDK.17")
    
    print("=" * 70)

if __name__ == "__main__":
    main()


# 📋 Руководство по установке Java для Tabula

**Дата создания:** 2025-12-01  
**Назначение:** Инструкции по установке Java Runtime Environment (JRE) для использования Tabula в системе извлечения таблиц из PDF

---

## 🔍 Проверка наличия Java

Перед установкой проверьте, установлена ли уже Java:

```bash
java -version
```

Если Java установлена, вы увидите информацию о версии:
```
openjdk version "17.0.1" 2021-10-19
OpenJDK Runtime Environment (build 17.0.1+12-Ubuntu-120.04)
OpenJDK 64-Bit Server VM (build 17.0.1+12-Ubuntu-120.04, mixed mode, sharing)
```

Если команда не найдена, Java не установлена.

---

## 🪟 Windows

### Вариант 1: Установка через официальный сайт (рекомендуется)

1. Перейдите на https://www.java.com/download/
2. Скачайте Java для Windows
3. Запустите установщик и следуйте инструкциям
4. Перезапустите терминал/PowerShell
5. Проверьте установку: `java -version`

### Вариант 2: Установка через Chocolatey

Если у вас установлен Chocolatey:

```powershell
choco install openjdk
```

Или для конкретной версии:

```powershell
choco install openjdk17
```

### Вариант 3: Установка через winget

```powershell
winget install Microsoft.OpenJDK.17
```

### Проверка установки

```powershell
java -version
```

---

## 🐧 Linux

### Ubuntu/Debian

```bash
# Обновление списка пакетов
sudo apt-get update

# Установка OpenJDK (JRE)
sudo apt-get install default-jre

# Или для конкретной версии
sudo apt-get install openjdk-17-jre
```

### CentOS/RHEL/Fedora

```bash
# Fedora
sudo dnf install java-17-openjdk

# CentOS/RHEL
sudo yum install java-17-openjdk
```

### Проверка установки

```bash
java -version
```

---

## 🍎 macOS

### Вариант 1: Установка через Homebrew (рекомендуется)

```bash
# Установка OpenJDK
brew install openjdk

# Или для конкретной версии
brew install openjdk@17
```

После установки может потребоваться добавить в PATH:

```bash
echo 'export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Вариант 2: Установка через официальный сайт

1. Перейдите на https://www.java.com/download/
2. Скачайте Java для macOS
3. Запустите установщик
4. Проверьте установку: `java -version`

### Проверка установки

```bash
java -version
```

---

## 🔧 Настройка переменных окружения (если необходимо)

Если Java установлена, но команда `java` не найдена, возможно, нужно добавить Java в PATH.

### Windows

1. Найдите путь к Java (обычно `C:\Program Files\Java\jre-<version>\bin`)
2. Добавьте путь в переменную окружения PATH:
   - Откройте "Система" → "Дополнительные параметры системы"
   - Нажмите "Переменные среды"
   - В "Системные переменные" найдите `Path` и добавьте путь к `bin`

### Linux/macOS

Добавьте в `~/.bashrc` или `~/.zshrc`:

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64  # Путь может отличаться
export PATH=$JAVA_HOME/bin:$PATH
```

Затем перезагрузите терминал:

```bash
source ~/.bashrc  # или source ~/.zshrc
```

---

## ✅ Проверка работы Tabula

После установки Java перезапустите сервис ingest и проверьте логи:

```bash
# В логах должно появиться:
✅ Tabula доступен: Java <версия> установлена
```

Или проверьте программно:

```python
from eaip_full_skeleton.services.ingest.utils.table_detector import check_dependencies

deps = check_dependencies()
print(f"Tabula доступен: {deps['tabula_usable']}")
print(f"Java информация: {deps['java']}")
```

---

## 🐛 Решение проблем

### Проблема: Java установлена, но не найдена

**Решение:**
1. Проверьте, что Java добавлена в PATH
2. Перезапустите терминал/сервис
3. Проверьте версию: `java -version`

### Проблема: Несколько версий Java

**Решение:**
1. Установите одну версию (рекомендуется Java 11 или выше)
2. Удалите старые версии или настройте `JAVA_HOME`

### Проблема: Tabula всё ещё не работает

**Решение:**
1. Убедитесь, что Java установлена: `java -version`
2. Перезапустите Python-процесс/сервис
3. Проверьте логи на наличие ошибок

---

## 📚 Дополнительная информация

- **Официальный сайт Java:** https://www.java.com/
- **OpenJDK:** https://openjdk.org/
- **Tabula-py документация:** https://github.com/chezou/tabula-py

---

## 💡 Примечания

- Tabula не является критически важным компонентом — система работает с альтернативными методами (pdfplumber, camelot)
- Установка Java рекомендуется для улучшения качества извлечения таблиц из сложных PDF
- Минимальная версия Java: 8 (рекомендуется 11 или выше)

---

---

## ✅ УСТАНОВКА ЗАВЕРШЕНА (2025-12-01)

**Установленная версия:** Microsoft OpenJDK 17.0.17 (LTS)  
**Путь установки:** `C:\Program Files\Microsoft\jdk-17.0.17.10-hotspot`  
**Статус:** ✅ Java доступна, Tabula готов к работе

**Проверка:**
```bash
java -version
# openjdk version "17.0.17" 2025-10-21 LTS
```

---

**Статус:** ✅ Готово к использованию  
**Последнее обновление:** 2025-12-01


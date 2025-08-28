# 🔨 Сборка EXE файла для парсера

## 📋 Описание

Этот раздел описывает, как упаковать парсер в один EXE файл, который будет работать без установки Python.

## 🚀 Способы сборки

### Способ 1: Автоматическая сборка (рекомендуется)

#### На Windows:
```bash
# Двойной клик на файл
build_exe_simple.bat
```

#### На Linux/Mac:
```bash
python3 build_exe.py
```

### Способ 2: Ручная сборка

```bash
# 1. Установка PyInstaller
pip install pyinstaller

# 2. Сборка EXE
pyinstaller --onefile --name=NovaskladParser parser-requests.py

# 3. EXE файл будет в папке dist/
```

## 📁 Файлы для сборки

- `build_exe.py` - Python скрипт для сборки
- `build_exe_simple.bat` - BAT файл для Windows
- `parser-requests.py` - основной парсер
- `requirements-requests.txt` - зависимости

## ⚙️ Параметры сборки

### Основные параметры:
- `--onefile` - один EXE файл
- `--name=NovaskladParser` - имя EXE файла
- `--windowed` - без консольного окна (для GUI)

### Скрытые импорты:
- `--hidden-import=rich.console` - Rich библиотека
- `--hidden-import=pandas` - Pandas для Excel
- `--hidden-import=openpyxl` - OpenPyXL для Excel
- `--hidden-import=bs4` - BeautifulSoup для парсинга
- `--hidden-import=lxml` - LXML парсер

## 🔧 Требования для сборки

### Системные требования:
- Python 3.7+
- pip (менеджер пакетов)
- Достаточно места на диске (2-3 ГБ)

### Python пакеты:
- pyinstaller
- requests
- beautifulsoup4
- pandas
- openpyxl
- rich
- lxml

## 📊 Результат сборки

После успешной сборки вы получите:

### Файлы:
- `NovaskladParser.exe` - основной EXE файл
- `dist/NovaskladParser.exe` - копия в папке dist

### Размер:
- Обычно 50-150 МБ
- Зависит от количества библиотек

## 🚨 Возможные проблемы

### Ошибка "Python не найден":
```bash
# Добавьте Python в PATH или используйте полный путь
C:\Python39\python.exe build_exe_simple.bat
```

### Ошибка "Module not found":
```bash
# Установите недостающие пакеты
pip install requests beautifulsoup4 pandas openpyxl rich lxml
```

### Большой размер EXE:
```bash
# Используйте --exclude-module для исключения ненужных модулей
pyinstaller --onefile --exclude-module=matplotlib --exclude-module=numpy parser-requests.py
```

## 💡 Оптимизация

### Уменьшение размера:
```bash
# Исключаем ненужные модули
pyinstaller --onefile \
  --exclude-module=matplotlib \
  --exclude-module=numpy \
  --exclude-module=scipy \
  --exclude-module=tkinter \
  parser-requests.py
```

### Ускорение запуска:
```bash
# Сборка в папку (не один файл)
pyinstaller --name=NovaskladParser parser-requests.py
```

## 🎯 Использование готового EXE

### Запуск:
```bash
# Двойной клик на файл или
NovaskladParser.exe
```

### Распространение:
- Скопируйте `NovaskladParser.exe` на любой компьютер
- Работает без установки Python
- Требует только Windows

## 🔍 Отладка сборки

### Подробный вывод:
```bash
pyinstaller --onefile --debug=all parser-requests.py
```

### Проверка зависимостей:
```bash
# Анализ зависимостей
pyi-bindepend parser-requests.py
```

### Логи сборки:
```bash
# Логи сохраняются в build/ и dist/
```

## 📚 Дополнительные ресурсы

- [PyInstaller документация](https://pyinstaller.readthedocs.io/)
- [PyInstaller GitHub](https://github.com/pyinstaller/pyinstaller)
- [Примеры сборки](https://github.com/pyinstaller/pyinstaller/tree/develop/examples)

## 🎉 Результат

После успешной сборки у вас будет:
- ✅ Один EXE файл
- ✅ Работает без Python
- ✅ Можно распространять
- ✅ Простой запуск

Теперь парсер можно использовать на любом компьютере с Windows! 🚀
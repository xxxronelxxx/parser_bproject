@echo off
echo 🚀 Исправленная сборка EXE файла для парсера
echo ================================================

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python и добавьте в PATH
    pause
    exit /b 1
)

echo ✅ Python найден
echo.

REM Устанавливаем PyInstaller
echo 📦 Устанавливаем PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 (
    echo ❌ Ошибка установки PyInstaller
    pause
    exit /b 1
)

echo ✅ PyInstaller установлен
echo.

REM Устанавливаем все зависимости
echo 📦 Устанавливаем зависимости...
python -m pip install -r requirements-requests.txt
if errorlevel 1 (
    echo ⚠️ Некоторые зависимости не установлены, продолжаем...
)

echo ✅ Зависимости установлены
echo.

REM Создаем spec файл с правильными настройками
echo 🔧 Создаем spec файл...
python -c "
import PyInstaller.__main__
PyInstaller.__main__.run([
    '--name=NovaskladParser',
    '--onefile',
    '--console',
    '--hidden-import=bs4',
    '--hidden-import=bs4.builder',
    '--hidden-import=bs4.builder._lxml',
    '--hidden-import=lxml',
    '--hidden-import=lxml.etree',
    '--hidden-import=lxml.html',
    '--hidden-import=pandas',
    '--hidden-import=openpyxl',
    '--hidden-import=rich',
    '--hidden-import=rich.console',
    '--hidden-import=rich.progress',
    '--hidden-import=rich.panel',
    '--hidden-import=rich.table',
    '--hidden-import=requests',
    '--hidden-import=urllib3',
    '--hidden-import=certifi',
    '--hidden-import=charset_normalizer',
    '--hidden-import=idna',
    '--hidden-import=chardet',
    'parser-requests.py'
])
"

if errorlevel 1 (
    echo ❌ Ошибка сборки!
    pause
    exit /b 1
)

echo ✅ Сборка завершена успешно!
echo.

REM Копируем EXE в корневую папку
if exist "dist\NovaskladParser.exe" (
    copy "dist\NovaskladParser.exe" "NovaskladParser.exe"
    echo ✅ EXE файл скопирован в корневую папку
    echo.
    
    REM Показываем размер файла
    for %%A in ("NovaskladParser.exe") do echo 📊 Размер файла: %%~zA байт
    
    echo.
    echo 🎉 Готово! Теперь можно запускать NovaskladParser.exe
    echo 💡 Все модули включены!
    
    REM Очищаем временные файлы
    echo.
    echo 🧹 Очищаем временные файлы...
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    if exist "__pycache__" rmdir /s /q "__pycache__"
    if exist "NovaskladParser.spec" del "NovaskladParser.spec"
    echo ✅ Временные файлы удалены
    
) else (
    echo ❌ EXE файл не найден в папке dist
)

echo.
pause
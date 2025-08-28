@echo off
echo 🚀 Правильная сборка EXE файла
echo ===============================

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    pause
    exit /b 1
)

echo ✅ Python найден
echo.

REM Устанавливаем PyInstaller если нужно
echo 📦 Проверяем PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 📦 Устанавливаем PyInstaller...
    python -m pip install pyinstaller
)

echo ✅ PyInstaller готов
echo.

REM Удаляем старые файлы
echo 🧹 Очищаем старые файлы...
if exist "NovaskladParser.exe" del "NovaskladParser.exe"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "NovaskladParser.spec" del "NovaskladParser.spec"
echo ✅ Очистка завершена
echo.

REM Собираем EXE с правильными параметрами
echo 🔨 Начинаем сборку...
pyinstaller --onefile --name=NovaskladParser --console --hidden-import=bs4 --hidden-import=bs4.builder --hidden-import=bs4.builder._lxml --hidden-import=lxml --hidden-import=lxml.etree --hidden-import=lxml.html --hidden-import=pandas --hidden-import=openpyxl --hidden-import=rich --hidden-import=rich.console --hidden-import=rich.progress --hidden-import=rich.panel --hidden-import=rich.table --hidden-import=requests --hidden-import=urllib3 --hidden-import=certifi --hidden-import=charset_normalizer --hidden-import=idna --hidden-import=chardet parser-requests.py

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
    if exist "NovaskladParser.spec" del "NovaskladParser.spec"
    echo ✅ Временные файлы удалены
    
) else (
    echo ❌ EXE файл не найден в папке dist
)

echo.
pause
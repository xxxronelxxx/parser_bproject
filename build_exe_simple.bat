@echo off
echo 🚀 Сборка EXE файла для парсера novasklad.kz
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

REM Собираем EXE
echo 🔨 Начинаем сборку EXE файла...
pyinstaller --onefile --name=NovaskladParser --hidden-import=rich.console --hidden-import=rich.progress --hidden-import=rich.panel --hidden-import=rich.table --hidden-import=pandas --hidden-import=openpyxl --hidden-import=bs4 --hidden-import=lxml parser-requests.py

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
    echo 💡 Файл работает без установки Python!
    
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
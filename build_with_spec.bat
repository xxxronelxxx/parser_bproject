@echo off
echo 🚀 Сборка EXE с готовым spec файлом
echo ====================================

REM Проверяем наличие spec файла
if not exist "NovaskladParser.spec" (
    echo ❌ Файл NovaskladParser.spec не найден!
    pause
    exit /b 1
)

echo ✅ Spec файл найден
echo.

REM Собираем EXE используя spec файл
echo 🔨 Начинаем сборку с spec файлом...
pyinstaller NovaskladParser.spec

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
    echo 💡 Все модули включены через spec файл!
    
    REM Очищаем временные файлы
    echo.
    echo 🧹 Очищаем временные файлы...
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    echo ✅ Временные файлы удалены
    
) else (
    echo ❌ EXE файл не найден в папке dist
)

echo.
pause
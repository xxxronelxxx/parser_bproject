#!/usr/bin/env python3
"""
Скрипт для сборки EXE файла из парсера
"""

import subprocess
import sys
import os
import shutil

def install_pyinstaller():
    """Устанавливает pyinstaller если не установлен"""
    try:
        import PyInstaller
        print("✅ PyInstaller уже установлен")
        return True
    except ImportError:
        print("📦 Устанавливаем PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller установлен успешно")
            return True
        except subprocess.CalledProcessError:
            print("❌ Ошибка установки PyInstaller")
            return False

def build_exe():
    """Собирает EXE файл"""
    print("🔨 Начинаем сборку EXE файла...")
    
    # Проверяем наличие основного файла
    if not os.path.exists("parser-requests.py"):
        print("❌ Файл parser-requests.py не найден!")
        return False
    
    # Команда для сборки
    cmd = [
        "pyinstaller",
        "--onefile",                    # Один EXE файл
        "--windowed",                   # Без консольного окна (можно убрать для отладки)
        "--name=NovaskladParser",       # Имя EXE файла
        "--icon=icon.ico",              # Иконка (если есть)
        "--add-data=requirements-requests.txt;.",  # Добавляем файл зависимостей
        "--hidden-import=rich.console", # Явно добавляем rich
        "--hidden-import=rich.progress",
        "--hidden-import=rich.panel",
        "--hidden-import=rich.table",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=bs4",
        "--hidden-import=lxml",
        "parser-requests.py"
    ]
    
    # Убираем параметры для файлов, которых нет
    if not os.path.exists("icon.ico"):
        cmd.remove("--icon=icon.ico")
    
    print(f"📋 Команда сборки: {' '.join(cmd)}")
    
    try:
        # Выполняем сборку
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Сборка завершена успешно!")
        
        # Проверяем результат
        exe_path = os.path.join("dist", "NovaskladParser.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # В МБ
            print(f"📁 EXE файл создан: {exe_path}")
            print(f"📊 Размер файла: {file_size:.1f} МБ")
            
            # Копируем в корневую папку
            shutil.copy2(exe_path, "NovaskladParser.exe")
            print("✅ EXE файл скопирован в корневую папку")
            
            return True
        else:
            print("❌ EXE файл не найден в папке dist")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки: {e}")
        print(f"📋 Вывод: {e.stdout}")
        print(f"❌ Ошибки: {e.stderr}")
        return False

def clean_build():
    """Очищает временные файлы сборки"""
    print("🧹 Очищаем временные файлы...")
    
    folders_to_remove = ["build", "dist", "__pycache__"]
    files_to_remove = ["NovaskladParser.spec"]
    
    for folder in folders_to_remove:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🗑️ Удалена папка: {folder}")
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️ Удален файл: {file}")

def main():
    """Главная функция"""
    print("🚀 Сборка EXE файла для парсера novasklad.kz")
    print("=" * 50)
    
    # Устанавливаем PyInstaller
    if not install_pyinstaller():
        print("❌ Не удалось установить PyInstaller")
        return
    
    # Собираем EXE
    if build_exe():
        print("\n🎉 Сборка завершена успешно!")
        print("📁 EXE файл: NovaskladParser.exe")
        print("💡 Теперь можно запускать парсер без Python!")
        
        # Очищаем временные файлы
        clean_build()
        
    else:
        print("\n💥 Сборка не удалась!")
        print("🔍 Проверьте ошибки выше")

if __name__ == "__main__":
    main()
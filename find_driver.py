#!/usr/bin/env python3
"""
Скрипт для поиска WebDriver файлов в системе
"""

import os
import glob

def find_webdriver_files():
    """Поиск WebDriver файлов в системе"""
    print("🔍 Поиск WebDriver файлов...")
    
    # Текущая директория
    current_dir = os.getcwd()
    print(f"📁 Текущая рабочая директория: {current_dir}")
    
    # Ищем в текущей директории и подпапках
    print("\n🔍 Поиск в текущей директории и подпапках:")
    
    # Поиск msedgedriver.exe
    edge_patterns = [
        "msedgedriver.exe",
        "msedgedriver",
        "**/msedgedriver.exe",
        "**/msedgedriver"
    ]
    
    for pattern in edge_patterns:
        try:
            files = glob.glob(pattern, recursive=True)
            for file in files:
                if os.path.isfile(file):
                    print(f"✅ Edge: {os.path.abspath(file)}")
        except Exception as e:
            print(f"❌ Ошибка при поиске {pattern}: {e}")
    
    # Поиск chromedriver.exe
    chrome_patterns = [
        "chromedriver.exe",
        "chromedriver",
        "**/chromedriver.exe",
        "**/chromedriver"
    ]
    
    for pattern in chrome_patterns:
        try:
            files = glob.glob(pattern, recursive=True)
            for file in files:
                if os.path.isfile(file):
                    print(f"✅ Chrome: {os.path.abspath(file)}")
        except Exception as e:
            print(f"❌ Ошибка при поиске {pattern}: {e}")
    
    # Поиск в стандартных местах Windows
    print("\n🔍 Поиск в стандартных местах Windows:")
    windows_paths = [
        "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedgedriver.exe",
        "C:\\Program Files\\Microsoft\\Edge\\Application\\msedgedriver.exe",
        "C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe",
        "C:\\Windows\\System32\\msedgedriver.exe",
        "C:\\Windows\\SysWOW64\\msedgedriver.exe"
    ]
    
    for path in windows_paths:
        if os.path.exists(path):
            print(f"✅ Windows: {path}")
        else:
            print(f"❌ Windows: {path} - не найден")
    
    # Поиск в переменных окружения
    print("\n🔍 Поиск в переменных окружения:")
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    for path_dir in path_dirs:
        if 'edge' in path_dir.lower() or 'chrome' in path_dir.lower():
            print(f"📁 PATH: {path_dir}")
            try:
                files = os.listdir(path_dir)
                for file in files:
                    if 'msedgedriver' in file.lower() or 'chromedriver' in file.lower():
                        full_path = os.path.join(path_dir, file)
                        if os.path.isfile(full_path):
                            print(f"✅ PATH файл: {full_path}")
            except Exception as e:
                print(f"❌ Ошибка при чтении {path_dir}: {e}")

if __name__ == "__main__":
    find_webdriver_files()
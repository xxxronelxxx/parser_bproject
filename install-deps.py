#!/usr/bin/env python3
"""
Скрипт для установки зависимостей парсера
"""

import subprocess
import sys
import os

def install_package(package):
    """Устанавливает пакет через pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🔧 Установка зависимостей для парсера...")
    
    # Список необходимых пакетов
    packages = [
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0", 
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "rich>=13.0.0",
        "lxml>=4.9.0"
    ]
    
    print(f"📦 Устанавливаем {len(packages)} пакетов...")
    
    success_count = 0
    for package in packages:
        print(f"📥 Устанавливаем {package}...")
        if install_package(package):
            print(f"✅ {package} установлен успешно")
            success_count += 1
        else:
            print(f"❌ Ошибка установки {package}")
    
    print(f"\n📊 Результат: {success_count}/{len(packages)} пакетов установлено")
    
    if success_count == len(packages):
        print("🎉 Все зависимости установлены! Теперь можно запускать парсер:")
        print("python parser-requests.py")
    else:
        print("⚠️ Некоторые пакеты не установлены. Попробуйте установить вручную:")
        print("pip install -r requirements-requests.txt")

if __name__ == "__main__":
    main()
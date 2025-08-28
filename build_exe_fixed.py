#!/usr/bin/env python3
"""
Исправленный скрипт для сборки EXE файла
"""

import subprocess
import sys
import os
import shutil

def install_pyinstaller():
    """Устанавливает pyinstaller"""
    try:
        import PyInstaller
        print("✅ PyInstaller уже установлен")
        return True
    except ImportError:
        print("📦 Устанавливаем PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            return True
        except:
            return False

def build_exe():
    """Собирает EXE файл с правильными параметрами"""
    print("🔨 Начинаем сборку EXE файла...")
    
    # Создаем spec файл с правильными настройками
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['parser-requests.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'bs4',
        'bs4.builder',
        'bs4.builder._html5lib',
        'bs4.builder._htmlparser',
        'bs4.builder._lxml',
        'lxml',
        'lxml.etree',
        'lxml.html',
        'lxml.html.clean',
        'lxml.html.defs',
        'lxml.html.diff',
        'lxml.html.formfill',
        'lxml.html.html5parser',
        'lxml.html.soupparser',
        'lxml.html.usedoctest',
        'lxml.html.builder',
        'lxml.html.clean',
        'lxml.html.defs',
        'lxml.html.diff',
        'lxml.html.formfill',
        'lxml.html.html5parser',
        'lxml.html.soupparser',
        'lxml.html.usedoctest',
        'pandas',
        'pandas._libs',
        'pandas._libs.tslibs',
        'pandas._libs.tslibs.base',
        'pandas._libs.tslibs.offsets',
        'pandas._libs.tslibs.parsing',
        'pandas._libs.tslibs.period',
        'pandas._libs.tslibs.strptime',
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.timestamps',
        'pandas._libs.tslibs.timezones',
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.timestamps',
        'pandas._libs.tslibs.timezones',
        'openpyxl',
        'openpyxl.cell',
        'openpyxl.workbook',
        'openpyxl.worksheet',
        'openpyxl.styles',
        'openpyxl.utils',
        'openpyxl.reader',
        'openpyxl.writer',
        'rich',
        'rich.console',
        'rich.progress',
        'rich.panel',
        'rich.table',
        'rich.text',
        'rich.ansi',
        'rich.color',
        'rich.control',
        'rich.default_styles',
        'rich.emoji',
        'rich.highlighter',
        'rich.layout',
        'rich.live',
        'rich.logging',
        'rich.markdown',
        'rich.measure',
        'rich.padding',
        'rich.pretty',
        'rich.prompt',
        'rich.rule',
        'rich.screen',
        'rich.segment',
        'rich.spinner',
        'rich.status',
        'rich.syntax',
        'rich.tabulate',
        'rich.traceback',
        'rich.tree',
        'requests',
        'urllib3',
        'urllib3.util',
        'urllib3.util.retry',
        'urllib3.util.timeout',
        'urllib3.util.url',
        'urllib3.util.ssl_',
        'urllib3.util.connection',
        'urllib3.util.request',
        'urllib3.util.response',
        'urllib3.util.retry',
        'urllib3.util.timeout',
        'urllib3.util.url',
        'urllib3.util.ssl_',
        'urllib3.util.connection',
        'urllib3.util.request',
        'urllib3.util.response',
        'certifi',
        'charset_normalizer',
        'idna',
        'chardet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NovaskladParser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    # Сохраняем spec файл
    with open("NovaskladParser.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ Spec файл создан")
    
    # Собираем с помощью spec файла
    try:
        result = subprocess.run([
            "pyinstaller", "NovaskladParser.spec"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Сборка завершена успешно!")
        
        # Проверяем результат
        exe_path = os.path.join("dist", "NovaskladParser.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 EXE файл создан: {exe_path}")
            print(f"📊 Размер файла: {file_size:.1f} МБ")
            
            # Копируем в корневую папку
            shutil.copy2(exe_path, "NovaskladParser.exe")
            print("✅ EXE файл скопирован в корневую папку")
            
            return True
        else:
            print("❌ EXE файл не найден")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки: {e}")
        return False

def main():
    """Главная функция"""
    print("🚀 Исправленная сборка EXE файла")
    print("=" * 40)
    
    if not install_pyinstaller():
        print("❌ Не удалось установить PyInstaller")
        return
    
    if build_exe():
        print("\n🎉 Сборка завершена успешно!")
        print("📁 EXE файл: NovaskladParser.exe")
        print("💡 Теперь все модули включены!")
    else:
        print("\n💥 Сборка не удалась!")

if __name__ == "__main__":
    main()
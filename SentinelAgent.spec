# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['pythoncom', 'pywintypes', 'servicemanager', 'win32api', 'win32con', 'win32event', 'win32evtlog', 'win32pipe', 'win32service', 'win32serviceutil', 'win32timezone', 'win32trace', 'winerror', 'ntsecuritycon']
hiddenimports += collect_submodules('win32com')


a = Analysis(
    ['agent\\agent.py'],
    pathex=[],
    binaries=[('C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python314\\Lib\\site-packages\\pywin32_system32\\pythoncom314.dll', '.'), ('C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python314\\Lib\\site-packages\\pywin32_system32\\pywintypes314.dll', '.')],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SentinelAgent',
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

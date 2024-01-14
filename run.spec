# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

from PyInstaller.utils.hooks import collect_submodules

psutil_submodules = collect_submodules('psutil')

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/ustupan/PycharmProjects/Metin2-Fish-Bot/venv/Lib/site-packages/customtkinter', 'customtkinter')
    , ('C:/Users/ustupan/lib/site-packages/keyboard', 'keyboard'), ('C:/Users/ustupan/lib/site-packages/openai', 'openai')],
    hiddenimports=collect_submodules('psutil') + ['win32api', 'keyboard', 'pyautogui', 'pywinauto', 'tkinter.font', 'darkdetect', 'openai', 'aiohttp'],
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
    hookspath=collect_submodules('psutil') + ['win32api', 'openai'],
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
     **{'onefile': True}
)

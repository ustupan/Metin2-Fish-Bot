# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

from PyInstaller.utils.hooks import collect_submodules

psutil_submodules = collect_submodules('psutil')

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/pc/AppData/Local/Programs/Python/Python38/Lib/site-packages/customtkinter', 'customtkinter')],
    hiddenimports=collect_submodules('psutil') + ['win32api', 'keyboard'],
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
    hookspath=collect_submodules('psutil') + ['win32api'],
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
)

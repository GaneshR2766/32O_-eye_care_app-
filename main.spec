# -*- mode: python ; coding: utf-8 -*-
import os

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],  # ensure correct relative path resolution
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('sounds', 'sounds'),
        ('sounds/user', 'sounds/user'),
        ('nature/*', 'nature'),
        ('settings.json', '.')
    ],

    hiddenimports=[],
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
    [],
    icon='assets/icon2.ico',
    exclude_binaries=True,
    name='32O',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # hides console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='32O',
)

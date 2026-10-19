# -*- mode: python ; coding: utf-8 -*-
# Public experimental build: no third-party music or Zpix font.

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/images', 'assets/images'),
        ('assets/fonts/PressStart2P-Regular.ttf', 'assets/fonts'),
        ('assets/fonts/FusionPixel10.ttf', 'assets/fonts'),
        ('assets/icon.ico', 'assets'),
        ('data', 'data'),
        ('licenses', 'licenses'),
    ],
    hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=['numpy'], noarchive=False, optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='LateNightProgrammerSimulator', debug=False,
    bootloader_ignore_signals=False, strip=False, upx=True, upx_exclude=[],
    runtime_tmpdir=None, console=False, disable_windowed_traceback=False,
    argv_emulation=False, target_arch=None, codesign_identity=None,
    entitlements_file=None, icon=['assets/icon.ico'],
)

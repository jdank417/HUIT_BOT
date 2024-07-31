# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['OptimisticOptimizer.py'],
    pathex=['/Users/jasondank/PycharmProjects/HUIT_BOT'],
    binaries=[],
    datas=[("info.txt", "."), ("config.json", "."), ("HUITLogo.png", ".")],
    hiddenimports=[
        'pkg_resources._vendor.jaraco.functools',
        'pkg_resources._vendor.jaraco.context',
        'pkg_resources._vendor.jaraco.text',
        'onnxscript'
    ],
    hookspath=[],
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
    [],
    exclude_binaries=True,
    name='OptimisticOptimizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OptimisticOptimizer',
)
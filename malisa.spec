# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

added_files = [
  ('_distr', '_distr'),
  ('actions/*.*', 'actions'),

  ('books/README.md', 'books'),
  ('books/Философия Процесса - Уайтхед.pdf', 'books'),

  # ('config/*.*', 'config'),
  ('config/config.in_', 'config'),
  ('config/logic.yaml', 'config'),
  ('config/user_logic.yaml', 'config'),
  ('config/radio_links.yaml', 'config'),
  ('config/words.yaml', 'config'),
  ('config/README.md', 'config'),

  ('data/*.*', 'data'),
  ('memo/README.md', 'memo'),
  ('playlist/*.*', 'playlist'),  
  ('rdp/README.md', 'rdp'),  

  ('script/release/*.*', 'script'),

  ('sound/*.mp3', 'sound'),
  ('stand_up/whattodo.txt', 'stand_up'),
  ('tmp/README.md', 'tmp'),

  ('malisa.bat', '.'),

  ('VERSION', '.'),
  ('README.md', '.'),
  ('README.ru.md', '.'),  
  ('INSTALL.md', '.'),
  ('INSTALL.ru.md', '.'),

  ('README.md', 'docs'),
  ('README.ru.md', 'docs'),  
  ('INSTALL.md', 'docs'),
  ('INSTALL.ru.md', 'docs')
]

excludes = [
  # 'tk', 'tkinter'
]

hook_files = [
  './hook.py'
]

a = Analysis(
    ['malisa.py'],
    pathex=[],
    binaries=[],
    datas = added_files,
    hiddenimports=['actions'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes = excludes,
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
    name='malisa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='malisa',
)

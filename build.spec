# -*- mode: python -*-

block_cipher = None


a = Analysis(['sp_experiment/sp.py'],
             pathex=['./sp_experiment'],
             binaries=[],
             datas=[ ('sp_experiment/*json', 'sp_experiment') ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['arabic_reshaper'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='sp_experiment',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )

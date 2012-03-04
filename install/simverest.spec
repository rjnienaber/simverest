# -*- mode: python -*-
a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'src\\simverest.py'],
             pathex=['..\\..\\pyinstaller-1.5.1'])

static_web = Tree('src/web/static')
a.datas += static_web

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'simverest.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=True )

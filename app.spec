# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["Flask","Jinja2","MarkupSafe","PyQt5-Qt5","PyQt5_sip","Werkzeug","altgraph","blinker","certifi","charset-normalizer","click","colorama","idna","itsdangerous","packaging","pefile","pillow","psutil","pygame","pyinstaller","pyinstaller-hooks-contrib","pypiwin32","pywin32","pywin32-ctypes","requests","setuptools","urllib3","win10toast","time","json","random","datetime","socket","tkinter","math","socket","urllib","email","html","https,"'PyQt5.QAxContainer','PyQt5.QtBluetooth','PyQt5.QtDBus','PyQt5.QtDesigner','PyQt5.QtHelp','PyQt5.QtLocation','PyQt5.QtMultimedia','PyQt5.QtMultimediaWidgets','PyQt5.QtNetwork','PyQt5.QtNfc','PyQt5.QtOpenGL','PyQt5.QtPositioning','PyQt5.QtPrintSupport','PyQt5.QtQml','PyQt5.QtQuick','PyQt5.QtQuick3D','PyQt5.QtQuickWidgets','PyQt5.QtRemoteObjects','PyQt5.QtSensors','PyQt5.QtSerialPort','PyQt5.QtSql','PyQt5.QtSvg','PyQt5.QtTest','PyQt5.QtTextToSpeech','PyQt5.QtWebChannel','PyQt5.QtWebSockets','PyQt5.QtWinExtras','PyQt5.QtXml','PyQt5.QtXmlPatterns',],
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
    name='app',
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
    icon = ["images/4.ico"]
)

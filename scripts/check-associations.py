#!/usr/bin/env python3
"""Exercise per-user installer associations and cleanup in the disposable Wine prefix."""
from pathlib import Path
import os
import re
import subprocess

root = Path(__file__).resolve().parent.parent
out = root / 'build/association-validation'
out.mkdir(parents=True, exist_ok=True)
commands = [
    '@echo off',
    r'reg add "HKCU\Software\Classes\.docx" /ve /d "Sentinel.Document" /f',
    r'reg add "HKCU\Software\Classes\.docx\OpenWithProgids" /v "Sentinel.Document" /d "" /f',
]
installer = r'Z:\workspace\tabajara\dist\word-tab-excel-tab-instalador-windows-x64.exe'
for stage in ('installed', 'reinstalled'):
    commands.append(f'start /wait "" "{installer}" /S /D=C:\\Tab Associations Test')
    for key, name in [('Classes', stage), ('WordTab\\Capabilities', stage+'-word'),
                      ('ExcelTab\\Capabilities', stage+'-excel'), ('RegisteredApplications', stage+'-apps')]:
        commands.append(f'reg export "HKCU\\Software\\{key}" "Z:\\workspace\\tabajara\\build\\association-validation\\{name}.reg" /y')
commands += [r'"C:\Tab Associations Test\Desinstalar.exe" /S _?=C:\Tab Associations Test',
             r'reg export "HKCU\Software\Classes" "Z:\workspace\tabajara\build\association-validation\uninstalled.reg" /y',
             r'reg export "HKCU\Software\RegisteredApplications" "Z:\workspace\tabajara\build\association-validation\uninstalled-apps.reg" /y']
(out / 'test.cmd').write_bytes(('\r\n'.join(commands)+'\r\n').encode())
subprocess.run(['bash', str(root/'scripts/wine.sh'), 'cmd.exe', '/c',
                r'Z:\workspace\tabajara\build\association-validation\test.cmd'],
               env={**os.environ, 'DISPLAY': os.environ.get('DISPLAY', ':99')}, check=True)

def read(name):
    return (out/(name+'.reg')).read_text(encoding='utf-16')

def sections(text):
    return {m[1]: m[2] for m in re.finditer(r'^\[([^\n]+)\]\n(.*?)(?=^\[|\Z)', text, re.M|re.S)}

word = '.docx .docm .dotx .dotm .doc .dot .rtf .odt .md .txt'.split()
excel = '.xlsx .xlsm .xlsb .ods .csv .tsv'.split()
for stage in ('installed', 'reinstalled'):
    data = read(stage)
    keys = sections(data)
    for app, exts, cap in [('WordTab', word, 'word'), ('ExcelTab', excel, 'excel')]:
        prefix = 'HKEY_CURRENT_USER\\Software\\Classes\\'
        expected = f'"C:\\Tab Associations Test\\{app}.exe" "%1"'
        # .reg serialization escapes backslashes and double quotes.
        encoded = expected.replace('\\', '\\\\').replace('"', '\\"')
        assert '@="'+encoded+'"' in keys[prefix+f'Applications\\{app}.exe\\shell\\open\\command']
        for ext in exts:
            entry = keys[prefix+ext+'\\OpenWithProgids']
            match = re.search(r'"('+app+r'\.[^"]+)"=', entry)
            assert match, (stage, app, ext)
            assert '@="'+encoded+'"' in keys[prefix+match[1]+'\\shell\\open\\command']
            assert f'"{ext}"=""' in keys[prefix+f'Applications\\{app}.exe\\SupportedTypes']
            assert f'"{ext}"="{app}.' in read(stage+'-'+cap)
        assert f'"{app[:-3]} Tab"=' in read(stage+'-apps')
    assert '@="Sentinel.Document"' in keys['HKEY_CURRENT_USER\\Software\\Classes\\.docx']
    assert '"Sentinel.Document"=""' in keys['HKEY_CURRENT_USER\\Software\\Classes\\.docx\\OpenWithProgids']
clean = read('uninstalled')
assert 'WordTab.' not in clean and 'ExcelTab.' not in clean
assert 'Applications\\WordTab.exe' not in clean and 'Applications\\ExcelTab.exe' not in clean
assert '@="Sentinel.Document"' in clean and '"Sentinel.Document"=""' in clean
assert '"Word Tab"=' not in read('uninstalled-apps') and '"Excel Tab"=' not in read('uninstalled-apps')
print('PASS: install/reinstall associations, quoted commands, supported types, capabilities, preserved default and other applications, uninstall cleanup')

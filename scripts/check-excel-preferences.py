#!/usr/bin/env python3
"""Check preferences after restarting the test Excel Tab (--control 7979).

Before restarting: pin Print Preview through the More menu, enable AutoSave,
open a saved XLSX and edit a cell. Confirm the disk edit, then quit normally.
Use scripts/wine.sh with a disposable APPDATA, never a real desktop profile.
"""
import json
import socket
import time


def call(method, params=None):
    with socket.create_connection(('127.0.0.1', 7979), timeout=5) as connection:
        connection.settimeout(30)
        with connection.makefile('rwb') as stream:
            stream.write((json.dumps({'id':1,'method':method,'params':params or {}})+'\n').encode())
            stream.flush()
            response = json.loads(stream.readline())
    assert response.get('ok'), response
    return response.get('result')

state = call('ui.inspect')
assert state['ui']['autosave'] is True, state
assert 'preview' in state['ui']['quickAccess'], state
assert state['ui']['language'] == 'pt' and state['ui']['animations'] is False
call('app.open', {'path':r'Z:\workspace\tabajara\build\print-settings-validation\Impressão Brasil.xlsx'})
assert call('cell.get', {'cell':'B1'})['value'] == 'Salvo automaticamente'
call('ui.click', {'x':389,'y':19})
for _ in range(40):
    state = call('ui.inspect')
    if state['backstage'] == 'print':
        break
    time.sleep(.1)
else:
    raise AssertionError('The pinned preview button did not open Print')
print('PASS: pinned shortcut and AutoSave restored after restart; saved edit reopened; pinned shortcut opens preview')

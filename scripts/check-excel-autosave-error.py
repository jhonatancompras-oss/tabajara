#!/usr/bin/env python3
"""Verify an AutoSave failure preserves edits and alerts the user (disposable Wine app)."""
from pathlib import Path
import json
import socket
import tempfile
import time

root=Path(__file__).resolve().parent.parent
out=Path(tempfile.mkdtemp(prefix='autosave-error-',dir=root/'build'))
folder=out/'destination'
folder.mkdir()
path=folder/'test.xlsx'

def call(method,params=None):
    with socket.create_connection(('127.0.0.1',7979),timeout=5) as connection:
        connection.settimeout(30)
        with connection.makefile('rwb') as stream:
            stream.write((json.dumps({'id':1,'method':method,'params':params or {}})+'\n').encode())
            stream.flush()
            response=json.loads(stream.readline())
    assert response.get('ok'),response
    return response.get('result')

assert call('ui.inspect')['ui']['autosave'] is True
call('app.save',{'path':'Z:'+str(path).replace('/','\\')})
before=path.read_bytes()
folder.rename(out/'preserved')
folder.write_text('Test-only obstruction: the original XLSX is preserved beside this file.')
try:
    call('cell.set',{'cell':'D1','input':'Alteração preservada após falha'})
    for _ in range(100):
        state=call('ui.inspect')
        if not state['ui']['autosave'] and state['message']:break
        time.sleep(.1)
    else:raise AssertionError('AutoSave failed silently')
    assert 'Falha no salvamento automático:' in state['message']['text'],state
    assert state['documents'][state['activeDocument']]['dirty']
    assert call('cell.get',{'cell':'D1'})['value']=='Alteração preservada após falha'
    assert (out/'preserved/test.xlsx').read_bytes()==before
    (out/'result.json').write_text(json.dumps(state,ensure_ascii=False,indent=2))
finally:
    folder.unlink()
    (out/'preserved').rename(folder)
call('ui.key',{'key':'Escape'})
call('app.save')
assert path.is_file()
print('PASS: AutoSave failure shows Portuguese alert, stops retries, preserves unsaved edit and original XLSX; manual save succeeds after restoring destination')

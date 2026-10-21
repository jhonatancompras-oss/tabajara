#!/usr/bin/env python3
"""Drive the installed Excel Tab at --control 7979, under the Wine virtual display."""
from pathlib import Path
import json
import socket
import time

root = Path(__file__).resolve().parent.parent
out = root / 'build/menu-validation'
out.mkdir(parents=True, exist_ok=True)
records = []

def call(method, params=None):
    with socket.create_connection(('127.0.0.1', 7979), timeout=5) as connection:
        connection.settimeout(60)
        with connection.makefile('rwb') as stream:
            stream.write((json.dumps({'id':1, 'method':method, 'params':params or {}})+'\n').encode())
            stream.flush()
            response = json.loads(stream.readline())
    records.append({'method':method, 'params':params, 'response':response})
    assert response.get('ok'), response
    return response.get('result')

def shot(name):
    call('ui.screenshot', {'path':'Z:'+str(out/name).replace('/', '\\')})

def page():
    # UI pointer/keyboard events are processed in the next frame.
    for _ in range(40):
        state = call('ui.inspect')
        if state['backstage'] == 'print':
            return state
        time.sleep(.1)
    raise AssertionError(state)

try:
    call('ui.resize', {'width':1360,'height':900})
    call('engine.execute', {'command':'app.language.set','params':{'language':'pt'}})
    call('cell.set', {'cell':'A1','input':'Prévia de impressão — Tab'})
    call('cell.set', {'cell':'A70','input':'Segunda página'})
    path = 'Z:'+str(out/'Prévia Brasil.xlsx').replace('/', '\\')
    call('app.save', {'path':path})
    before = call('document.inspect')
    call('ui.click', {'x':357,'y':19})
    shot('menu-portugues.png')
    call('ui.click', {'x':430,'y':180})
    assert page()['documents'][0]['title'] == 'Prévia Brasil.xlsx'
    shot('visualizar-impressao.png')
    call('ui.click', {'x':653,'y':694})
    shot('visualizar-impressao-pagina2.png')
    call('ui.key', {'key':'Escape'})
    call('ui.key', {'key':'P','ctrl':True})
    page()
    shot('ctrl-p-previa.png')
    call('ui.key', {'key':'Escape'})
    time.sleep(.2)
    call('ui.click', {'x':357,'y':19})
    call('ui.click', {'x':430,'y':206})
    page()
    printing = call('engine.execute', {'command':'ui.printSettings','params':{}})
    assert not printing['busy'] and printing['status'] not in ('submitted', 'submitting')
    assert call('document.inspect') == before, 'Preview changed the workbook'
    call('ui.key', {'key':'Escape'})
    call('app.open', {'path':path})
    assert call('cell.get', {'cell':'A70'})['value'] == 'Segunda página'
    print('PASS: preview menu, page navigation, Ctrl+P, Print menu open settings without submission; workbook preserved and reopened')
finally:
    (out/'results.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))

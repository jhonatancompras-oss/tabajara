#!/usr/bin/env python3
"""Exercise the print sidebar through real pointer/keyboard events at 1360x900.

Use the disposable Wine APPDATA prepared for check-excel-preferences.py, which
leaves the two-page test workbook open on the Print page with AutoSave enabled.
"""
from pathlib import Path
import json
import socket
import time
import xml.etree.ElementTree as ET
import zipfile

root = Path(__file__).resolve().parent.parent
out = root/'build/print-settings-validation'
records = []

def call(method, params=None):
    with socket.create_connection(('127.0.0.1',7979),timeout=5) as connection:
        connection.settimeout(30)
        with connection.makefile('rwb') as stream:
            stream.write((json.dumps({'id':1,'method':method,'params':params or {}})+'\n').encode())
            stream.flush()
            response = json.loads(stream.readline())
    records.append({'method':method,'params':params,'response':response})
    assert response.get('ok'), response
    return response.get('result')

def click(x,y,count=1):
    call('ui.click',{'x':x,'y':y,'count':count})
    time.sleep(.15)

def text(x,y,value,count=1):
    click(x,y,count)
    call('ui.key',{'key':'A','ctrl':True})
    call('ui.text',{'text':value})
    time.sleep(.1)

def preview():
    return call('engine.execute',{'command':'file.printPreview','params':{}})

def shot(name):
    call('ui.screenshot',{'path':'Z:'+str(out/name).replace('/','\\')})

try:
    # Printer discovery must have finished so its status text has stable height.
    for _ in range(100):
        status=call('engine.execute',{'command':'ui.printSettings','params':{}})
        if not status['discovering']:break
        time.sleep(.1)
    call('engine.execute',{'command':'pageLayout.pageSetup','params':{'fitToPage':False,'printArea':'','right':0.7}})
    call('engine.execute',{'command':'ui.backstage','params':{'page':'close'}})
    call('engine.execute',{'command':'ui.backstage','params':{'page':'print'}})
    assert preview()['pages']==2
    text(330,557,'A1:C10')
    click(320,584)
    result=preview()
    assert result['pages']==1 and result['pageList'][0]['range']=='A1:C10',result
    click(320,612)
    assert preview()['pages']==2
    text(330,557,'A1:C70')
    click(320,584)
    assert preview()['pages']==2
    text(333,710,'2.54',2)
    call('ui.key',{'key':'Enter'})
    click(247,501)
    assert preview()['pages']==1
    shot('margens-area-ajuste.png')
    call('app.save')
    path=out/'Impressão Brasil.xlsx'
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as archive:
        sheet=ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
        margins=sheet.find('m:pageMargins',ns)
        assert abs(float(margins.attrib['right'])-1.0)<1e-5,margins.attrib
        setup=sheet.find('m:pageSetup',ns)
        assert setup.attrib['fitToWidth']=='1' and setup.attrib['fitToHeight']=='1',setup.attrib
        workbook=ET.fromstring(archive.read('xl/workbook.xml'))
        area=next(e for e in workbook.findall('m:definedNames/m:definedName',ns) if e.attrib.get('name')=='_xlnm.Print_Area')
        assert '$A$1:$C$70' in area.text,area.text
    call('app.open',{'path':'Z:'+str(path).replace('/','\\')})
    assert preview()['pages']==1
    assert call('cell.get',{'cell':'C70'})['value']=='Fim da área'
    call('engine.execute',{'command':'ui.backstage','params':{'page':'close'}})
    call('cell.set',{'cell':'B2','input':''})
    call('ui.cell.click',{'cell':'B2'})
    call('ui.edit.begin',{'text':'Salvar pela barra'})
    click(241,19)
    assert call('cell.get',{'cell':'B2'})['value']=='Salvar pela barra'
    click(273,19)
    assert call('cell.get',{'cell':'B2'})['value'] in ('',None)
    click(325,19)
    assert call('cell.get',{'cell':'B2'})['value']=='Salvar pela barra'
    marker=f'AutoSave após reiniciar {time.time_ns()}'
    call('cell.set',{'cell':'C3','input':marker})
    for _ in range(100):
        try:
            with zipfile.ZipFile(path) as archive:
                if any(marker in archive.read(n).decode() for n in archive.namelist() if n.endswith('.xml')):break
        except zipfile.BadZipFile:
            pass
        time.sleep(.1)
    else:raise AssertionError('AutoSave stopped working after restart')
    call('ui.click',{'x':389,'y':19,'button':'right'})
    shot('remover-atalho.png')
    click(470,44)
    for _ in range(40):
        if 'preview' not in call('ui.inspect')['ui']['quickAccess']:break
        time.sleep(.1)
    else:raise AssertionError('Pinned shortcut was not removed')
    shot('barra-apos-remover.png')
    print('PASS: set/clear print area; cm margins and fit persisted in XLSX and reopened; Save commits draft, Undo/Redo work; AutoSave works after restart; pinned shortcut removed')
finally:
    (out/'results.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))

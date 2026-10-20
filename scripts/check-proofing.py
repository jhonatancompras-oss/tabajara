#!/usr/bin/env python3
"""Regression: proofing selector, old preferences, real Portuguese spelling and restart."""
from pathlib import Path
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path('/workspace/tabajara')
EVIDENCE = Path(tempfile.mkdtemp(prefix='proofing-validation-', dir=ROOT / 'build'))
PROFILE = EVIDENCE / 'profile'
PROFILE.mkdir()
# A preferences file produced before proofingLanguage existed must still load.
(PROFILE / 'ui.json').write_text(json.dumps({'language': 'pt-br', 'startScreen': True}))
BINARY = sys.argv[1] if len(sys.argv) > 1 else '/workspace/wine-tab-runtime/drive_c/TabProofingValidation/WordTab.exe'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
records = []

def windows(path):
    return 'Z:' + str(path).replace('/', '\\')

class App:
    def __init__(self, number):
        self.log = (EVIDENCE / f'session-{number}.log').open('w')
        environment = dict(os.environ, DISPLAY=':99', WGPU_BACKEND='gl', LIBGL_ALWAYS_SOFTWARE='1',
                           WORDCRAFT_PROFILE_DIR=windows(PROFILE))
        self.process = subprocess.Popen(['bash', str(ROOT / 'scripts/wine.sh'), BINARY, '--control', '7981'],
                                        env=environment, stdout=self.log, stderr=subprocess.STDOUT)
        self.id = 0
        for _ in range(90):
            if self.process.poll() is not None:
                raise RuntimeError(f'App stopped early; see {EVIDENCE}')
            try:
                self.socket = socket.create_connection(('127.0.0.1', 7981), timeout=2)
                keyfile = PROFILE / 'control-key.local-7981'
                if not keyfile.exists():
                    self.socket.close()
                    time.sleep(1)
                    continue
                self.key = keyfile.read_text().strip()
                self.socket.settimeout(60)
                self.stream = self.socket.makefile('rwb')
                return
            except ConnectionRefusedError:
                time.sleep(1)
        raise TimeoutError(f'App did not become ready; see {EVIDENCE}')

    def call(self, method, params=None, fail=False):
        self.id += 1
        payload = {'id': self.id, 'key': self.key, 'method': method, 'params': params or {}}
        self.stream.write((json.dumps(payload, ensure_ascii=False) + '\n').encode())
        self.stream.flush()
        response = json.loads(self.stream.readline())
        records.append({'method': method, 'params': params, 'response': response})
        assert response.get('ok') == (not fail), response
        return response.get('result')

    def save(self, name, language):
        path = EVIDENCE / name
        self.call('file.save', {'path': windows(path)})
        with zipfile.ZipFile(path) as archive:
            styles = ET.fromstring(archive.read('word/styles.xml'))
            default = styles.find(f'{W}docDefaults/{W}rPrDefault/{W}rPr/{W}lang')
            assert default is not None and default.get(W + 'val') == language, name
            document = ET.fromstring(archive.read('word/document.xml'))
            assert all(tag.get(W + 'val') == language for tag in document.iter(W + 'lang')), name
            return ''.join(t.text or '' for t in document.iter(W + 't'))

    def close(self):
        self.call('app.quit')
        self.stream.close()
        self.socket.close()
        assert self.process.wait(timeout=45) == 0
        self.log.close()

try:
    app = App(1)
    # A control-port launch deliberately opens an editor; closing it models the normal start screen.
    app.call('file.close', {'force': True})
    state = app.call('ui.proofingLanguage')
    assert state['language'] == 'pt-BR' and state['hasDocument'] is False
    app.call('file.options', {'pane': 'language'})
    app.call('ui.screenshot', {'path': windows(EVIDENCE / 'language-no-document.png')})
    app.call('ui.proofingLanguage', {'value': 'en-US'})
    app.call('ui.language', {'value': 'en'})
    app.call('file.new', {'template': 'blank'})
    text = 'A casa é bonita. As crianças brincam no jardim. cazaaa.'
    app.call('text.insert', {'text': text})
    assert app.save('original-english.docx', 'en-US') == text
    app.call('ui.proofingLanguage', {'value': 'pt-BR', 'applyToDocument': True})
    assert app.save('converted-portuguese.docx', 'pt-BR') == text
    issues = app.call('review.issues')
    spelling = [issue for issue in issues if issue['kind'] == 'spelling']
    assert [issue['text'] for issue in spelling] == ['cazaaa'], spelling
    assert all(issue['lang'].lower().startswith('pt') for issue in spelling)
    app.call('ui.proofingLanguage', {'value': '!!!'}, fail=True)
    assert app.call('ui.proofingLanguage')['language'] == 'pt-BR'
    app.close()
    saved = json.loads((PROFILE / 'ui.json').read_text())
    assert saved['proofingLanguage'] == 'pt-BR' and saved['language'] == 'en'

    app = App(2)
    app.call('file.close', {'force': True})
    assert app.call('ui.proofingLanguage')['language'] == 'pt-BR'
    app.call('file.new', {'template': 'blank'})
    app.call('text.insert', {'text': 'casa'})
    app.save('portuguese-after-restart.docx', 'pt-BR')
    app.call('ui.proofingLanguage', {'value': 'en-US'})
    assert app.save('existing-document-preserved.docx', 'pt-BR') == 'casa'
    app.call('file.new', {'template': 'blank'})
    app.save('english-new-document.docx', 'en-US')
    app.call('ui.proofingLanguage', {'value': 'pt-BR', 'applyToDocument': True})
    app.save('portuguese-empty-document.docx', 'pt-BR')
    app.call('ui.language', {'value': 'pt-br'})
    app.call('file.options', {'pane': 'language'})
    app.call('ui.screenshot', {'path': windows(EVIDENCE / 'language-portuguese.png')})
    app.close()
    print('PASS: legacy preferences, selectable proofing languages, whole-text application, Portuguese dictionary, restart persistence and independent interface language.')
finally:
    (EVIDENCE / 'results.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
    print(f'Evidence: {EVIDENCE}')

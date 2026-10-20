#!/usr/bin/env python3
"""Exercise the actual Windows CLI binaries, including OOXML save/reopen and PDF export."""
from pathlib import Path
import json
import subprocess
import tempfile
import zipfile

ROOT = Path('/workspace/tabajara')
WORD = Path('/workspace/wordcraft/target/x86_64-pc-windows-gnu/release/wordcraft-cli.exe')
EXCEL = ROOT / 'build/gridcraft/target/x86_64-pc-windows-gnu/release/gridcraft-cli.exe'
folder = Path(tempfile.mkdtemp(prefix='validation-', dir=ROOT / 'build'))
results = []

def windows(path):
    return 'Z:' + str(path).replace('/', '\\')

def run(binary, *args):
    result = subprocess.run(['bash', str(ROOT / 'scripts/wine.sh'), str(binary), *args],
                            capture_output=True, text=True, timeout=120)
    results.append({'program': binary.name, 'args': args, 'exit_code': result.returncode,
                    'stdout': result.stdout, 'stderr': result.stderr})
    if result.returncode:
        (folder / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
        raise RuntimeError(f'{binary.name} failed: {result.stderr}')
    return result.stdout.strip()

docx = folder / 'texto.docx'
pdf = folder / 'texto.pdf'
text = 'Olá, Word Tab! Café e ação.'
run(WORD, 'run', '--cmd', 'text.insert=' + json.dumps({'text': text}, ensure_ascii=False), '--save', windows(docx))
with zipfile.ZipFile(docx) as archive:
    assert text in archive.read('word/document.xml').decode(), 'DOCX text did not round-trip'
run(WORD, 'convert', windows(docx), windows(pdf))
assert pdf.read_bytes().startswith(b'%PDF-') and pdf.stat().st_size > 1000

xlsx = folder / 'planilha.xlsx'
run(EXCEL, 'run', '--cmd', 'cell.set={"cell":"A1","input":"10"}',
    '--cmd', 'cell.set={"cell":"A2","input":"20"}',
    '--cmd', 'cell.set={"cell":"A3","input":"=SUM(A1:A2)"}', '--out', windows(xlsx), '--quiet')
assert run(EXCEL, 'eval', '=A3', '--in', windows(xlsx)) == '30', 'Spreadsheet formula did not survive save/reopen'
with zipfile.ZipFile(xlsx) as archive:
    assert 'xl/workbook.xml' in archive.namelist()

(folder / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
print(f'PASS: DOCX with Portuguese text, PDF export, XLSX save/reopen and formula result 30. Evidence: {folder}')

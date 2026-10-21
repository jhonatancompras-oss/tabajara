#!/usr/bin/env python3
"""Export the installer, hashes and original Tab artwork for download."""
from pathlib import Path
import hashlib
import shutil
import zipfile

root = Path('/workspace/tabajara')
output = Path('/workspace/shared/downloads')
output.mkdir(parents=True, exist_ok=True)
installer = root / 'dist/word-tab-excel-tab-instalador-windows-x64.exe'
assert installer.is_file()
checksum = hashlib.sha256(installer.read_bytes()).hexdigest()
assert (root / 'dist/SHA256SUMS.txt').read_text().split()[0] == checksum
shutil.copy2(installer, output / installer.name)
shutil.copy2(root / 'dist/SHA256SUMS.txt', output / 'SHA256SUMS.txt')
with zipfile.ZipFile(output / 'word-tab-excel-tab-windows-x64.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    archive.write(installer, installer.name)
    archive.write(root / 'dist/SHA256SUMS.txt', 'SHA256SUMS.txt')
    for path in sorted((root / 'assets').rglob('*')):
        if path.is_file():
            archive.write(path, 'logos/' + str(path.relative_to(root / 'assets')))
    archive.writestr('LEIA-ME.txt',
        'WORD TAB E EXCEL TAB — WINDOWS 64 BITS\n\n'
        'Execute word-tab-excel-tab-instalador-windows-x64.exe para instalar os dois programas.\n'
        'O instalador cria um atalho para Word Tab e outro para Excel Tab.\n'
        'O idioma inicial é português do Brasil; outros idiomas continuam disponíveis nas opções.\n'
        'Atualização 0.9.0-tab.5: área de impressão e margens em centímetros na prévia.\n'
        'O ajuste a uma página e as configurações de impressão ficam salvos no XLSX.\n'
        'Use os três pontos > Fixar na barra de acesso rápido para manter os comandos na barra.\n'
        'Os atalhos e o estado do salvamento automático ficam salvos ao fechar o programa.\n'
        'O salvamento automático requer um arquivo XLSX já salvo em disco.\n'
        'Desde 0.9.0-tab.4: menu superior do Excel Tab traduzido para português.\n'
        'Use Visualizar impressão… no menu superior para conferir as páginas antes de imprimir.\n'
        'Desde 0.9.0-tab.3: os programas aparecem no Abrir com do Windows.\n'
        'O usuário pode escolher o aplicativo padrão nas configurações do Windows.\n'
        'Desde 0.9.0-tab.2: o idioma de revisão pode ser selecionado e fica salvo.\n'
        'Em Arquivo > Opções > Idioma, selecione Português (Brasil) no idioma de revisão.\n'
        'Para textos existentes, use Aplicar ao texto do documento.\n'
        'O dicionário brasileiro VERO está incluído, com seus créditos e licenças.\n'
        'Algumas mensagens e os exemplos podem aparecer em inglês.\n\n'
        'Versão independente experimental, baseada no código 0.9.0 de WordCraft e GridCraft.\n'
        'O instalador personalizado não tem assinatura digital.\n'
        'Verificações no Linux com Wine não substituem testes em um computador Windows.\n'
        'As licenças e os créditos originais acompanham a instalação.\n'
        'Os logos estão na pasta logos.\n')
print(output / installer.name)
print(output / 'word-tab-excel-tab-windows-x64.zip')

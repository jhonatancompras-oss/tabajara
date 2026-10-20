#!/usr/bin/env python3
"""Create separately branded build trees; preserve upstream checkouts and licenses."""
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for directory, package, title, original in [
    ('wordcraft', 'wordcraft', 'Word Tab', 'WordCraft'),
    ('sheetcraft', 'gridcraft', 'Excel Tab', 'GridCraft'),
]:
    source = Path('/workspace') / directory
    destination = ROOT / 'build' / package
    if destination.exists():
        raise SystemExit(f'Build tree already exists: {destination}; preserve or remove it explicitly before regenerating.')
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns('.git', 'target', 'dist'))
    for parent in ('apps', 'crates'):
        for path in (destination / parent).rglob('*'):
            if not path.is_file() or path.suffix not in ('.rs', '.tsv'):
                continue
            lines = path.read_text().splitlines(keepends=True)
            # Keep upstream copyright notices verbatim, including in About.
            path.write_text(''.join(line if 'copyright' in line.lower() else re.sub(r'\b' + original + r'\b', title, line) for line in lines))
    dialogs = destination / 'crates/ui-egui/src/dialogs.rs'
    text = dialogs.read_text()
    if package == 'wordcraft':
        text = text.replace('A free, open-source word processor written from scratch in Rust.\\nPart of the Crafting Apps from the ArtCraft team.',
                            'Editor de textos independente, baseado no WordCraft da equipe ArtCraft. Código aberto: MIT ou Apache-2.0.')
        text = '\n'.join(line for line in text.split('\n') if 'ui.hyperlink_to' not in line or ('getartcraft.com' not in line and 'discord.gg/artcraft' not in line))
        prefs = destination / 'crates/ui-egui/src/lib.rs'
        prefs.write_text(prefs.read_text().replace('show_discord: true,', 'show_discord: false,'))
        locale = destination / 'crates/ui-egui/src/i18n/mod.rs'
        content = locale.read_text().replace('static SYSTEM: OnceLock<Lang> = OnceLock::new();\n    *SYSTEM.get_or_init(detect_system_lang)',
                    'static SYSTEM: OnceLock<Lang> = OnceLock::new();\n    *SYSTEM.get_or_init(|| lang_from_tag("pt-br").unwrap_or_else(detect_system_lang))')
        locale.write_text(content)
    else:
        text = text.replace('A clean-room, open-source, Rust-native spreadsheet. Part of ArtCraft.',
                            'Planilha independente, baseada no GridCraft da equipe ArtCraft. Código aberto: MIT ou Apache-2.0.')
        text = '\n'.join(line for line in text.split('\n') if 'ui.hyperlink_to' not in line or ('getartcraft.com' not in line and 'discord.gg/artcraft' not in line))
        locale = destination / 'crates/ui-egui/src/i18n.rs'
        locale.write_text(locale.read_text().replace('pub fn system() -> Self {', 'pub fn system() -> Self {\n        if !cfg!(test) { return Self::PtBr; }'))
    dialogs.write_text(text)
    # Remove restricted ArtCraft artwork from the derivative, retaining its license notice.
    for path in (destination / 'docs/brand').glob('*'):
        if path.suffix.lower() in ('.svg', '.png'):
            path.unlink()
    assets = ROOT / 'assets' / ('word-tab' if package == 'wordcraft' else 'excel-tab')
    for path in (destination / 'assets/app-icon').rglob('*'):
        if path.is_file() and path.suffix.lower() in ('.png', '.ico'):
            shutil.copyfile(assets / ('icon.ico' if path.suffix == '.ico' else 'icon.png'), path)
    # Windows resource metadata must retain a real executable filename.
    (destination / 'TAB-ORIGIN.txt').write_text(
        f'{title}: versão independente baseada em {original}.\n'
        'Licenças e direitos dos autores originais preservados em LICENSE-MIT, LICENSE-APACHE, NOTICE e ATTRIBUTION.md.\n'
        'Identidade visual Tab criada com OpenAI para este projeto; não é um produto Microsoft ou ArtCraft.\n')
    print(destination)

subprocess.run([sys.executable, str(ROOT / 'scripts/apply-patches.py')], check=True)

#!/usr/bin/env python3
"""Apply reproducible fixes to generated copies, preserving unknown manual changes."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
for patch in sorted((root / 'patches').glob('*craft-*.patch')):
    command = ['patch', '--batch', '--fuzz=0', '-p1', '-d', str(root / 'build' / patch.name.split('-', 1)[0]), '-i', str(patch)]
    if subprocess.run(command + ['--dry-run', '--reverse'], capture_output=True).returncode == 0:
        print(f'{patch.name}: already applied')
        continue
    preview = subprocess.run(command + ['--dry-run'], capture_output=True, text=True)
    if preview.returncode:
        raise SystemExit(f'Cannot apply {patch.name}; preserving build files.\n{preview.stdout}\n{preview.stderr}')
    subprocess.run(command, check=True)

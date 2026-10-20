# Word Tab e Excel Tab

Um pacote com duas versões independentes para Windows x64, baseadas respectivamente no WordCraft
e no GridCraft, com nomes e ícones próprios e português do Brasil como idioma
inicial. O seletor de idioma dos projetos de origem continua disponível.
As traduções existentes podem apresentar trechos em inglês.

## Desenvolvimento neste ambiente

Use o checkout existente em `/workspace/tabajara`; cada tarefa na nuvem já é
isolada, portanto não crie worktrees para a preparação.

```bash
cd /workspace/tabajara
bash scripts/setup.sh
bash scripts/build.sh
```

O setup usa Rust 1.95.0, o alvo `x86_64-pc-windows-gnu`, MinGW e NSIS. Os
pacotes Debian são autenticados pelo APT e extraídos em `/workspace/toolchain`,
sem instalação em diretórios do sistema. Os lockfiles são usados com `--locked`.
As revisões de origem estão fixadas no script. Os checkouts originais permanecem
intactos; as alterações são aplicadas a cópias em `build/`.

`prepare.py` recusa sobrescrever uma cópia existente. Para regenerá-la, preserve
primeiro qualquer alteração manual e remova explicitamente apenas a cópia
gerada desejada. O setup preserva cópias já preparadas.

## Distribuição

O instalador é gerado em `dist/`, com o nome
`word-tab-excel-tab-instalador-windows-x64.exe`. Instala os dois programas para o usuário atual, sem
solicitar privilégios de administrador, e incluem atalhos e desinstalador.
`SHA256SUMS.txt` registra os hashes dos arquivos finais.

Os instaladores personalizados não têm assinatura digital. Não são os
instaladores oficiais dos projetos de origem e não são produtos Microsoft.
Os fontes de base desta preparação são da versão de desenvolvimento 0.9.0:

| Aplicativo | Origem | Revisão |
|---|---|---|
| Word Tab | https://github.com/storytold/wordcraft | `d1b0bfc3f9dd83126b162a42b667facecb003b7f` |
| Excel Tab | https://github.com/storytold/sheetcraft (GridCraft) | `68e58a2eae462ba997a8ba5a1269e03a79b61136` |

Mantêm-se as licenças MIT/Apache-2.0 e os créditos dos projetos de origem.
A atribuição da identidade visual está em `assets/ATRIBUICAO.md`.

## Verificação

O helper `bash scripts/wine.sh caminho.exe` permite executar verificações de
Windows sob Wine no Linux. Para testar a interface, primeiro inicie um display
virtual e defina `DISPLAY=:99` e `WGPU_BACKEND=gl`. Isso não substitui a
validação da interface e da instalação em um computador Windows.

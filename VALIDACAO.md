# Verificações desta preparação

Em 20/10/2026, no ambiente Linux:

- Rust 1.95.0 e alvo Windows GNU instalados; MinGW e NSIS preparados com pacotes Debian autenticados.
- `scripts/setup.sh` executado e repetido com sucesso.
- Quatro executáveis Windows x64 compilados com `--locked --release`: Word Tab, Excel Tab e as duas ferramentas CLI.
- Onze testes existentes de `wordcraft-geom` passaram.
- `scripts/check-cli.py` passou com os executáveis Windows sob Wine: texto em português salvo em DOCX, exportação para PDF, gravação/reabertura de XLSX e fórmula com resultado `30`.
- O texto extraído do PDF preservou `Olá, Word Tab! Café e ação.`.
- Ambas as interfaces Windows abriram sob Wine/Xvfb com menus em português. `document.inspect` e `ui.screenshot` responderam; as capturas foram inspecionadas.
- Os recursos Windows identificam os produtos como `Word Tab` e `Excel Tab`; ambos usam o subsistema GUI.
- Instalador único de 64 bits, interface PortugueseBR, compilado sem avisos. Teste de estrutura confirmou os dois programas, quatro atalhos, licenças e desinstalador.
- O instalador final também foi executado sob Wine; os hashes dos dois executáveis instalados são idênticos aos dos binários validados. O hash do instalador e a integridade do ZIP de download foram conferidos.
- `install_script`, `start_skill` e os três checkouts foram salvos no rascunho da configuração do ambiente. Isso não publica o ambiente.

As primeiras tentativas de Wine exigiram configurar seus arquivos de dados e a DLL zlib. Uma execução concorrente de verificações interrompeu uma delas; o helper agora serializa os acessos ao perfil e o teste funcional completo foi repetido com sucesso.

Os checkouts originais não têm alterações rastreadas. As personalizações são reproduzidas pelo script em cópias geradas.

Não foram executadas a suíte completa `cargo xtask ci` ou validação em um computador Windows real. Os downloads foram publicados no repositório e vinculados às releases do GitHub. Os instaladores personalizados não possuem assinatura digital. As bases são código 0.9.0 em desenvolvimento; as traduções de origem ainda podem conter trechos em inglês.


## Atualização 0.9.0-tab.2 — idioma de revisão

A tela de idioma tinha uma mensagem fixa afirmando que a revisão era em inglês.
Foi substituída por um seletor de idioma de revisão, independente do idioma da
interface, com preferência persistida e aplicação explícita ao texto aberto.
As alterações de fonte estão em `patches/wordcraft-proofing.patch`; o preparo
aplica esse patch de forma repetível sem modificar os checkouts originais.

O instalador inclui os dados do dicionário brasileiro VERO, sem substituir
dicionários preexistentes nem excluir dados do usuário na desinstalação.
A origem, os hashes e as licenças estão em `dictionaries/`.

Verificações da atualização:

- Compilação de release do Word Tab e do instalador, sem avisos. Excel Tab reutilizado sem alteração.
- Aplicação do patch em uma cópia limpa confere byte a byte com o fonte compilado; reaplicação detecta que já está aplicado.
- `scripts/check-proofing.py` passou com o executável instalado pelo pacote: preferências antigas, idioma inglês/português, conversão do texto aberto, validação de tags DOCX, dicionário brasileiro real, código inválido rejeitado, persistência após reiniciar e independência do idioma da interface.
- O corretor aceitou as palavras da frase de teste em português e identificou `cazaaa` como erro ortográfico.
- Os cliques reais do seletor trocaram inglês por português. Um clique real em **Aplicar ao texto do documento** converteu o DOCX de `en-US` para `pt-BR`, incluindo a linguagem padrão e as marcações explícitas do texto.
- Capturas da tela de opções com e sem documento foram inspecionadas.
- O executável instalado confere com o hash do binário compilado.

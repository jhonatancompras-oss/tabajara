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

Não foram executadas a suíte completa `cargo xtask ci`, validação em um computador Windows real ou publicação de uma release pública. Os instaladores personalizados não possuem assinatura digital. As bases são código 0.9.0 em desenvolvimento; as traduções de origem ainda podem conter trechos em inglês.

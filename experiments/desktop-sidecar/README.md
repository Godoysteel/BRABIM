# IfcOpenShell empacotado como processo local (sidecar) — teste de viabilidade

Executado em 08/09/2026. Com a plataforma confirmada como desktop ([decisão 0006](../../docs/04-decisoes/0006-plataforma-desktop-e-retorno-ifcopenshell.md)), testa se o IfcOpenShell nativo pode ser empacotado num executável standalone (sem exigir Python instalado na máquina do usuário) e conversar com o app via um processo local de longa duração — o padrão que o Tauri chama de "sidecar".

## Abordagem

`worker.py` sobe o IfcOpenShell uma vez (pagando o custo de import só na inicialização) e depois fica lendo requisições em JSON, uma por linha, via stdin, respondendo em JSON via stdout — em vez de abrir um processo Python novo a cada edição do usuário. Recebe parâmetros reais de um cômodo (`{room: {width, depth, height, thickness, doorWidth, doorHeight, doorOffset, windowWidth, windowHeight, windowOffset, sill}}`) e monta um retângulo de 4 paredes com os 4 cantos conectados, cortando vãos reais de porta e janela via `ifcopenshell.api.feature.add_feature` (booleana de verdade, não caixas compostas), devolvendo vértices/faces de cada parede já com os furos — não mais um cenário fixo de teste. Essa evolução (incluindo porta/janela) foi integrada de ponta a ponta no app real do BRABIM (`prototipo/src-tauri/`, ver [integração](../../docs/03-arquitetura/integracao-ifcopenshell.md)) e validada primeiro no [experimento Tauri isolado](../tauri-sidecar/README.md).

Empacotado com PyInstaller (`--onefile --collect-all ifcopenshell`).

## Execução

Em `experiments/desktop-sidecar`, com Python 3.14: `python -m pip install --target .venv-libs ifcopenshell numpy pyinstaller` seguido de `PYTHONPATH=.venv-libs python -m PyInstaller --onefile --name brabim-engine --paths .venv-libs --collect-all ifcopenshell worker.py`. O executável fica em `dist/brabim-engine.exe`.

## Problemas encontrados e resolvidos

O PyInstaller analisa o código estaticamente para decidir o que empacotar, mas o `ifcopenshell.api` carrega seus submódulos dinamicamente por string (`api.run('root.create_entity', ...)` importa `ifcopenshell.api.root` em tempo de execução) — invisível para essa análise. A primeira tentativa (`--onefile` simples) gerou um executável que iniciava mas falhava em toda requisição (`No module named 'ifcopenshell.api.root'`). A flag `--collect-all ifcopenshell` resolveu isso e também um segundo problema (um arquivo de dados JSON interno do pacote que também não era detectado automaticamter).

## Resultado

| Etapa | Tempo |
|---|---|
| Iniciar o executável até sinalizar pronto (`ready`) | ~3,5 s |
| Primeira requisição (aquecimento) | ~0,1 s |
| Requisições seguintes | ~0,02–0,03 s |

Tamanho do executável: **71 MB** (Python + IfcOpenShell + NumPy, tudo incluído).

O custo de ~3,5 s acontece **uma vez**, quando o aplicativo desktop sobe (inicia o processo local e mantém aberto durante a sessão) — não a cada edição. Por edição, a resposta de ~20-30 ms é consistente com o já medido no [experimento nativo original](../ifcopenshell/README.md).

## Limites deste teste

Não testa a parte Tauri (Rust não estava disponível neste ambiente) — só valida que o motor **pode** ser empacotado como executável standalone e responder rápido como processo de longa duração. Falta: empacotamento real via Tauri sidecar, comunicação real do frontend React com esse processo (aqui foi testado só via `subprocess` do Python), tamanho final do instalador do app completo, e teste em outras versões do Windows/macOS/Linux — só testado no ambiente de desenvolvimento atual (Windows). O executável de 71 MB provavelmente pode ser reduzido usando `--onedir` em vez de `--onefile` (evita descompactar num diretório temporário a cada início, reduzindo os ~3,5 s de partida), não testado aqui.

## Conclusão

O maior risco de empacotar o IfcOpenShell — a biblioteca ser compilada/nativa e não um pacote Python puro — está resolvido: o PyInstaller consegue empacotá-la com os ajustes acima, e o padrão de processo de longa duração dá respostas rápidas o bastante para edição ao vivo. Falta fechar a ponta Tauri (instalar Rust, configurar o sidecar de verdade) para ter o caminho completo validado.

## Ponta Tauri fechada: instalador real gerado e testado (10/09/2026)

Rust (`rustup`, toolchain `stable-x86_64-pc-windows-msvc`) e o Visual Studio Build Tools (MSVC) já estavam instalados nesta máquina, sem precisar instalar nada — só faltava `~/.cargo/bin` no `PATH` da sessão.

O comando de empacotamento mudou porque o worker agora também usa `OCP` (telhado/pilares/cinta, ver [decisão 0008](../04-decisoes/0008-telhado-por-interseccao-de-planos.md)), que carrega DLLs nativas do VTK por linkagem binária sem importar o pacote Python `vtk` -- mesmo problema já investigado e resolvido em [roof-ocp.README.md](roof-ocp.README.md#peso-do-pacote--investigado-e-parcialmente-resolvido). Comando final, em `experiments/desktop-sidecar`:

```
python -m pip install --target .venv-libs ifcopenshell numpy pyinstaller cadquery-ocp
PYTHONPATH=.venv-libs python -m PyInstaller --onefile --name brabim-engine --paths .venv-libs \
  --collect-all ifcopenshell --collect-all OCP \
  --exclude-module matplotlib --exclude-module vtkmodules \
  --add-binary ".venv-libs/vtk.libs;vtk.libs" worker.py
```

Sem `--exclude-module`/`--add-binary`, o executável sobe e falha na primeira linha (`OCP/__init__.py` levanta `FileNotFoundError` procurando `vtk.libs` num diretório temporário do PyInstaller que não existe, porque `--collect-all OCP` não pega a pasta `vtk.libs`, que é um pacote irmão, não um submódulo de `OCP`). Com o comando acima, o executável sobe e responde corretamente (telhado + pilares + cinta juntos, ~0,27 s por recálculo) em **250 MB**, o mesmo tamanho já medido no experimento isolado.

Copiado para `prototipo/src-tauri/binaries/brabim-engine-x86_64-pc-windows-msvc.exe` (convenção de nome de sidecar do Tauri: sufixo do target triple; pasta agora no `.gitignore` do `src-tauri`, artefato de build de ~250 MB não pertence ao git) e então `npx tauri build` (rodado de dentro de `prototipo`, com `~/.cargo/bin` no `PATH`) compilou e empacotou de ponta a ponta pela primeira vez: ~6 min de compilação Rust (primeira vez; incremental depois), gerando `src-tauri/target/release/app.exe` (107 MB) e dois instaladores em `src-tauri/target/release/bundle/`: `msi/brabim_0.1.0_x64_en-US.msi` (346 MB) e `nsis/brabim_0.1.0_x64-setup.exe` (345 MB, o mais direto para instalar num Windows comum).

Testado de verdade: rodar `app.exe` diretamente abre a janela do BRABIM e, com "Motor real (IFC)" ligado por padrão, o app já sobe sozinho um processo `brabim-engine.exe` (confirmado via `tasklist`) -- a ponte sidecar funciona no app compilado de verdade, não só via `subprocess` de teste em Python. Não testado: instalação de fato via o `.msi`/`setup.exe` (só o `app.exe` cru), Windows sem WebView2 pré-instalado, e macOS/Linux (`externalBin` do Tauri exige um binário por plataforma-alvo, cada um com sua própria etapa de empacotamento do lado Python).

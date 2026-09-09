# Tauri chamando o IfcOpenShell como sidecar — validação de ponta a ponta

Executado em 08/09/2026. Fecha o [experimento de empacotamento](../desktop-sidecar/README.md): confirma que um app Tauri real consegue subir o executável congelado do IfcOpenShell como processo local ("sidecar") e conversar com ele via stdin/stdout, dentro de uma janela desktop de verdade.

## Pré-requisitos instalados nesta tarefa

Este ambiente de desenvolvimento não tinha Rust nem o componente C++ do Visual Studio — ambos exigidos pelo Tauri para compilar no Windows. Instalados via `winget install Rustlang.Rustup` e adicionando a carga de trabalho "Desenvolvimento para desktop com C++" ao Visual Studio já existente (exigiu elevação de administrador — não é automatizável sem alguém aprovar o prompt do Windows).

## Estrutura

Scaffold gerado por `npm create tauri-app@latest` (template vanilla + Vite, Tauri v2). O executável de `../desktop-sidecar/dist/brabim-engine.exe` foi copiado para `src-tauri/binaries/brabim-engine-x86_64-pc-windows-msvc.exe` (convenção de nome exigida pelo Tauri: `<nome>-<target-triple>.exe`) e declarado em `tauri.conf.json` como `bundle.externalBin`.

## Problemas encontrados e resolvidos

1. **`tauri-plugin-shell` não tem a feature `with-global-tauri`** — só existe no core do Tauri, não em plugins individuais. Sem ela, `window.__TAURI__.shell` não existe no template vanilla puro. Resolvido trocando o template estático por Vite (bundler de verdade), importando `@tauri-apps/plugin-shell` normalmente pelo `main.js` — caminho mais robusto de qualquer forma, e o mesmo que o protótipo React já usa.
2. **Permissão errada**: `shell:allow-execute` não cobre `Command.sidecar(...).spawn()` — o erro real (`shell.spawn not allowed`) só apareceu no log do processo Rust, não na tela do app. A permissão correta é `shell:allow-spawn`, com escopo `{"name": "binaries/brabim-engine", "sidecar": true}` em `src-tauri/capabilities/default.json`.

Nenhum dos dois problemas era óbvio pela documentação; os dois só ficaram claros tentando rodar e lendo o erro real.

## Resultado

Testado manualmente na janela do app (não automatizável sem interação humana com uma janela nativa):

```
sidecar spawned, pid 40132
[+10.189s] ready — ifcopenshell 0.8.5
[+10.435s] resultado: 0.252s, 5 paredes, 40 vértices
[+31.658s] resultado (aquecido): 0.044s, 5 paredes, 40 vértices
```

O tempo de partida (~10s) é mais alto que os ~3,5s medidos isoladamente no experimento anterior — provavelmente efeito de build debug do próprio app Tauri e/ou verificação do Windows Defender no executável recém-copiado; não investigado a fundo. O que importa está confirmado: a comunicação funciona ponta a ponta, e a resposta aquecida (44ms) é rápida o bastante para edição ao vivo.

## Ícone e tela de abertura

O ícone do app foi gerado a partir de [docs/marca/icone-robo.png](../../docs/marca/icone-robo.png) via `npm run tauri icon <caminho>` (gera todas as resoluções Windows/macOS/Linux/mobile automaticamente). A tela de abertura (`src/index.html`, elemento `#splash`) mostra [docs/marca/logo-brabim.png](../../docs/marca/logo-brabim.png) em tela cheia desde o carregamento e some (com transição) assim que a mensagem `ready` do sidecar chega — testado manualmente, funcionou como esperado.

## Loop interativo real (parâmetros de verdade, não mais cenário fixo)

`../desktop-sidecar/worker.py` deixou de rodar sempre o mesmo cenário de teste: agora recebe `{id, room:{width,depth,height,thickness}}` e monta um cômodo retangular de verdade (4 paredes com os 4 cantos conectados via `geometry.connect_path`), devolvendo os vértices/faces de cada parede. A interface (`src/index.html` + `src/main.js`) ganhou campos de largura e profundidade que, a cada mudança (com debounce de 300ms), mandam os novos parâmetros pro motor e redesenham a planta em SVG com o resultado real devolvido — não mais um valor decorativo.

Testado manualmente: mudar a largura de 5 para 8 e para 3 metros atualiza a planta corretamente, com o motor respondendo em ~30ms por edição (depois do aquecimento inicial). Este é o primeiro loop "editar → motor recalcula → tela atualiza" funcionando de ponta a ponta com dados reais, não um teste com clique manual e cenário fixo.

## Limites deste teste

Build debug, não release (o build de produção deve iniciar mais rápido). Testado só manualmente numa sessão; sem automação de teste de UI para uma janela nativa. O motivo do ~10s de partida fria não foi isolado. Falta medir o tamanho final do instalador com o executável de 71 MB do motor embutido.

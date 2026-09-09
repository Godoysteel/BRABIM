# Protótipo BRABIM

Aplicação web para avaliar seleção de paredes e edição de altura e espessura em planta e 3D. Modelo sintético de cinco paredes; valores em metros. Alterações permanecem apenas na sessão e desaparecem ao recarregar.

## Executar

Requer Node.js >=22.13.0. Execute `npm ci` e `npm run dev` nesta pasta. `npm run build` gera a versão para hospedagem. `npx tsc --noEmit` verifica os tipos.

## Escopo e limites

O editor cria até oito cômodos retangulares lado a lado, com paredes compartilhadas, portas de ligação, esquadrias externas e pisos. Permite editar medidas, desfazer, salvar no navegador e exportar/abrir projetos JSON. Arquivos antigos de cômodo único são aceitos. Planta e 3D têm enquadramento do conjunto.

Profundidade, altura e espessuras são comuns. Não há planta livre, telhado, fundação, cálculo estrutural ou IFC do modelo editado. Veja [documentação dos ambientes conectados](../docs/02-produto/ambientes-conectados.md).

## Reaproveitamento open source

Three.js: renderização, seleção por raycasting e OrbitControls (licença MIT). React e componentes shadcn/Base UI: estado e controles de interface. Dependências e versões exatas estão em package-lock.json; avisos originais permanecem nos pacotes distribuídos pelo empacotador. Não foi implementado kernel BIM próprio.

Documentação consultada: https://threejs.org/manual/en/installation.html e https://threejs.org/docs/pages/OrbitControls.html.

## Validação

O suporte WebMCP é opcional e oferece seleção de parede existente. Não houve contexto WebMCP disponível para verificar o contrato em execução. Não foram solicitados testes de interface no navegador; a validação inclui compilação, tipos e resposta HTTP local.

## GitHub Pages

Publicação pública: https://godoysteel.github.io/BRABIM/ (editor) e https://godoysteel.github.io/BRABIM/ensaios/ (resultados IFC). O comando npm run build:pages gera arquivos estáticos em dist-pages. O workflow pages.yml publica automaticamente alterações no protótipo na branch main. Não executa o motor Python online.

## App desktop (Tauri)

A plataforma final do BRABIM é desktop, não navegador ([decisão 0006](../docs/04-decisoes/0006-plataforma-desktop-e-retorno-ifcopenshell.md)). `src-tauri/` empacota esta mesma interface (React/Three.js, sem duplicação de código) numa janela nativa via [Tauri](https://tauri.app), com o motor IfcOpenShell rodando como processo local ("sidecar") — sem servidor externo.

Requer Rust (`rustup`) e, no Windows, o componente "Desenvolvimento para desktop com C++" do Visual Studio. Para rodar:

1. Gerar o executável do motor (ver [experiments/desktop-sidecar](../experiments/desktop-sidecar/README.md)) e copiá-lo para `src-tauri/binaries/brabim-engine-x86_64-pc-windows-msvc.exe` (nome exigido pelo Tauri: `<nome>-<target-triple>.exe`; o binário não é versionado, é gerado localmente).
2. `npm run tauri dev` para rodar em desenvolvimento, ou `npm run tauri build` para gerar o instalador.

Na interface, o campo **"Motor real (IFC)"** na barra de ferramentas liga o cálculo real do IfcOpenShell para o ambiente ativo (não aparece na versão web, onde o motor não está disponível). Hoje calcula só o retângulo de 4 paredes desse ambiente — porta, janela, piso e ambientes conectados continuam com a geometria demonstrativa; a integração completa é trabalho futuro.



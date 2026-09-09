# 0006 — Plataforma desktop confirmada; motor volta a ser IfcOpenShell nativo

**Data:** 08/09/2026. **Status:** direção confirmada e caminho técnico (Tauri + sidecar IfcOpenShell) validado de ponta a ponta.

## Contexto

A plataforma final do BRABIM era uma questão explicitamente em aberto desde a concepção (documento mestre, pergunta 13; [estado do projeto](../00-visao/estado-do-projeto.md), linha "Plataforma final: ainda em avaliação"). As decisões [0004](0004-wasm-nao-viavel-tempo-real.md) e [0005](0005-occt-wasm-para-encontros.md) foram tomadas assumindo implicitamente um alvo web sem servidor, o que levou a descartar o IfcOpenShell nativo (por exigir um serviço rodando em algum lugar) e adotar OCCT via WebAssembly como alternativa sem servidor.

O idealizador esclareceu que o produto final não será para navegador — será desktop.

## Decisão

Confirmar **desktop** como plataforma final, encerrando a questão em aberto. Com isso, a restrição que motivou o desvio para WASM deixa de existir: um motor Python nativo empacotado junto ao aplicativo não é "depender de outro software" no sentido de serviço externo — é código local, análogo ao que FreeCAD (Python+OCCT) e Bonsai (empacotado com Blender) já fazem.

O motor de encontros de parede volta a ser o **IfcOpenShell nativo**, não o OCCT/WASM. Critérios para a escolha: o experimento nativo original já validou 8 condições geométricas (incluindo encontros em T) em menos de 1 segundo — mais testado que o experimento OCCT, que só confirmou 1 sólido resultante sem verificação geométrica completa —, e o IfcOpenShell produz IFC de verdade, atendendo à interoperabilidade como um dos pilares do produto. O OCCT via WASM não teria caminho natural para conformidade IFC.

## Alternativas e consequências

O trabalho de integração do [experimento OCCT/WASM](../../experiments/opencascade-wasm/README.md) não é descartado como conhecimento (a técnica de união booleana continua válida e pode servir de referência ou plano B), mas deixa de ser a via adotada.

Empacotamento escolhido para o app desktop: **Tauri**, chamando o IfcOpenShell como processo local de longa duração ("sidecar"), em vez de Electron — instalador menor, sem embutir um Chromium inteiro. O [experimento de empacotamento](../../experiments/desktop-sidecar/README.md) validou a parte de maior risco: o IfcOpenShell nativo (com suas dependências compiladas) pode ser empacotado num executável standalone via PyInstaller — não é trivial (o `ifcopenshell.api` carrega módulos dinamicamente, exigindo `--collect-all` para funcionar), mas funciona. Rodando como processo de longa duração, o custo de inicialização isolado (~3,5s) acontece uma vez ao abrir o app; cada requisição depois disso responde em ~20-30ms.

O [experimento com Tauri de verdade](../../experiments/tauri-sidecar/README.md) fechou essa validação: Rust e o componente C++ do Visual Studio foram instalados nesta tarefa (exigiu aprovação manual de um prompt de administrador do Windows — não automatizável sozinho), um app Tauri mínimo foi criado, e o sidecar rodou dentro dele de ponta a ponta, com resultado real na tela: motor pronto em ~10s (build debug) e respostas de 252ms (primeira) e 44ms (aquecida). Dois problemas de configuração foram encontrados e resolvidos (permissão `shell:allow-spawn`, não `shell:allow-execute`; plugin de shell precisa de um bundler real como Vite, não do template estático puro) — documentados no experimento para não se repetirem.

O protótipo web publicado no GitHub Pages continua existindo como ferramenta de validação de interface e fluxo, não como o produto final — consistente com o que já estava registrado em [prototipo.md](../02-produto/prototipo.md) ("Isso não define a plataforma final do produto").

## Referências

[Decisão 0002](0002-reutilizacao-e-ifcopenshell.md) · [Decisão 0004](0004-wasm-nao-viavel-tempo-real.md) · [Decisão 0005](0005-occt-wasm-para-encontros.md) · [Experimento nativo](../../experiments/ifcopenshell/README.md) · [Experimento de empacotamento desktop](../../experiments/desktop-sidecar/README.md) · [Experimento Tauri completo](../../experiments/tauri-sidecar/README.md)

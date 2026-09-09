# Integração do IfcOpenShell

**Data:** 08-09/09/2026. **Status:** integrado ao app desktop real (não mais só experimento) para o retângulo básico de um ambiente; ambientes conectados e aberturas continuam com geometria demonstrativa.

## Resultado do primeiro experimento

Três cenários passaram nas oito verificações automatizadas de cada caso: modelo original, espessuras diferentes e alturas diferentes. Foram gerados IFCs e malhas; veja [procedimento, resultados e limites](../../experiments/ifcopenshell/README.md). Memória, edição sequencial de parâmetros e revisão profissional continuam pendentes. O protótipo publicado não mudou.

## Objetivo

Reutilizar a geração de geometria e encontros do IfcOpenShell no BRABIM. O usuário permanece na interface do BRABIM; não precisa abrir Revit ou Blender. A biblioteca é uma dependência técnica incorporada à solução.

O pacote 0.8.5 está em `.runtime/python`, fora do versionamento. Sua execução foi comprovada pelo experimento; isso não representa integração com a viewport nem validação abrangente de junções.

## Arquitetura a experimentar

**Edição no BRABIM → parâmetros e conexões → adaptador → IfcOpenShell → geometria e identificadores → planta e 3D.**

O adaptador deve isolar a aplicação das particularidades da API, conservar identificadores e unidades e comunicar falhas sem apresentar resultados antigos como se fossem atuais.

Para a primeira prova, gerar um arquivo e a geometria separadamente. Em seguida, avaliar um serviço Python para processamento dinâmico. A hospedagem atual da interface não está configurada para esse motor Python; não assumir que basta instalar o pacote no frontend.

Rodar o IfcOpenShell no próprio navegador via WASM foi testado e descartado para recálculo em tempo real: o cálculo da mesma cena de cinco paredes levou de 27 a 53 segundos em WASM, contra menos de 1 segundo nativo — ver [experimento](../../experiments/ifcopenshell-wasm/README.md) e [decisão 0004](../04-decisoes/0004-wasm-nao-viavel-tempo-real.md).

Isso levou a testar OCCT/WASM (união booleana de sólidos) como alternativa sem servidor — ver [experimento](../../experiments/opencascade-wasm/README.md) e [decisão 0005](../04-decisoes/0005-occt-wasm-para-encontros.md) — mas a plataforma final foi esclarecida como **desktop**, não navegador ([decisão 0006](../04-decisoes/0006-plataforma-desktop-e-retorno-ifcopenshell.md)). Em desktop, o motor Python roda embutido no próprio aplicativo, sem precisar de servidor externo; a razão original para evitar o IfcOpenShell nativo deixa de existir. O motor volta a ser o **IfcOpenShell nativo**, mantendo conformidade IFC desde o início. Falta decidir como o aplicativo desktop empacota e se comunica com esse processo Python.

Em uma futura edição desktop, o motor poderá ser empacotado localmente. Para a opção web com servidor, haverá comunicação de rede. Nenhuma dessas opções foi definida como plataforma final.

## Integração real no app (09/09/2026)

Deixou de ser só experimento isolado: `prototipo/src-tauri/` empacota a interface real do BRABIM num app Tauri, com `prototipo/lib/engine-client.ts` conversando com o sidecar do motor. Um campo **"Motor real (IFC)"** na interface liga o cálculo real do IfcOpenShell para o ambiente ativo — testado manualmente, funciona: editar largura/profundidade atualiza a planta e o 3D com a geometria calculada de verdade, não mais a demonstrativa.

Escopo desta integração: só o retângulo de 4 paredes do ambiente ativo (o mesmo caso validado no [experimento de empacotamento](../../experiments/desktop-sidecar/README.md)). Ainda não integrados ao motor: porta, janela, piso, paredes compartilhadas entre ambientes conectados e portas de ligação — esses continuam com a geometria demonstrativa do Three.js. Ligar um segundo ambiente ao motor hoje mostraria paredes duplicadas na fronteira compartilhada, já que o motor ainda não sabe que dois ambientes são vizinhos.

## Validação prevista

| Caso | Evidência necessária |
|---|---|
| Cinco paredes atuais | Elementos e relações preservados |
| Cantos em L e encontros em T | Fechamento e ausência de sobreposição indevida |
| Espessuras diferentes | Recalcular sem frestas e conferir geometria |
| Alturas e ângulos diferentes | Registrar resultados e limitações, sem presumir suporte correto |
| Edição repetida | Planta e 3D representam a mesma revisão |
| Falha do motor | Mensagem clara e último resultado identificado como anterior |

O experimento registra duração por cenário. Medições de memória, tamanho das respostas de serviço e benchmark repetido permanecem pendentes. Diego poderá conferir os casos e Paulo revisar critérios técnicos, conforme divisão proposta.

## Custos e atualizações

Não foi identificado custo de assinatura por usuário do IfcOpenShell. O planejamento deve considerar integração, testes, manutenção e processamento/armazenamento quando houver servidor. Não há orçamento mensal ou promessa de hospedagem gratuita.

Usar versão explícita, começando pelo experimento com 0.8.5; preparar dependências reproduzíveis antes da adoção. Não atualizar automaticamente o motor. Avaliar cada atualização com casos de referência, comparação de geometria, desempenho e compatibilidade; manter forma de retornar à versão anterior. Versões antigas também podem demandar correções e acompanhamento.

Os metadados locais indicam LGPLv3 ou posterior. O código de Bonsai consultado declara GPLv3 ou posterior e deve ser avaliado separadamente. A forma de distribuição e as obrigações aplicáveis ainda precisam ser analisadas; não foi aprovada uma estratégia de licenciamento do BRABIM.

## Fontes consultadas na pesquisa

- [Regeneração de paredes na API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/geometry/regenerate_wall_representation/index.html)
- [Código e aviso de licença do módulo](https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.8.0/src/ifcopenshell-python/ifcopenshell/api/geometry/regenerate_wall_representation.py)
- [Comparação inicial com alternativas](reaproveitamento-open-source.md)

As referências de código são de uma branch consultada, não um commit imutável correspondente à instalação 0.8.5. Conferir o artefato fixado ao implementar.

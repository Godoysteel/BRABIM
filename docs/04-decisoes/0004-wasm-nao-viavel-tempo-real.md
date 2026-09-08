# 0004 — WASM do IfcOpenShell descartado para recálculo em tempo real

**Data:** 08/09/2026. **Status:** resultado de experimento; decisão de arquitetura pendente sobre a alternativa.

## Contexto

Ao planejar como ligar o IfcOpenShell ao editor sem manter um servidor Python — a maior incerteza de infraestrutura registrada em [integracao-ifcopenshell.md](../03-arquitetura/integracao-ifcopenshell.md) — identificamos que o próprio projeto IfcOpenShell mantém wheels WASM oficiais (via Pyodide), o que permitiria rodar o motor inteiro no navegador do visitante, sem back-end algum. Antes de assumir essa rota, testamos.

## Experimento

[experiments/ifcopenshell-wasm](../../experiments/ifcopenshell-wasm/README.md) carregou o wheel oficial 0.8.5 e repetiu a cena de cinco paredes já validada no [experimento nativo](../../experiments/ifcopenshell/README.md). A API funciona e produz a mesma geometria. Porém o cálculo levou de 27 a 53 segundos em três execuções, contra 0,08 a 0,57 segundos no Python nativo — de 50 a mais de 100 vezes mais lento, consistente com o aviso do repositório de exemplo da própria IfcOpenShell sobre desempenho e tratamento de exceções em WASM.

## Decisão

Descartar WASM no navegador como forma de recalcular a geometria a cada edição do usuário (arrastar parede, digitar medida): a espera de dezenas de segundos por operação não é aceitável para o fluxo de edição ao vivo. WASM permanece como opção possível apenas para uma ação pontual e explícita (ex.: um botão "gerar IFC final" que o usuário aciona sabendo que vai esperar), não decidida nesta tarefa.

## Alternativas e consequências

Descartado WASM em tempo real, a alternativa que permanece é um serviço Python nativo (servidor ou função serverless) processando as edições e devolvendo geometria — essa era a hipótese original antes de investigarmos WASM, e volta a ser a mais viável conhecida. Ela implica custo e manutenção de hospedagem ainda não orçados, e latência de rede que também não foi medida. Nenhuma dessas opções foi escolhida; a decisão de arquitetura final para recálculo ao vivo continua pendente.

## Referências

[Experimento WASM](../../experiments/ifcopenshell-wasm/README.md) · [Experimento nativo](../../experiments/ifcopenshell/README.md) · [Integração planejada](../03-arquitetura/integracao-ifcopenshell.md)

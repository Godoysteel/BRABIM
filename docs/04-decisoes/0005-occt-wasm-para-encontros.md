# 0005 — OCCT via WASM como hipótese principal para encontros de parede

**Data:** 08/09/2026. **Status:** resultado de experimento promissor; ainda não integrado, testes adicionais pendentes.

## Contexto

Depois de [descartar WASM do IfcOpenShell](0004-wasm-nao-viavel-tempo-real.md) por lentidão e de o idealizador recusar tanto servidor externo quanto algoritmo de junção escrito do zero, faltava uma via que reaproveitasse software existente sem servidor. A pesquisa original de reaproveitamento já apontava o FreeCAD/Open Cascade Technology (OCCT) como parte do ecossistema a investigar, mas não tinha sido testado.

Investigação mostrou que o módulo Arch do FreeCAD já resolve encontros de parede por **união booleana de sólidos** (um sólido "hospedeiro" mais "adições"), não por uma fórmula geométrica específica para cada tipo de encontro — e que o OCCT (o kernel por trás disso) tem um binding WASM maduro e ativamente sincronizado, o [OpenCascade.js](https://ocjs.org/).

## Experimento

[experiments/opencascade-wasm](../../experiments/opencascade-wasm/README.md) modelou as mesmas cinco paredes dos experimentos anteriores como caixas 3D e uniu todas com `BRepAlgoAPI_Fuse`, sem código de junção próprio. Resultado: união completa num único sólido (incluindo os dois encontros em T), em ~600ms de carregamento do WASM mais ~250ms de cálculo — de 100 a 200 vezes mais rápido que o WASM do IfcOpenShell, e competitivo com o tempo nativo em Python, rodando inteiramente no navegador.

## Decisão

Adotar união booleana de sólidos via OCCT/WASM como **hipótese principal** para o motor de encontros de parede do BRABIM, substituindo tanto o plano de servidor com IfcOpenShell quanto a ideia de escrever um algoritmo de junção próprio. Ainda não é uma integração — faltam testar: ângulos arbitrários, aberturas de porta/janela por subtração booleana, comportamento em navegador real (o experimento rodou em Node), e o tamanho real do download (~13,9 MB com gzip, medido; ainda não otimizado nem testado em conexão lenta).

## Alternativas e consequências

Repete o padrão já estabelecido: preferir reaproveitar um motor maduro (OCCT, usado por FreeCAD) a escrever geometria própria, mesmo que isso não seja o resultado inicialmente cogitado (IfcOpenShell). A diferença central frente ao IfcOpenShell é que aqui abrimos mão da conformidade IFC nativa — OCCT não entende o formato IFC, produz sólidos genéricos; exportar para IFC exigiria uma camada própria de conversão, não resolvida por este experimento. Essa é uma troca aceita nesta decisão: geometria correta e rápida agora, interoperabilidade IFC como problema separado a resolver depois, se buscada.

A licença (LGPL-2.1) é da mesma família já registrada para o IfcOpenShell; a avaliação de obrigações de distribuição continua pendente e deve cobrir as duas.

## Referências

[Experimento OCCT/WASM](../../experiments/opencascade-wasm/README.md) · [Decisão 0004](0004-wasm-nao-viavel-tempo-real.md) · [Pesquisa de reaproveitamento](../03-arquitetura/reaproveitamento-open-source.md)

# Teste de encontros com IfcOpenShell

Executado em 08/09/2026 com IfcOpenShell 0.8.5. Usa diretamente a API de regeneração, sem implementar algoritmo próprio de junção.

## Execução

Com Python 3.12: `python -m pip install --target .runtime/python -r experiments/ifcopenshell/requirements.txt` na raiz, seguido de `python experiments/ifcopenshell/test_joins.py`.

## Resultados

Três cenários passaram: modelo original de cinco paredes, espessuras diferentes e alturas diferentes. Cada cenário verifica oito condições: cinco paredes, seis conexões, projeções válidas, ausência de sobreposição relevante em planta, distância nula entre pares conectados, alturas preservadas, estabilidade após nova regeneração e manutenção dos GUIDs.

Tolerâncias: área de sobreposição/diferença menor que 1e-7 m²; distância/altura menor que 1e-7 m. Resíduos numéricos próximos de zero são tolerados. Conferir valores individuais e tempos no [relatório JSON](results/report.json).

- [IFC original](results/baseline.ifc)
- [IFC com espessuras diferentes](results/different-thickness.ifc)
- [IFC com alturas diferentes](results/different-height.ifc)

Os JSON de cada caso contêm malhas trianguladas em coordenadas IFC (Z vertical), GUIDs e projeções extraídas das malhas. Não são capturas da viewport.

## Limites

Contato entre projeções não prova continuidade construtiva de todo o encontro. Não foram testados ângulos arbitrários, camadas de materiais diferentes, aberturas, paredes inclinadas, alterações sequenciais de parâmetros ou preservação de geometria após reabrir o IFC. Repetição avaliada: regenerar sem mudar parâmetros. Para extrusões verticais, ausência de interseção relevante nas projeções exclui sobreposição volumétrica relevante; não substitui testes de sólidos gerais.

O teste de alturas verifica a extensão vertical, não a solução construtiva acima da menor parede. A validação de Diego e Paulo permanece pendente. Tempos são de uma execução local, incluindo geração, triangulação e serialização; não são benchmark de produção. Memória ainda não foi medida.

O protótipo publicado permanece inalterado. O próximo passo é inspecionar os IFCs e integrar suas malhas às vistas.

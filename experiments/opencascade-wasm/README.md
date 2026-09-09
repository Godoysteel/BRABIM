# Encontros de parede por união booleana de sólidos (OCCT/WASM)

Executado em 08/09/2026. Testa uma terceira via para os encontros de parede, depois de [IfcOpenShell nativo](../ifcopenshell/README.md) (exige servidor) e [IfcOpenShell via WASM](../ifcopenshell-wasm/README.md) (lento demais para tempo real): usar o mesmo truque que o FreeCAD usa no seu módulo Arch — em vez de calcular a interseção geométrica de cada tipo de encontro (reto, L, T, cruz) com uma fórmula própria, modelar cada parede como um sólido 3D e deixar o motor de booleanas do CAD **unir** todos os sólidos. A união resolve L, T e cruzamentos automaticamente, sem código específico para cada caso.

## O que existe pronto

[OpenCascade.js](https://ocjs.org/) expõe o Open Cascade Technology (OCCT) — kernel B-rep usado por FreeCAD, entre outros — compilado para WebAssembly, rodando no navegador ou em Node, sem servidor. Pacote npm `opencascade.js`, licença LGPL-2.1 (mesma família da do IfcOpenShell), mantido com bindings gerados automaticamente a partir do OCCT (2069 commits no repositório, sincronizado com o projeto original).

## Execução

`npm install` seguido de `node run.mjs` nesta pasta. Repete o mesmo cenário de cinco paredes dos outros experimentos (retângulo P01-P04 mais divisória P05, formando dois encontros em T), desta vez como caixas 3D axis-aligned unidas em sequência (`BRepAlgoAPI_Fuse`), sem nenhuma fórmula de junção escrita por nós.

A biblioteca não expõe nomes de método diretamente utilizáveis a partir da documentação (os bindings são gerados e numerados por sobrecarga, ex. `BRepPrimAPI_MakeBox_3`); as assinaturas corretas foram descobertas por tentativa direta contra o binário carregado, não adivinhadas.

## Resultado

| Etapa | Tempo |
|---|---|
| Carregar o runtime WASM | ~600-625 ms |
| Unir as 5 paredes (4 operações booleanas) | ~220-235 ms |
| Triangular o sólido final | ~26-28 ms |

Três execuções, valores estáveis. O sólido final tem **1 único sólido** (`solidCount: 1`) — confirmando que a união realmente fundiu as cinco caixas nos pontos de contato, incluindo os dois encontros em T, sem intervenção nossa — e 42 faces, consistente com faces internas coincidentes terem sido removidas pela operação booleana.

Comparado ao [experimento WASM do IfcOpenShell](../ifcopenshell-wasm/README.md) (27-53 segundos para o mesmo cenário), esta abordagem é de 100 a 200 vezes mais rápida, e do lado do Python nativo (0,08-0,57 s) é comparável ou mais rápida, apesar de rodar inteiramente no navegador.

## Ressalvas importantes

- **Tamanho do arquivo WASM:** o binário completo do OpenCascade.js tem ~63 MB descomprimidos, ~13,9 MB com gzip (medido localmente; brotli, que o GitHub Pages também serve, tende a ser um pouco menor). Ainda é um download único considerável para a primeira visita — ficaria em cache depois. Uma build reduzida (o projeto de terceiros [`occt-wasm`](https://github.com/andymai/occt-wasm) anuncia ~4 MB em brotli, não testado aqui) é candidata a redução antes de produção.
- **Testado só em Node, com paredes retas e alinhadas aos eixos.** Ângulos arbitrários, aberturas (porta/janela) cortadas por subtração booleana, e o comportamento no navegador real (não só Node) ainda não foram testados.
- **Sem verificação geométrica formal** (tipo as oito verificações do experimento nativo): confirmamos que virou 1 sólido com contagem de faces plausível, não comparamos volumes ou footprints ponto a ponto.
- **Licença:** LGPL-2.1, mesma categoria já registrada para o IfcOpenShell — a mesma avaliação de obrigações de distribuição pendente se aplica aqui.

## Conclusão

Via preliminar, mas a mais promissora até agora: resolve L e T automaticamente com um motor CAD maduro e reaproveitado (não uma fórmula própria), roda inteiramente no navegador (sem servidor) e em menos de 1 segundo no total. Antes de adotar, falta medir o tamanho real do download e testar ângulos arbitrários, aberturas e o comportamento em navegador de verdade — não é ainda uma decisão de arquitetura, é a hipótese mais forte para o próximo experimento.

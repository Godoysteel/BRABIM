# Ambientes conectados — protótipo

O editor permite criar de um a oito cômodos retangulares alinhados lado a lado. Esta etapa avança sem depender da disponibilidade dos parceiros; Paulo e Diego podem avaliar posteriormente os exemplos e a usabilidade.

## Uso

1. Adicione um cômodo à direita e selecione seu nome na lista ou na planta.
2. Altere nome, largura, porta externa e janela; confirme medidas com Enter.
3. Profundidade, altura, espessura de parede e piso são comuns a todos os cômodos.
4. Confira a parede compartilhada e a porta central entre os ambientes na planta e no 3D.
5. Salve no navegador ou exporte o projeto em JSON para compartilhar. Abrir arquivo e reabrir salvo substituem o modelo atual; Desfazer recupera o anterior.

Remover um cômodo aproxima os restantes. Desfazer mantém até 50 alterações na sessão. O navegador não sincroniza dados com outros computadores. Não há salvamento automático.

## Modelo e compatibilidade

`brabim-house`, versão 1, guarda uma lista com identificador, nome e medidas de cada ambiente. Arquivos `brabim-room`, versão 1, são migrados para um projeto com um ambiente. O salvamento antigo do navegador também pode ser reaberto quando ainda não existe um projeto salvo na nova chave.

Cada divisória tem uma identificação única e pertence aos dois ambientes adjacentes. A porta de ligação mede 0,90 m e tem altura de até 2,10 m, limitada pela altura das paredes. As paredes longitudinais e os pisos terminam na mesma fronteira entre ambientes, sem volumes sobrepostos. O enquadramento 3D considera as dimensões do conjunto.

## Limites

Ainda não há planta livre, cômodos em L, pavimentos, telhado, fundação, cálculo estrutural ou exportação IFC do modelo editado. Cada cômodo mantém uma porta externa ao sul e janela ao norte. Portas de ligação têm posição central fixa. A planta representa um corte a 1,20 m.

A geometria reaproveita as primitivas Three.js e a implementação retangular existente. Esta composição restrita não substitui um motor BIM de junções genéricas. O IfcOpenShell permanece nos ensaios separados: o GitHub Pages não executa Python nem recalcula IFC.

## Verificação

Executar na pasta `prototipo`: `npx tsc --noEmit`, `npm run build:pages`, `node --experimental-strip-types scripts/test-room.mjs` e `node --experimental-strip-types scripts/test-house.mjs`.

Os testes da casa verificam migração e ida/volta do arquivo, limites e medidas inválidas, atualização global, divisórias únicas, passagem desobstruída e ausência de interseção volumétrica entre paredes e pisos no exemplo com três cômodos. A avaliação visual e de interação com usuários continua necessária.

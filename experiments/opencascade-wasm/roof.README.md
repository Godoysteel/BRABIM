# Telhado por interseção de planos (mecanismo do Revit) — validação

Executado em 09/09/2026. Testa se o mecanismo real do Revit para telhados — cada aresta do contorno recebe um plano inclinado ("define inclinação") ou fica vertical, e o telhado final é o encontro entre esses planos — pode ser reproduzido com OCCT, a mesma ferramenta já validada para [encontros de parede](README.md).

## Por que não usar straight skeleton

O straight skeleton (biblioteca `bpypolyskel`, usável sem Blender via `pip install mathutils`) resolve bem telhados de quatro águas, mas telhados de duas águas exigem pós-processamento — são dois mecanismos diferentes para dois casos. O Revit usa **um mecanismo só**: inclinação ligada/desligada por aresta. Isso bate diretamente com o que o OCCT já sabe fazer bem (interseção booleana de sólidos), sem precisar de uma biblioteca especializada em telhados.

## Abordagem testada

Para cada aresta do beiral com inclinação ligada, cria-se um plano inclinado infinito (`gp_Pln` + `BRepBuilderAPI_MakeFace` sem limites) e um semi-espaço a partir dele (`BRepPrimAPI_MakeHalfSpace`), guardando o lado onde fica o material do telhado. O sólido final é a interseção (`BRepAlgoAPI_Common`) de uma caixa alta com todos os semi-espaços das arestas inclinadas; arestas sem inclinação simplesmente não recebem corte algum, permanecendo como a face vertical da própria caixa (a empena).

Rodar: `node roof.mjs` em `experiments/opencascade-wasm` (mesma configuração do [experimento de paredes](README.md)).

## Resultado

Testado sobre um contorno de 8×5 m, beiral a 3 m:

| Configuração | Arestas inclinadas | Volume calculado | Volume conferido na mão |
|---|---|---:|---:|
| Quatro águas (hip) | norte, sul, leste, oeste | 23,750 m³ | 23,750 m³ (fórmula do prismatoide) |
| Duas águas (gable) | norte, sul | 30,000 m³ | 30,000 m³ (prisma triangular) |
| Uma água (shed) | norte | 30,000 m³ | 30,000 m³ (prisma triangular) |
| Misto (3+1) | norte, leste, oeste | 35,200 m³ | não conferido na mão, mas sólido único e válido (5 faces) |

Todas as configurações produziram um sólido único, fechado, com 5 faces (as inclinadas/verticais mais a base), sem erros geométricos. As três primeiras batem exatamente com o cálculo analítico feito à parte. Tempo total das 4 configurações: ~650ms incluindo o carregamento do WASM (~600ms) — o cálculo de cada telhado individual é da ordem de poucos milissegundos, mesma faixa já medida para paredes.

## Conclusão

O mesmo mecanismo (arestas com/sem inclinação + interseção de semi-espaços) reproduz quatro águas, duas águas, uma água e combinações mistas sem código especial para cada caso — como o Revit faz, e sem precisar de uma biblioteca externa dedicada a telhados. Isso reaproveita o OCCT já validado para paredes, em vez de somar mais uma dependência (`bpypolyskel`) que só resolveria parte do problema.

## Limites deste teste

Testado só sobre um contorno retangular simples (não um L ou polígono arbitrário com reentrâncias, onde arestas côncavas podem gerar planos que não se comportam da mesma forma). Não testado: beirais com balanço (overhang) além da parede, platibandas, telhados com águas de inclinações diferentes entre si, nem a extração da malha final para desenho (o teste só mede volume e contagem de faces, não converte para vértices/faces prontos para a viewport). Falta decidir como essa geometria OCCT entraria no motor real (`prototipo/src-tauri`, hoje puramente IfcOpenShell/Python) — não resolvido aqui.

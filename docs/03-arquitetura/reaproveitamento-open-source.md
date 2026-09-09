# Reaproveitamento open source — encontros de paredes

**Pesquisa:** 08/09/2026. **Status:** inspeção de documentação e código; sem teste de integração.

## Diretriz do projeto

Pesquisar soluções existentes antes de implementar funcionalidades técnicas. Preferir integrar componentes adequados, depois adaptar quando necessário, e desenvolver uma solução própria apenas quando houver lacuna demonstrada. A diferenciação do BRABIM será a experiência simples para o usuário.

## Candidatos inspecionados

### IfcOpenShell — prioridade para prova de conceito

A função `ifcopenshell.api.geometry.regenerate_wall_representation` reconstrói paredes considerando conexões, recortes e encontros de topo e meia-esquadria. Usa eixos, camadas e prioridades, com relações IFC entre elementos. O arquivo consultado declara LGPL-3.0-or-later.

É uma implementação Python com dependências do IfcOpenShell e NumPy, não um módulo que possa ser importado diretamente no frontend atual. Próximo experimento: executar separadamente, gerar um exemplo IFC e verificar a geometria antes de decidir integração por serviço ou outra arquitetura. Não assumir execução no ambiente atual de hospedagem.

Fontes: [API oficial](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/geometry/regenerate_wall_representation/index.html), [implementação e licença do arquivo](https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.8.0/src/ifcopenshell-python/ifcopenshell/api/geometry/regenerate_wall_representation.py).

### Bonsai — fluxo BIM e referência de integração

Documenta ferramentas de extensão, encontro de topo e meia-esquadria. O módulo de paredes inspecionado depende de Blender e IfcOpenShell e declara GPL-3.0-or-later. Avaliar separadamente do IfcOpenShell: não assumir uma licença única para todo o ecossistema.

Fontes: [modelagem de paredes, documentação instável](https://docs-unstable.bonsaibim.org/guides/authoring/basic_modeling/creating_walls.html), [módulo de paredes](https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.8.0/src/bonsai/bonsai/bim/module/model/wall.py).

### OCCT (via OpenCascade.js) — escolha atual, testada

O FreeCAD resolve encontros de parede no seu módulo Arch por união booleana de sólidos (um sólido "hospedeiro" mais "adições"), não por uma fórmula de junção específica por caso. O motor por trás disso, Open Cascade Technology (OCCT), tem um binding WebAssembly maduro e ativamente sincronizado com o projeto original: [OpenCascade.js](https://ocjs.org/) (pacote npm `opencascade.js`, LGPL-2.1). Testado em [experimento próprio](../../experiments/opencascade-wasm/README.md): a mesma cena de cinco paredes com dois encontros em T uniu-se corretamente num único sólido em menos de 1 segundo, rodando no navegador. Ver [decisão 0005](../04-decisoes/0005-occt-wasm-para-encontros.md). Pendências: tamanho do download (~14 MB comprimido), ângulos arbitrários, aberturas e teste em navegador real, não só Node.

Bonsai foi descartado como candidato direto (não como referência de estudo): depende de Blender rodando como aplicativo desktop, não é embarcável numa página web de forma alguma, independente de servidor ou não. FreeCAD tem o mesmo problema como aplicativo — o que se aproveita dele é o OCCT isoladamente (via OpenCascade.js), não o FreeCAD em si.

### Blueprint3D — bissetriz, mas só resolve cantos em L

O arquivo `half_edge.ts` calcula extremidades internas e externas a partir de paredes adjacentes, por bissetriz angular entre duas paredes que se encontram num vértice. A implementação original usa TypeScript antigo, jQuery e APIs antigas do Three.js. Sua licença é MIT. Inspeção posterior do código confirmou que a estrutura assume exatamente duas paredes por vértice: cantos em L funcionam para qualquer ângulo, mas **não há suporte a encontros em T ou cruzamentos** (três ou mais paredes no mesmo ponto), nem a espessuras diferentes no mesmo encontro. Como o BRABIM já depende de encontros em T (portas de ligação entre ambientes), esse candidato resolve só parte do problema — descartado em favor do OCCT (união booleana de sólidos, que resolve L e T sem distinção de caso).

Fontes: [código de HalfEdge](https://raw.githubusercontent.com/furnishup/blueprint3d/master/src/model/half_edge.ts), [licença](https://raw.githubusercontent.com/furnishup/blueprint3d/master/LICENSE.txt).

## Critérios para o experimento

1. Fixar uma versão ou commit e conferir licença e dependências desse artefato.
2. Reproduzir cantos em L e encontros em T do exemplo atual.
3. Variar espessuras, alturas e ângulos; conferir fechamento e volumes sobrepostos.
4. Verificar seleção independente e coerência entre planta e 3D.
5. Registrar limitações e custo de integração antes de alterar o protótipo publicado.

Nenhuma biblioteca foi integrada nesta pesquisa. As junções do protótipo permanecem como estavam. A licença identificada não substitui a avaliação das obrigações do modo de distribuição escolhido.

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

### Blueprint3D — alternativa próxima ao frontend

O arquivo `half_edge.ts` calcula extremidades internas e externas a partir de paredes adjacentes. A implementação original usa TypeScript antigo, jQuery e APIs antigas do Three.js. Sua licença é MIT. É candidato a adaptação, não adoção imediata: a rotina inspecionada usa bissetriz e deslocamento da própria parede, portanto espessuras diferentes e encontros em T precisam de ensaios específicos.

Fontes: [código de HalfEdge](https://raw.githubusercontent.com/furnishup/blueprint3d/master/src/model/half_edge.ts), [licença](https://raw.githubusercontent.com/furnishup/blueprint3d/master/LICENSE.txt).

## Critérios para o experimento

1. Fixar uma versão ou commit e conferir licença e dependências desse artefato.
2. Reproduzir cantos em L e encontros em T do exemplo atual.
3. Variar espessuras, alturas e ângulos; conferir fechamento e volumes sobrepostos.
4. Verificar seleção independente e coerência entre planta e 3D.
5. Registrar limitações e custo de integração antes de alterar o protótipo publicado.

Nenhuma biblioteca foi integrada nesta pesquisa. As junções do protótipo permanecem como estavam. A licença identificada não substitui a avaliação das obrigações do modo de distribuição escolhido.

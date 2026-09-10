# 0008 — Telhado por interseção de planos (mecanismo do Revit), não straight skeleton

**Data:** 09-10/09/2026. **Status:** integrado ao app desktop real (não mais só experimento), para o retângulo de um ambiente isolado.

## Contexto

Ao discutir telhado como próximo desafio de geometria depois de paredes/porta/janela, a hipótese inicial (registrada em conversa, não em decisão anterior) era usar straight skeleton (`bpypolyskel`, usável sem Blender). Essa técnica resolve bem quatro águas, mas exige pós-processamento para duas águas — dois mecanismos para dois casos.

Investigação de como o Revit resolve telhados mostrou um mecanismo mais simples: a ferramenta "telhado por contorno" liga ou desliga "define inclinação" por aresta do contorno; onde há inclinação, forma-se um plano inclinado partindo daquela aresta; o telhado final é o encontro entre todos os planos (e as arestas sem inclinação viram empena). Quatro águas e duas águas saem do mesmo mecanismo, só variando quais arestas têm inclinação.

## Decisão

Adotar como hipótese principal para telhados a **interseção de semi-espaços via OCCT** (mesma ferramenta já validada para paredes, [decisão 0005](0005-occt-wasm-para-encontros.md)), reproduzindo o mecanismo do Revit, em vez de adotar uma biblioteca de straight skeleton.

[Experimento](../../experiments/opencascade-wasm/roof.README.md) validou quatro configurações sobre um contorno retangular (quatro águas, duas águas, uma água, e uma mista de três águas mais uma empena) — todos os sólidos resultantes são únicos, fechados e geometricamente válidos; três deles tiveram o volume conferido contra cálculo analítico feito à parte, com correspondência exata.

## Alternativas e consequências

`bpypolyskel`/straight skeleton continua conhecida e documentada como alternativa (ver conversa registrada e pesquisa externa), mas não foi escolhida: exigiria manter dois mecanismos (skeleton para quatro águas, gambiarra para duas águas) em vez de um só, e seria mais uma dependência nova em vez de reaproveitar o OCCT já testado.

Esta era inicialmente uma validação geométrica isolada, sem resposta para como o sólido calculado em OCCT entraria no motor real (Python/IfcOpenShell). Um [segundo experimento](../../experiments/desktop-sidecar/roof-ocp.README.md) fechou essa lacuna: `cadquery-ocp` (o binding OCCT usado pelo CadQuery, publicado no PyPI — cuidado, não confundir com o pacote `OCP` do PyPI, que é outro projeto sem relação) roda nativamente em Python, no mesmo processo que o `ifcopenshell`, sem conflito, com resultado numericamente idêntico ao já obtido em JavaScript/WASM. Isso significa que o motor pode ganhar OCCT como dependência adicional dentro do mesmo `worker.py`, sem precisar de WASM nem de um segundo processo.

Ponto de atenção descoberto e parcialmente resolvido: a instalação padrão de `cadquery-ocp` traz VTK (~314 MB) e matplotlib (~33 MB) como dependências. Investigação mostrou que matplotlib e o pacote Python do VTK não são de fato necessários — o OCP só precisa que a pasta de DLLs nativas do VTK (`vtk.libs`, ~264 MB) exista no disco, por causa de linkagem binária, não por uso real dessas bibliotecas. Testado com `--exclude-module` no PyInstaller: o executável final ficou em **250 MB** (contra 71 MB sem telhado), funcionando corretamente — bem menor que os ~450 MB que seriam sem essa exclusão, mas ainda um salto grande, já que as DLLs nativas do VTK continuam sendo custo fixo enquanto o `cadquery-ocp` depender delas.

Um [terceiro experimento](../../experiments/desktop-sidecar/roof-to-ifc.README.md) fechou a última lacuna técnica: não há ponte direta documentada entre `TopoDS_Shape` (OCCT) e uma representação IFC, mas não precisa — basta triangular o sólido (mesma técnica do experimento em JS) e entregar vértices/triângulos para `ifcopenshell.api.geometry.add_mesh_representation`, que monta a representação sozinho. Testado de ponta a ponta: sólido do telhado calculado pelo OCP virou uma entidade `IfcRoof` de verdade, escrita num arquivo `.ifc` válido (IFC4, `IfcPolygonalFaceSet`), e relida corretamente pelo motor de geometria do próprio `ifcopenshell` — altura da cumeeira bateu exatamente com o esperado (3 m de beiral + inclinação até 4,5 m).

## Integração real no app e dois bugs de alinhamento (10/09/2026)

O `worker.py` (mesmo processo que já resolve paredes/porta/janela, ver [integração do IfcOpenShell](../03-arquitetura/integracao-ifcopenshell.md)) passou a calcular o telhado de verdade para o ambiente ativo, ligado por um campo "Telhado (4 águas)" na interface. Dois bugs de alinhamento entre parede e telhado apareceram nesse processo e foram corrigidos:

**Parede atravessando o telhado (face inferior no lugar errado).** A primeira versão modelava o telhado como um único corte plano na altura do beiral, o que ou apagava o beiral (se o corte cobrisse o contorno estendido) ou deixava a região de beiral inteiramente sólida até o chão (se o corte cobrisse só o contorno original). A correção definitiva trocou a técnica: o telhado passou a ser uma casca de espessura real — dois sólidos (`_roof_mass`) idênticos exceto pela altura de ancoragem, um subtraído do outro (`BRepAlgoAPI_Cut`). Uma primeira tentativa dessa casca ainda saiu invertida (face de baixo ancorada `thickness` abaixo do beiral, em vez de exatamente nele), deixando os 10 cm de topo da parede dentro do sólido do telhado — só ficou visível com números exatos, não com captura de tela: o [painel de depuração](#painel-de-depuração-para-bugs-de-geometria) construído nesta mesma sessão exportou os vértices reais e mostrou parede indo até z=2,8 com a face inferior do telhado em z=2,7 na mesma região. Corrigido invertendo as âncoras: a face de baixo (contato com a parede) fica exatamente em `eave_height`; a face de cima (visível) fica `thickness` acima.

**Quina da parede fora do lugar exato (offset de meia espessura).** Depois do primeiro bug corrigido, o usuário definiu o critério exato desejado: "a quina da parede deveria coincidir com a aresta inferior do encontro das águas" — ou seja, o ponto de beiral zero (sem inclinação ainda) do telhado deve cair exatamente na quina externa da parede, nem para dentro nem para fora. O `build_room` estava passando `width`/`depth` (medidas internas livres do ambiente) direto para `build_roof`, mas a face externa real da parede fica meia espessura further out — a quina caía `thickness/2` para dentro da zona de beiral. Corrigido chamando `build_roof(..., w + t, d + t, ...)`, isto é, usando a medida externa da parede (medida livre + espessura) como referência do telhado. Verificado empiricamente (não só algebricamente) em três conjuntos de dimensões diferentes (5×4×0,2 / 7×3×0,15 / 3,5×6×0,25 m), com requisições de diagnóstico a beiral zero: em todos os casos a quina externa da parede caiu exatamente em `z = eave_height` na face inferior do telhado, confirmando que a correção não depende do caso de teste original.

## Painel de depuração para bugs de geometria

Como não é possível ver a janela nativa do Tauri diretamente, os dois bugs acima só foram diagnosticados com precisão depois de construir, a pedido do usuário, um painel de ferramentas dedicado no editor (`prototipo/app/room-editor.tsx` + `viewport.tsx`):

- **Coordenadas por clique**: clicar em qualquer superfície do 3D registra o ponto exato (x, profundidade, altura) num histórico dos últimos 5 cliques, com a distância até o clique anterior.
- **Exportação de depuração em JSON**: baixa um arquivo com os parâmetros do ambiente ativo e os vértices/faces crus de cada malha exibida (paredes, telhado) — permite ler os números exatos de qualquer bug de geometria em vez de tentar interpretar uma captura de tela.
- **Wireframe**: alterna todos os materiais para malha de arame, útil para ver sobreposições escondidas atrás de faces sólidas.
- **Corte de seção**: um plano de recorte do Three.js (`localClippingEnabled`) esconde metade frontal do modelo, permitindo olhar direto para dentro de uma junção sem girar a câmera.

Essas ferramentas resolveram em uma sessão dois bugs reais que provavelmente exigiriam várias rodadas de captura de tela e adivinhação.

O que resta agora é trabalho de produto, não mais dúvida de viabilidade técnica: decidir o contorno a partir do modelo de ambientes do BRABIM em vez de um retângulo fixo de teste (ainda só suporta um ambiente isolado, retangular e alinhado aos eixos — sem ambientes conectados nem formato em L), expor os controles de inclinação/beiral por aresta na interface (hoje fixos em `{slope:.6, slopedEdges:['north','south','east','west']}`), testar águas com inclinações diferentes entre si, e resolver o peso do instalador (~250 MB) antes de considerar isso pronto.

## Referências

[Experimento de validação (JS/WASM)](../../experiments/opencascade-wasm/roof.README.md) · [Experimento de integração (Python/OCP + IfcOpenShell)](../../experiments/desktop-sidecar/roof-ocp.README.md) · [Experimento da ponte para IFC real](../../experiments/desktop-sidecar/roof-to-ifc.README.md) · [Decisão 0005 — OCCT para paredes](0005-occt-wasm-para-encontros.md) · [Decisão 0006 — motor nativo desktop](0006-plataforma-desktop-e-retorno-ifcopenshell.md)

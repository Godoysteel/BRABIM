# 0008 — Telhado por interseção de planos (mecanismo do Revit), não straight skeleton

**Data:** 09/09/2026. **Status:** geometria, empacotamento e ponte para IFC real todos validados por experimento; não integrada ao produto (falta trabalho de produto, não de viabilidade técnica).

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

O que resta agora é trabalho de produto, não mais dúvida de viabilidade técnica: decidir o contorno a partir do modelo de ambientes do BRABIM em vez de um retângulo fixo de teste, expor os controles de inclinação por aresta na interface, testar contornos não retangulares (L, reentrâncias) e águas com inclinações diferentes entre si, e resolver o peso do instalador (~250 MB) antes de considerar isso pronto.

## Referências

[Experimento de validação (JS/WASM)](../../experiments/opencascade-wasm/roof.README.md) · [Experimento de integração (Python/OCP + IfcOpenShell)](../../experiments/desktop-sidecar/roof-ocp.README.md) · [Experimento da ponte para IFC real](../../experiments/desktop-sidecar/roof-to-ifc.README.md) · [Decisão 0005 — OCCT para paredes](0005-occt-wasm-para-encontros.md) · [Decisão 0006 — motor nativo desktop](0006-plataforma-desktop-e-retorno-ifcopenshell.md)

# 0008 — Telhado por interseção de planos (mecanismo do Revit), não straight skeleton

**Data:** 09/09/2026. **Status:** hipótese geométrica e caminho de integração com o motor real ambos validados por experimento; não integrada ao produto.

## Contexto

Ao discutir telhado como próximo desafio de geometria depois de paredes/porta/janela, a hipótese inicial (registrada em conversa, não em decisão anterior) era usar straight skeleton (`bpypolyskel`, usável sem Blender). Essa técnica resolve bem quatro águas, mas exige pós-processamento para duas águas — dois mecanismos para dois casos.

Investigação de como o Revit resolve telhados mostrou um mecanismo mais simples: a ferramenta "telhado por contorno" liga ou desliga "define inclinação" por aresta do contorno; onde há inclinação, forma-se um plano inclinado partindo daquela aresta; o telhado final é o encontro entre todos os planos (e as arestas sem inclinação viram empena). Quatro águas e duas águas saem do mesmo mecanismo, só variando quais arestas têm inclinação.

## Decisão

Adotar como hipótese principal para telhados a **interseção de semi-espaços via OCCT** (mesma ferramenta já validada para paredes, [decisão 0005](0005-occt-wasm-para-encontros.md)), reproduzindo o mecanismo do Revit, em vez de adotar uma biblioteca de straight skeleton.

[Experimento](../../experiments/opencascade-wasm/roof.README.md) validou quatro configurações sobre um contorno retangular (quatro águas, duas águas, uma água, e uma mista de três águas mais uma empena) — todos os sólidos resultantes são únicos, fechados e geometricamente válidos; três deles tiveram o volume conferido contra cálculo analítico feito à parte, com correspondência exata.

## Alternativas e consequências

`bpypolyskel`/straight skeleton continua conhecida e documentada como alternativa (ver conversa registrada e pesquisa externa), mas não foi escolhida: exigiria manter dois mecanismos (skeleton para quatro águas, gambiarra para duas águas) em vez de um só, e seria mais uma dependência nova em vez de reaproveitar o OCCT já testado.

Esta era inicialmente uma validação geométrica isolada, sem resposta para como o sólido calculado em OCCT entraria no motor real (Python/IfcOpenShell). Um [segundo experimento](../../experiments/desktop-sidecar/roof-ocp.README.md) fechou essa lacuna: `cadquery-ocp` (o binding OCCT usado pelo CadQuery, publicado no PyPI — cuidado, não confundir com o pacote `OCP` do PyPI, que é outro projeto sem relação) roda nativamente em Python, no mesmo processo que o `ifcopenshell`, sem conflito, com resultado numericamente idêntico ao já obtido em JavaScript/WASM. Isso significa que o motor pode ganhar OCCT como dependência adicional dentro do mesmo `worker.py`, sem precisar de WASM nem de um segundo processo.

Ponto de atenção descoberto: a instalação padrão de `cadquery-ocp` traz VTK (~314 MB) e matplotlib (~33 MB) como dependências, aparentemente só usadas por um recurso de visualização que o BRABIM não usa — isso pode inflar bastante o executável final se não for excluído no empacotamento.

Ainda falta: converter o sólido do OCCT em uma entidade IFC real (`IfcRoof`) dentro do arquivo que o `ifcopenshell` já monta — não há uma ponte direta documentada entre `TopoDS_Shape` e uma representação IFC, provavelmente exigindo triangular o sólido e construir a representação a partir de vértices/faces. Também falta extrair a malha para desenho na viewport, testar contornos não retangulares (L, reentrâncias) e telhados com águas de inclinações diferentes entre si, e resolver o peso de VTK/matplotlib no instalador.

## Referências

[Experimento de validação (JS/WASM)](../../experiments/opencascade-wasm/roof.README.md) · [Experimento de integração (Python/OCP + IfcOpenShell)](../../experiments/desktop-sidecar/roof-ocp.README.md) · [Decisão 0005 — OCCT para paredes](0005-occt-wasm-para-encontros.md) · [Decisão 0006 — motor nativo desktop](0006-plataforma-desktop-e-retorno-ifcopenshell.md)

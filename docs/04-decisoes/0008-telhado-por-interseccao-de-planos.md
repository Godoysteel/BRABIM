# 0008 — Telhado por interseção de planos (mecanismo do Revit), não straight skeleton

**Data:** 09/09/2026. **Status:** hipótese validada por experimento; não integrada ao produto.

## Contexto

Ao discutir telhado como próximo desafio de geometria depois de paredes/porta/janela, a hipótese inicial (registrada em conversa, não em decisão anterior) era usar straight skeleton (`bpypolyskel`, usável sem Blender). Essa técnica resolve bem quatro águas, mas exige pós-processamento para duas águas — dois mecanismos para dois casos.

Investigação de como o Revit resolve telhados mostrou um mecanismo mais simples: a ferramenta "telhado por contorno" liga ou desliga "define inclinação" por aresta do contorno; onde há inclinação, forma-se um plano inclinado partindo daquela aresta; o telhado final é o encontro entre todos os planos (e as arestas sem inclinação viram empena). Quatro águas e duas águas saem do mesmo mecanismo, só variando quais arestas têm inclinação.

## Decisão

Adotar como hipótese principal para telhados a **interseção de semi-espaços via OCCT** (mesma ferramenta já validada para paredes, [decisão 0005](0005-occt-wasm-para-encontros.md)), reproduzindo o mecanismo do Revit, em vez de adotar uma biblioteca de straight skeleton.

[Experimento](../../experiments/opencascade-wasm/roof.README.md) validou quatro configurações sobre um contorno retangular (quatro águas, duas águas, uma água, e uma mista de três águas mais uma empena) — todos os sólidos resultantes são únicos, fechados e geometricamente válidos; três deles tiveram o volume conferido contra cálculo analítico feito à parte, com correspondência exata.

## Alternativas e consequências

`bpypolyskel`/straight skeleton continua conhecida e documentada como alternativa (ver conversa registrada e pesquisa externa), mas não foi escolhida: exigiria manter dois mecanismos (skeleton para quatro águas, gambiarra para duas águas) em vez de um só, e seria mais uma dependência nova em vez de reaproveitar o OCCT já testado.

Esta é uma validação geométrica isolada, não uma integração: falta decidir como o sólido calculado em OCCT entra no motor real do produto (hoje `prototipo/src-tauri` roda IfcOpenShell/Python nativo, sem OCCT direto), extrair a malha para desenho na viewport, e testar contornos não retangulares (L, reentrâncias) e telhados com águas de inclinações diferentes entre si.

## Referências

[Experimento de validação](../../experiments/opencascade-wasm/roof.README.md) · [Decisão 0005 — OCCT para paredes](0005-occt-wasm-para-encontros.md) · [Decisão 0006 — motor nativo desktop](0006-plataforma-desktop-e-retorno-ifcopenshell.md)

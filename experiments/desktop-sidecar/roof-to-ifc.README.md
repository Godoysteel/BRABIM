# Sólido do OCCT vira `IfcRoof` de verdade

Executado em 09/09/2026. Fecha a última lacuna deixada pela [validação OCCT+IfcOpenShell no mesmo processo](roof-ocp.README.md): o sólido calculado pelo OCP consegue mesmo virar uma entidade IFC real, gravável no mesmo arquivo que as paredes?

## Caminho encontrado

`ifcopenshell.api.geometry.add_mesh_representation` aceita vértices e faces brutos (qualquer polígono, não precisa ser triângulo) e monta a representação IFC sozinho — não existe uma ponte direta documentada entre `TopoDS_Shape` (OCCT) e uma entidade IFC, mas não precisa: basta triangular o sólido (mesma técnica já usada no [experimento em JavaScript](../opencascade-wasm/README.md) — `BRepMesh_IncrementalMesh` + percorrer `BRep_Tool.Triangulation` de cada face) e entregar os vértices/triângulos pra esse helper.

## Teste

`roof_to_ifc.py`: monta o telhado de quatro águas (mesmo do [experimento anterior](roof-ocp.README.md)) com OCP, triangula, cria um `IfcRoof` de verdade dentro de um `ifcopenshell.file`, escreve o arquivo `.ifc`, e — mais importante — **lê de volta** a geometria desse `IfcRoof` usando o motor de geometria do próprio `ifcopenshell` (não o OCP), pra confirmar que o resultado é um IFC válido de verdade, não só um arquivo que parece certo.

Executar: `PYTHONPATH=.venv-libs python roof_to_ifc.py` em `experiments/desktop-sidecar`.

## Resultado

```
triangulated: 18 vertices, 8 triangles (0.028s)
round-trip via ifcopenshell.geom: 6 vertex coords, 8 triangles
z range: 3.0 .. 4.500000000000001 (expect 0..3 eave + slope)
wrote results_roof_ifc.ifc ifc_class of roof entity: IfcRoof
```

A altura bate exatamente com o esperado (beiral a 3 m, cumeeira a 3 + 0,6×2,5 = 4,5 m). O arquivo gerado é um IFC4 STEP válido, com uma entidade `IFCROOF` de verdade contendo um `IFCPOLYGONALFACESET` (representação do tipo `Tessellation`) — inspecionável em qualquer visualizador IFC, não é um formato inventado pelo BRABIM.

Curiosidade: o motor de geometria do `ifcopenshell` (ao reler o `IfcRoof` para gerar a malha de exibição) devolveu só 6 vértices para as 8 triângulos, contra os 18 vértices originais da triangulação do OCCT — ele solda os pontos coincidentes automaticamente ao processar a geometria, mesmo o arquivo em si guardando os 18 pontos "crus" sem essa otimização.

## Conclusão

A cadeia completa está provada: **contorno da casa → OCCT (planos + booleana) → triangulação → `IfcRoof` real → arquivo IFC válido → geometria relida corretamente**. Faltam apenas os passos de produto (não geometria): decidir o contorno a partir do modelo de ambientes do BRABIM em vez de um retângulo fixo, oferecer os controles de inclinação por aresta na interface, e resolver o peso do instalador (~250 MB, ver [experimento anterior](roof-ocp.README.md)) antes de considerar isso pronto para uso.

## Limites deste teste

Testado só com o telhado de quatro águas sobre um retângulo simples; não testado com duas águas, misto, contornos em L, nem múltiplos telhados no mesmo arquivo. A malha final é sempre triangulada (não preserva as faces originais como polígonos maiores, ex. um retângulo vira 2 triângulos) — isso é válido em IFC, mas gera mais dados do que o estritamente necessário; não investigado se vale a pena extrair as faces planas originais em vez de triangular tudo.

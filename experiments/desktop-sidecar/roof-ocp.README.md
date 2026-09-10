# OCCT em Python (OCP) junto com o IfcOpenShell, no mesmo processo

Executado em 09/09/2026. Fecha a dúvida arquitetural deixada pela [validação do telhado em JS/WASM](../opencascade-wasm/roof.README.md): dá pra rodar OCCT nativamente em Python, no mesmo processo que já roda o motor real (`worker.py`), sem precisar de WASM nem de dois processos separados?

## Descoberta: nome ambíguo no PyPI

`pip install pythonocc-core` não tem wheel no PyPI (é distribuído majoritariamente via conda, que não estava disponível neste ambiente). A primeira tentativa alternativa, `pip install OCP`, instalou com sucesso mas é **um pacote completamente diferente** ("Open Collaboration Platform", de outro autor) — nome igual, projeto sem relação nenhuma com geometria 3D. O binding certo (usado pelo CadQuery e pelo build123d) está publicado como **`cadquery-ocp`** no PyPI, que ao instalar disponibiliza o módulo `import OCP`. Vale conferir o nome do pacote (não só o nome do módulo importado) antes de assumir que instalou a coisa certa.

## Teste

`roof_ocp.py` reproduz exatamente o [experimento em JavaScript](../opencascade-wasm/roof.mjs) (mesmo mecanismo de telhado por interseção de semi-espaços), mas em Python, com `ifcopenshell` importado no mesmo processo — antes, depois, e intercalado com o uso do OCP — para confirmar que os dois convivem sem conflito de símbolos ou DLLs.

Executar: `PYTHONPATH=.venv-libs python roof_ocp.py` em `experiments/desktop-sidecar`, com `cadquery-ocp` instalado em `.venv-libs`.

## Resultado

```
Hip (4 aguas)    -> faces: 5 volume: 23.750
Gable (2 aguas)  -> faces: 5 volume: 30.000
Shed (1 agua)    -> faces: 5 volume: 30.000
total seconds: 0.181
ifcopenshell still usable: <ifcopenshell.file.file object at ...>
```

Os volumes batem **exatamente** com os já calculados no experimento em JavaScript/WASM — duas implementações independentes do OCCT (embind/WASM vs pybind11/nativo) chegando ao mesmo resultado. `ifcopenshell` funcionou normalmente antes, depois e importado em qualquer ordem com o OCP, sem erro. O tempo total (0,18s) é bem menor que a versão WASM (~550ms), consistente com não ter o custo de carregar um runtime WebAssembly.

## Ponto de atenção: peso do pacote

`cadquery-ocp` sozinho ocupa ~109 MB, mas a instalação padrão via pip também traz **VTK (~314 MB) e matplotlib (~33 MB)** como dependências — aparentemente usados só por um recurso de visualização (`cadquery-ocp-proxy`) que não precisamos, já que o BRABIM não usa essas bibliotecas para desenhar nada. Se este caminho for adotado, vale investigar como excluir VTK/matplotlib do executável final (via `--exclude-module` do PyInstaller, ou uma forma de instalar só o núcleo do OCP sem o proxy) antes de assumir esses ~350 MB extras no instalador.

## Conclusão

A pergunta em aberto ("como o OCCT e o IfcOpenShell se encaixam no mesmo motor?") está respondida: rodam juntos, no mesmo processo Python, sem conflito, com resultado numericamente idêntico ao já validado em JS. O próximo passo (não feito aqui) é converter o sólido calculado pelo OCP em entidades IFC reais (`IfcRoof`) dentro do arquivo que o `ifcopenshell` já está montando — provavelmente triangulando o sólido do OCP e construindo a representação a partir dos vértices/faces, já que não há uma ponte direta documentada entre um `TopoDS_Shape` do OCCT e uma entidade IFC.

## Limites deste teste

Não testado: conversão do sólido OCP em entidade IFC de verdade, tamanho do executável final com essa dependência extra, e se dá pra remover VTK/matplotlib sem quebrar o `cadquery-ocp`. Mesma ressalva do teste em JS quanto a contornos não retangulares e águas com inclinações diferentes entre si.

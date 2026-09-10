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

## Peso do pacote — investigado e parcialmente resolvido

`cadquery-ocp` sozinho ocupa ~109 MB; a instalação padrão via pip também traz VTK (~314 MB: ~264 MB de DLLs nativas + ~50 MB de pacote Python) e matplotlib (~33 MB) como dependências declaradas.

Investigação mostrou que **o pacote Python do VTK e o matplotlib não são realmente necessários** — o próprio `OCP/__init__.py` só precisa que a pasta `vtk.libs` (as DLLs nativas, ~264 MB) exista no disco, porque o binário compilado do OCP está linkado contra elas; ele nunca importa o pacote `vtk` do Python nem o `matplotlib` em si (isso deve vir só de algum recurso auxiliar do `cadquery-ocp-proxy`, não usado aqui). Testado com sucesso:

1. `pip install --no-deps cadquery-ocp cadquery-ocp-proxy` (evita baixar VTK/matplotlib automaticamente).
2. Copiar manualmente a pasta `vtk.libs` (gerada por uma instalação completa do pacote `vtk`) para junto do OCP.
3. Congelar com PyInstaller passando `--exclude-module matplotlib --exclude-module vtkmodules` e `--add-binary ".../vtk.libs;vtk.libs"`.

Resultado: o executável final ficou em **250 MB** (IfcOpenShell + OCP + as DLLs do VTK, sem o pacote Python do VTK nem matplotlib) — abaixo do que seria com tudo incluído, mas ainda bem mais pesado que os 71 MB de antes de somar o OCCT, porque as DLLs nativas do VTK continuam sendo a maior parte do peso e não têm como ser removidas enquanto o OCP depender delas no nível binário. Testado e funcionando: o executável rodou corretamente, com os mesmos volumes certos e o IfcOpenShell funcionando.

## Conclusão

A pergunta em aberto ("como o OCCT e o IfcOpenShell se encaixam no mesmo motor?") está respondida: rodam juntos, no mesmo processo Python, sem conflito, com resultado numericamente idêntico ao já validado em JS — inclusive já empacotados juntos num executável de teste. O peso do instalador sobe de ~71 MB para ~250 MB ao somar o telhado; matplotlib e o pacote Python do VTK foram eliminados, mas as DLLs nativas do VTK (~264 MB) são um custo fixo enquanto usarmos o `cadquery-ocp`. O próximo passo (não feito aqui) é converter o sólido calculado pelo OCP em entidades IFC reais (`IfcRoof`) dentro do arquivo que o `ifcopenshell` já está montando — provavelmente triangulando o sólido do OCP e construindo a representação a partir dos vértices/faces, já que não há uma ponte direta documentada entre um `TopoDS_Shape` do OCCT e uma entidade IFC.

## Limites deste teste

Não testado: conversão do sólido OCP em entidade IFC de verdade, e se existe uma forma de conseguir as DLLs do VTK sem precisar instalar o pacote `vtk` completo uma vez só para extraí-las (hoje depende de ter instalado `vtk` em algum momento para gerar essa pasta). Mesma ressalva do teste em JS quanto a contornos não retangulares e águas com inclinações diferentes entre si.

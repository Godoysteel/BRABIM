# IfcOpenShell no navegador via WASM — teste de viabilidade

Executado em 08/09/2026. Testa se o motor Python que já resolve os encontros de parede (ver [experimento nativo](../ifcopenshell/README.md)) pode rodar direto no navegador do visitante, sem servidor — o que eliminaria a maior incerteza de infraestrutura da [integração planejada](../../docs/03-arquitetura/integracao-ifcopenshell.md).

## O que existe hoje

O projeto [IfcOpenShell/wasm-wheels](https://github.com/IfcOpenShell/wasm-wheels) mantém wheels oficiais do IfcOpenShell compilados para WebAssembly via Pyodide, incluindo a versão 0.8.5 (a mesma já validada no experimento nativo): `ifcopenshell-0.8.5-cp313-cp313-pyodide_2025_0_wasm32.whl`. Um repositório irmão, [IfcOpenShell/wasm-preview](https://github.com/IfcOpenShell/wasm-preview), demonstra o uso mas está arquivado desde janeiro de 2025 e se descreve como "technological preview", citando explicitamente desempenho não ideal e problemas de tratamento de exceções C++ em WASM.

## Execução

`npm install` seguido de `node run.mjs` nesta pasta. Usa o pacote `pyodide` para Node (equivalente ao que rodaria no navegador), carrega o wheel acima via `micropip` e repete a cena de cinco paredes do experimento nativo (mesmos encontros, mesmas dimensões), sem a camada de verificação por `shapely` do experimento original — o objetivo aqui é só medir viabilidade e tempo, não repetir as oito verificações já feitas nativamente.

`pyodide` precisou ser fixado em `0.28.3`: é a versão cujo runtime embutido (Python 3.13, `emscripten_2025_0`) corresponde ao wheel do IfcOpenShell. Versões mais novas do pacote `pyodide` (ex. a atual, com Python 3.14) rejeitam o wheel por incompatibilidade de plataforma.

## Resultado

O wheel carrega e a API (`geometry.connect_path`, `geometry.regenerate_wall_representation`, `ifcopenshell.geom.create_shape`) funciona: as cinco paredes e as seis conexões são geradas corretamente, com as mesmas dimensões e encontros do experimento nativo (ver `results/report.json` de uma execução).

Porém o tempo de execução do cálculo geométrico (sem contar carregar o Pyodide nem instalar o wheel) foi de **27 a 53 segundos** em três execuções, contra **0,08 a 0,57 segundos** no Python nativo — de 50 a mais de 100 vezes mais lento. A instalação do wheel via `micropip` levou de 3 a 126 segundos, com grande variação entre execuções (possivelmente por cache de rede, não medido a fundo).

| Etapa | WASM (Node/Pyodide) | Nativo (Python) |
|---|---|---|
| Carregar runtime | ~1,6–2,5 s (Pyodide) | não aplicável |
| Instalar/importar biblioteca | 3–126 s (variável) | já instalada localmente |
| Calcular 5 paredes + 6 conexões | 27–53 s | 0,08–0,57 s |

## Conclusão

Rodar o IfcOpenShell inteiro via WASM no navegador é **tecnicamente possível**, mas o tempo de cálculo observado — dezenas de segundos para uma cena pequena — inviabiliza recálculo em tempo real enquanto o usuário edita (arrastar uma parede, digitar uma medida). Isso é consistente com o aviso do próprio repositório de exemplo sobre desempenho e tratamento de exceções em WASM, e com o fato de o projeto estar arquivado.

Não descarta WASM para um uso pontual (por exemplo, um botão "gerar IFC final" que o usuário aciona e espera, em vez de recálculo a cada edição), mas para o objetivo de ligar o motor à edição ao vivo da planta/3D, a alternativa de um serviço Python (nativo, não WASM) processando as edições — com o custo de hospedagem e manutenção que isso implica — volta a ser a opção mais viável avaliada até aqui. Essa troca de custos (hospedagem vs. tempo de espera do usuário) ainda não foi decidida.

## Limites deste teste

Medido em Node.js, não no navegador real (o pacote `pyodide` para Node usa o mesmo runtime, mas condições de CPU/rede do navegador do usuário final podem variar). Testado só o cenário base de cinco paredes; espessuras e alturas diferentes não foram repetidas aqui por já termos o suficiente para decidir viabilidade. Memória não medida. Sem testes de cache de wheel em navegador real (Service Worker, IndexedDB), que poderiam reduzir o custo de instalação em visitas repetidas — não elimina o custo de execução.

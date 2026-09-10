# Integração do IfcOpenShell

**Data:** 08-10/09/2026. **Status:** integrado ao app desktop real (não mais só experimento) para o retângulo básico de um ambiente, incluindo porta, janela e telhado; ambientes conectados continuam com geometria demonstrativa.

## Resultado do primeiro experimento

Três cenários passaram nas oito verificações automatizadas de cada caso: modelo original, espessuras diferentes e alturas diferentes. Foram gerados IFCs e malhas; veja [procedimento, resultados e limites](../../experiments/ifcopenshell/README.md). Memória, edição sequencial de parâmetros e revisão profissional continuam pendentes. O protótipo publicado não mudou.

## Objetivo

Reutilizar a geração de geometria e encontros do IfcOpenShell no BRABIM. O usuário permanece na interface do BRABIM; não precisa abrir Revit ou Blender. A biblioteca é uma dependência técnica incorporada à solução.

O pacote 0.8.5 está em `.runtime/python`, fora do versionamento. Sua execução foi comprovada pelo experimento; isso não representa integração com a viewport nem validação abrangente de junções.

## Arquitetura a experimentar

**Edição no BRABIM → parâmetros e conexões → adaptador → IfcOpenShell → geometria e identificadores → planta e 3D.**

O adaptador deve isolar a aplicação das particularidades da API, conservar identificadores e unidades e comunicar falhas sem apresentar resultados antigos como se fossem atuais.

Para a primeira prova, gerar um arquivo e a geometria separadamente. Em seguida, avaliar um serviço Python para processamento dinâmico. A hospedagem atual da interface não está configurada para esse motor Python; não assumir que basta instalar o pacote no frontend.

Rodar o IfcOpenShell no próprio navegador via WASM foi testado e descartado para recálculo em tempo real: o cálculo da mesma cena de cinco paredes levou de 27 a 53 segundos em WASM, contra menos de 1 segundo nativo — ver [experimento](../../experiments/ifcopenshell-wasm/README.md) e [decisão 0004](../04-decisoes/0004-wasm-nao-viavel-tempo-real.md).

Isso levou a testar OCCT/WASM (união booleana de sólidos) como alternativa sem servidor — ver [experimento](../../experiments/opencascade-wasm/README.md) e [decisão 0005](../04-decisoes/0005-occt-wasm-para-encontros.md) — mas a plataforma final foi esclarecida como **desktop**, não navegador ([decisão 0006](../04-decisoes/0006-plataforma-desktop-e-retorno-ifcopenshell.md)). Em desktop, o motor Python roda embutido no próprio aplicativo, sem precisar de servidor externo; a razão original para evitar o IfcOpenShell nativo deixa de existir. O motor volta a ser o **IfcOpenShell nativo**, mantendo conformidade IFC desde o início. Falta decidir como o aplicativo desktop empacota e se comunica com esse processo Python.

Em uma futura edição desktop, o motor poderá ser empacotado localmente. Para a opção web com servidor, haverá comunicação de rede. Nenhuma dessas opções foi definida como plataforma final.

## Integração real no app (09/09/2026)

Deixou de ser só experimento isolado: `prototipo/src-tauri/` empacota a interface real do BRABIM num app Tauri, com `prototipo/lib/engine-client.ts` conversando com o sidecar do motor. Um campo **"Motor real (IFC)"** na interface liga o cálculo real do IfcOpenShell para o ambiente ativo — testado manualmente, funciona: editar largura/profundidade atualiza a planta e o 3D com a geometria calculada de verdade, não mais a demonstrativa.

Porta e janela também passaram a ser cortes reais: `worker.py` usa `ifcopenshell.api.feature.add_feature` (um `IfcOpeningElement` que voida a parede por booleana) para abrir o vão de verdade na geometria, na posição e altura definidas pelo usuário — não mais uma composição de caixas como no demonstrativo. Testado com os valores padrão (porta a 1 m com 0,9 m de largura; janela a 2 m com 1,2 m de largura e peitoril 1 m): o vão aparece corretamente na planta (dividida em dois segmentos ao redor do vão) e como furo real no 3D.

Escopo ainda restante: só o retângulo de 4 paredes do ambiente ativo, com porta e janela (o mesmo caso validado no [experimento de empacotamento](../../experiments/desktop-sidecar/README.md)). Ainda não integrados ao motor: piso, moldura/acabamento decorativo ao redor do vão (removido da planta quando o motor está ligado, por ficar dessincronizado do corte real), paredes compartilhadas entre ambientes conectados e portas de ligação. Ligar um segundo ambiente ao motor hoje mostraria paredes duplicadas na fronteira compartilhada, já que o motor ainda não sabe que dois ambientes são vizinhos. A função `add_opening` do worker também assume paredes paralelas aos eixos do mundo (válido para o retângulo atual, não generalizado para ângulos livres).

## Telhado real e painel de depuração (10/09/2026)

O `worker.py` passou a calcular também o telhado do ambiente ativo por interseção de semi-espaços OCCT (mecanismo já validado, ver [decisão 0008](../04-decisoes/0008-telhado-por-interseccao-de-planos.md)), ligado por um campo "Telhado (4 águas)" na interface — hoje com inclinação e beiral fixos (`{slope:.6, slopedEdges:['north','south','east','west'], overhang:.5}` em `room-editor.tsx`, sem controle de UI ainda). O sólido é modelado como uma casca de espessura real (dois sólidos subtraídos, não um corte plano único) para não deixar a parede aparecer por dentro do telhado nem apagar o beiral.

Dois bugs de alinhamento entre parede e telhado apareceram e foram corrigidos nessa integração — detalhados na [decisão 0008](../04-decisoes/0008-telhado-por-interseccao-de-planos.md#integração-real-no-app-e-dois-bugs-de-alinhamento-10092026). Ambos só foram diagnosticados com precisão graças a um **painel de ferramentas de depuração** construído nesta sessão (coordenadas por clique no 3D, exportação de vértices/faces em JSON, wireframe, corte de seção) — ver a mesma decisão para detalhes. Esse painel fica disponível a qualquer momento no editor, não é específico de telhado, e deve seguir útil para futuros bugs de geometria.

## Pilares e vigas (cinta) reais (10/09/2026)

O `worker.py` passou a gerar também a estrutura de concreto do ambiente ativo: um `IfcColumn` em cada um dos 4 cantos e um `IfcBeam` ("cinta de amarração") no topo de cada parede, ligados por um campo "Estrutura" na interface com dois parâmetros editáveis (lado do pilar, altura da cinta). Como pilar e viga ocupam o mesmo canto, a viga é recortada (booleana OCCT) pela união dos 4 pilares antes de virar malha — sem esse recorte, as duas faces coincidentes no canto piscavam na tela (mesma classe de bug já resolvida para camada/verga). Com "Armação" ligada, os mesmos pilares e vigas recebem ferragem real: `_reinforce_beam` (antes só horizontal, eixo X) ganhou um parâmetro de eixo para também servir a cinta de paredes leste/oeste (eixo Y), e uma função irmã vertical (`_reinforce_column`) cobre os pilares, com as barras longitudinais distribuídas ao redor do perímetro da seção (não só em duas fileiras, como na verga).

Testado isoladamente via `worker.py` (sem app Tauri disponível neste ambiente): pilares e vigas nascem exatamente encostados nos cantos, sem vão nem sobreposição, e a ferragem cai nas posições esperadas. Ligar "Estrutura" sozinho é rápido (~0,2 s); ligar "Estrutura" **e** "Armação" juntos sobe para ~4 s por recálculo num ambiente padrão, porque cada barra/estribo é uma entidade IFC própria (mais de 200 nesse caso) e o motor remalha cada uma duas vezes (uma para gravar a representação IFC, outra ao reler para a viewport — custo já existente no arquivo, só mais visível com mais entidades). Não há trava de desempenho para esse combo hoje; se incomodar no uso real, a otimização mais direta é parar de reler via `ifcopenshell.geom.create_shape` para formas que o próprio worker já triangulou.

### Pilares intermediários (10/09/2026)

Os 4 cantos continuam automáticos, mas cada parede (P01-P04) agora aceita pilares extras num ponto qualquer do seu próprio vão — mesma convenção de distância que porta/janela já usam (distância a partir do início da parede). `structure.extraColumns` no pedido ao motor é um dicionário parede → lista de distâncias; `worker.py` converte cada uma em ponto do mundo (`_wall_point`) e junta esses pilares aos 4 de canto numa única lista antes de gerar caixa, malha e ferragem — o mesmo código dos cantos serve para os dois casos. O corte booleano da cinta contra os pilares (já existente) generalizou de graça: a viga é recortada contra a união de *todos* os pilares que ela cruza, não só os dois das pontas, então um pilar no meio do vão também abre um vão limpo na viga sem precisar de código novo.

Na interface, com "Estrutura" ligada e uma parede selecionada, o painel de propriedades ganhou uma seção "Pilares intermediários": um "+ Pilar nesta parede" adiciona um no meio do vão (campo numérico de distância editável, sem arrastar ainda — diferente de porta/janela), e cada um tem seu próprio "×" para remover. Não é salvo no arquivo do projeto ainda (mesma limitação de telhado/armação/estrutura em si). Não há como remover um pilar de canto especificamente nesta versão — só ligar/desligar os 4 juntos pelo botão "Estrutura".

## Validação prevista

| Caso | Evidência necessária |
|---|---|
| Cinco paredes atuais | Elementos e relações preservados |
| Cantos em L e encontros em T | Fechamento e ausência de sobreposição indevida |
| Espessuras diferentes | Recalcular sem frestas e conferir geometria |
| Alturas e ângulos diferentes | Registrar resultados e limitações, sem presumir suporte correto |
| Edição repetida | Planta e 3D representam a mesma revisão |
| Falha do motor | Mensagem clara e último resultado identificado como anterior |

O experimento registra duração por cenário. Medições de memória, tamanho das respostas de serviço e benchmark repetido permanecem pendentes. Diego poderá conferir os casos e Paulo revisar critérios técnicos, conforme divisão proposta.

## Custos e atualizações

Não foi identificado custo de assinatura por usuário do IfcOpenShell. O planejamento deve considerar integração, testes, manutenção e processamento/armazenamento quando houver servidor. Não há orçamento mensal ou promessa de hospedagem gratuita.

Usar versão explícita, começando pelo experimento com 0.8.5; preparar dependências reproduzíveis antes da adoção. Não atualizar automaticamente o motor. Avaliar cada atualização com casos de referência, comparação de geometria, desempenho e compatibilidade; manter forma de retornar à versão anterior. Versões antigas também podem demandar correções e acompanhamento.

Os metadados locais indicam LGPLv3 ou posterior. O código de Bonsai consultado declara GPLv3 ou posterior e deve ser avaliado separadamente. A forma de distribuição e as obrigações aplicáveis ainda precisam ser analisadas; não foi aprovada uma estratégia de licenciamento do BRABIM.

## Fontes consultadas na pesquisa

- [Regeneração de paredes na API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/geometry/regenerate_wall_representation/index.html)
- [Código e aviso de licença do módulo](https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.8.0/src/ifcopenshell-python/ifcopenshell/api/geometry/regenerate_wall_representation.py)
- [Comparação inicial com alternativas](reaproveitamento-open-source.md)

As referências de código são de uma branch consultada, não um commit imutável correspondente à instalação 0.8.5. Conferir o artefato fixado ao implementar.

# BRABIM — roteiro funcional do básico ao avançado

Data: 10/09/2026. Proposta de desenvolvimento baseada na documentação oficial do Revit e na leitura do BRABIM desktop local. A ordem e os critérios de conclusão são recomendações para o BRABIM, não uma sequência prescrita pela Autodesk. Não constitui compromisso de prazo nem decisão já aprovada de MVP comercial.

## Objetivo e limite do básico

Concluir primeiro um fluxo de projeto arquitetônico de pequena edificação: criar, editar, salvar, reabrir, documentar, quantificar e compartilhar. O projeto de referência será uma casa de dois pavimentos, com planta em L, paredes compartilhadas, portas e janelas em orientações diferentes, escada, cobertura, pisos, lajes, forros e elementos estruturais geométricos simples.

O básico termina quando essa casa pode ser alterada e entregue com plantas, cortes, fachadas, pranchas PDF, tabelas e IFC coerentes com o modelo. Não termina quando cada ferramenta produz uma imagem isoladamente. Instalações completas, dimensionamento estrutural, fabricação e colaboração simultânea pertencem à expansão avançada.

O Revit organiza recursos de modelagem, documentação, análise e colaboração. Essa abrangência serve como referência de cobertura, sem assumir que todo recurso deva ser reproduzido ou que extensões do ecossistema sejam funções nativas do programa. [Visão geral oficial](https://www.autodesk.com/products/revit/features).

## Ponto de partida confirmado no código

Referência: `main`, commit `c5fbe7b`. Este roteiro foi originalmente escrito em outro worktree (`brabim-b642a1`, commit `accdeaa`) que tinha uma implementação própria e ainda não commitada de cinta; nesse meio-tempo, `main` recebeu pilares nos 4 cantos + cinta (recortada por booleana contra os pilares, ver [integração](../03-arquitetura/integracao-ifcopenshell.md#pilares-e-vigas-cinta-reais-10092026)), escolhida como a versão a manter. A tabela abaixo já reflete esse estado. Leitura de código; não é certificação por teste da aplicação em execução.

| Capacidade | Situação observada | Trabalho restante |
|---|---|---|
| Desktop Tauri + React/Three.js | Implementado | Robustez do processo local e distribuição |
| IfcOpenShell/OCCT local | Ligado ao editor | Modelo completo, continuidade de identidade e recuperação |
| Ambientes | Até oito retângulos alinhados | Paredes independentes e ambientes delimitados |
| Portas e janelas | Recortes reais no ambiente isolado | Múltiplas aberturas, outras orientações e hospedagem persistente |
| Cobertura | Duas/quatro águas e ajuste do topo das paredes | Parâmetros editáveis e contornos gerais |
| Paredes em camadas | Implementadas | Espessura única coerente entre camadas, encontros, layout e cobertura |
| Vergas, contravergas e armadura | Geometria implementada | Robustez, persistência e detalhamento; não representa dimensionamento |
| Pilares e cinta | Implementados (4 cantos fixos + viga no topo de cada parede), com armação real opcional | Pilares intermediários/removíveis ao longo da parede, validar encontros, aberturas altas, cobertura e salvamento |
| Materiais e texturas | Catálogo visual e mapas PBR | Propriedades técnicas com origem e escala de textura definida |
| Arquivo de projeto | JSON com ambientes e camadas | Incluir telhado, cinta, pilares, armaduras e demais opções hoje fora de `House` |
| Vistas | Planta, 3D e corte visual de inspeção | Cortes documentais, fachadas, cotas, pranchas e tabelas |

O worker cria um novo arquivo IFC em cada cálculo de ambiente. Isso não equivale a editar um documento BIM persistente com GUIDs conservados entre operações. A ponte cliente também precisa tratar requisições pendentes quando o processo encerra e resultados que chegam após uma edição mais recente.

## Regras de desenvolvimento

- Cada função deve funcionar ao criar, alterar, desfazer/refazer e salvar/reabrir.
- Modelo, planta, 3D, tabelas e documentos devem identificar a mesma revisão; resultado antigo deve aparecer como desatualizado.
- Primeiro cobrir geometrias frequentes e limites explícitos; depois ampliar complexidade.
- Não ampliar armaduras, renderização ou simulação enquanto houver falhas nos critérios do básico. Preservar o que existe e integrá-lo ao documento.
- Testar cada etapa com projetos pequenos de referência e com uma sequência real de alterações, além das verificações geométricas pertinentes.
- Como estudantes são o público prioritário registrado, fornecer unidades claras, mensagens compreensíveis, exemplos e ajuda contextual desde o início.

## Básico — etapas 0 a 7

### Etapa 0 — documento confiável e motor estável

1. Documento de projeto versionado, contendo todos os elementos, materiais, opções e configurações de projeto.
2. IDs persistentes, relações entre elementos e correspondência estável com entidades IFC.
3. Novo, abrir, salvar, salvar como, arquivos recentes e indicação de alterações não salvas.
4. Salvamento automático, cópia de recuperação, escrita segura e tratamento de arquivo incompatível/corrompido.
5. Desfazer e refazer para todas as operações, incluindo tipos, camadas e opções construtivas.
6. Unidades, precisão e entrada de medidas em português, com validação de intervalos e combinações.
7. Transações: uma edição inteira é aceita ou revertida; falha geométrica não deixa meio projeto alterado.
8. Revisão de requisições ao motor, descarte de respostas obsoletas, limite de espera e reinício após falha.
9. Migração dos projetos retangulares existentes para o documento novo.
10. Modelo de categorias, tipos e instâncias; biblioteca inicial pequena, com duplicar e editar tipo.

Conclusão: editar uma casa com cobertura, camadas, cinta e armação; salvar; fechar; reabrir sem perda; desfazer/refazer alterações; provocar uma falha do motor e recuperar sem corromper o documento.

Referência funcional: famílias agrupam componentes parametrizados, enquanto o painel de propriedades distingue operações sobre tipos e elementos colocados. [Famílias](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-Model/files/GUID-4EBB97AD-C7B6-4828-91EB-BC0E99B81E43.htm), [propriedades](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-GetStarted/files/GUID-A764EA7A-FE26-469B-857C-F3A70812FC34.htm).

### Etapa 1 — desenho e edição por paredes

1. Paredes por pontos, sequência de segmentos e retângulo, incluindo segmentos em ângulos livres.
2. Digitação de comprimento/ângulo, prévia antes de confirmar e cancelamento com Esc.
3. Captura de extremidades, ponto médio, interseção, perpendicular e alinhamento; trava ortogonal opcional.
4. Seleção simples, múltipla, por janela e por categoria; realce antes do clique.
5. Mover, copiar, girar, espelhar, apagar e editar pelas alças.
6. Alinhar, afastar, aparar, prolongar e dividir paredes.
7. Linha de referência por eixo/face, inversão do lado interno e externo e cotas temporárias editáveis.
8. Encontros em L, T e X, com espessuras diferentes; unir/desunir e indicar conexões inválidas.
9. Uma parede compartilhada representada uma única vez no modelo.
10. Propriedades de altura, espessura e camadas por tipo/instância, com espessura total coerente.

Conclusão: desenhar a planta em L com três ambientes, mover uma divisória e trocar sua espessura sem duplicações, frestas ou perda de relações. Planta e 3D devem concordar.

Referência funcional: o tutorial de paredes do Revit combina criação em cadeia, tipos, níveis e aparar/dividir. [Criar paredes](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-GetStarted/files/GUID-30D3A26F-42FF-40FA-83D2-B43EA67F3ECD.htm).

### Etapa 2 — portas, janelas e ambientes

1. Inserir várias portas, janelas e vãos vazios em qualquer parede reta suportada.
2. Vincular abertura e esquadria à parede; manter a posição relativa definida pelo usuário ao mover o hospedeiro.
3. Largura, altura, peitoril, distância à referência e inversão do sentido de abertura.
4. Mover/copiar/trocar tipo e excluir esquadrias, recompondo o vão anterior.
5. Tratar aberturas sobrepostas, fora da parede ou em conflito com encontros e vergas.
6. Identificar regiões fechadas e permitir colocar, nomear e numerar ambientes.
7. Linhas separadoras para ambientes sem parede e aviso de ambiente aberto, duplicado ou sem área.
8. Atualizar área, perímetro e volume com regra explícita de medição e tratamento de vãos.
9. Portas internas relacionando os ambientes dos dois lados.
10. Identificadores e quadro inicial de ambientes/esquadrias ligados aos elementos.

Conclusão: mover parede e janela, excluir uma porta e abrir/fechar um contorno; os recortes, ambientes e medidas devem acompanhar cada operação.

Referência funcional: no Revit, a área depende dos elementos delimitadores, da posição do limite e da altura de cálculo. Isso exige uma regra geométrica definida, além de um rótulo na planta. [Área de ambientes](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-ArchDesign/files/GUID-9348929C-18CA-40AC-BB64-71D01CC52F2B.htm).

### Etapa 3 — pavimentos e elementos horizontais

1. Níveis nomeados com cotas; paredes com base, topo e afastamentos associados a níveis.
2. Eixos de referência numerados e cotados.
3. Navegação por pavimento e copiar elementos entre níveis.
4. Pisos e lajes reais por contorno fechado, espessura, material e camadas.
5. Aberturas em pisos/lajes e shafts atravessando os níveis selecionados.
6. Forros planos por contorno, altura e recortes.
7. Pilares, vigas e fundações simples como elementos BIM geométricos editáveis, com tipos e níveis.
8. Junções básicas entre laje, parede, pilar e viga, com regras claras de prioridade.

Conclusão: elevar o pé-direito de um pavimento e verificar paredes, lajes, aberturas e apoios relacionados; produzir dois pavimentos sem copiar coordenadas manualmente.

### Etapa 4 — cobertura, circulação e componentes essenciais

1. Telhado por contorno poligonal; escolha das bordas inclinadas, inclinação, beiral, espessura e nível.
2. Coberturas simples de uma, duas e quatro águas; encontros de cobertura dentro de limites declarados.
3. Anexar/desanexar topo de parede ao telhado e atualizar em mudanças de altura/contorno.
4. Aberturas e claraboias simples; calhas e rufos básicos.
5. Escada reta e em L/U, com patamares, largura, altura a vencer e contagem de degraus.
6. Rampas simples e guarda-corpos/corrimãos associados ao percurso.
7. Biblioteca mínima de mobiliário, louças e equipamentos para compor e conferir o uso dos ambientes.
8. Revestimentos e rodapés simples, com material e dimensão, sem exigir modelar cada unidade.

Conclusão: completar a circulação vertical e a cobertura da casa de referência, alterando altura entre níveis sem deixar escada ou paredes desconectadas. Regras dimensionais adotadas devem ser visíveis; não presumir aprovação normativa automática.

Referência funcional: o Revit permite guarda-corpos independentes ou associados a escadas, rampas e outros elementos. [Guarda-corpos](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-ArchDesign/files/GUID-34DEB2F6-E66E-4801-8138-958DDB4D2A5A.htm).

### Etapa 5 — vistas e documentação

1. Navegador de projeto com níveis, vistas, tabelas e pranchas.
2. Plantas por nível, planta de cobertura e planta de forro.
3. Faixa de vista e altura de corte da planta; diferenciação entre elemento cortado e projetado.
4. Cortes e fachadas derivados do modelo, com profundidade, recorte e escala.
5. Vistas 3D salvas, caixa de corte, ocultar/isolar e filtros por categoria/material.
6. Cotas associativas lineares, alinhadas, angulares e de nível; atualização após edição.
7. Textos, chamadas, identificadores de ambientes, portas, janelas e materiais.
8. Espessuras e estilos de linha, hachuras, níveis de detalhe e modelos de vista.
9. Pranchas com formatos, carimbo, vistas em escala e numeração.
10. Impressão/PDF vetorial com escala verificável, fontes e espessuras consistentes.
11. Detalhes 2D complementares, referências entre cortes/detalhes e registro básico de revisão.

Conclusão: emitir plantas dos dois níveis, cobertura, dois cortes, quatro fachadas e quadro de esquadrias. Mudar uma janela e conferir atualização nas vistas, cotas e prancha.

Referência funcional: o conjunto documental do Revit reúne pranchas, vistas, carimbos, tabelas, cotas e revisões. [Documentação de construção](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-DocumentPresent/files/GUID-470D18F3-512E-4700-A48E-68F98A519028.htm).

### Etapa 6 — informação, quantitativos e troca de arquivos

1. Tabelas de ambientes, paredes, portas, janelas, pisos, lajes e coberturas.
2. Contagens, comprimentos, áreas e volumes; separar bruto/líquido e explicitar descontos de aberturas.
3. Quantidade por camada/material, evitando contar duas vezes paredes compartilhadas ou elementos sobrepostos.
4. Ordenar, filtrar, agrupar e totalizar; localizar no modelo os elementos de uma linha da tabela.
5. Exportar tabelas CSV com unidade e regra de cálculo identificadas.
6. Exportar IFC do projeto inteiro com níveis, classes, propriedades, relações e IDs consistentes.
7. Abrir IFC externo como referência, selecionar e consultar propriedades; edição irrestrita de IFC importado fica para etapa posterior.
8. Referências de imagem/PDF com ajuste de escala, origem e travamento; intercâmbio DXF 2D básico após avaliar biblioteca e cobertura.
9. Verificador de elementos sem material, duplicações, volumes inválidos e campos obrigatórios ausentes.

Conclusão: conferir quantitativos de uma geometria com valores conhecidos; abrir o IFC em visualizador independente e comparar dimensões, categorias e contagens. Não prometer leitura/escrita RVT ou RFA.

### Etapa 7 — consolidar o básico utilizável

1. Instalação e atualização no Windows preservando arquivos e preferências; desinstalação sem apagar projetos.
2. Projeto inicial, exemplos, atalhos consistentes e ajuda contextual nas ferramentas.
3. Testes com estudantes realizando tarefas sem orientação do desenvolvedor; registrar bloqueios e corrigir fluxos.
4. Medir abertura, salvamento, recálculo, navegação e memória em projetos de referência pequeno e médio; registrar hardware e metas antes de aprovar.
5. Verificar recuperação após encerramento inesperado, falha do motor e abertura de versão antiga.
6. Executar o teste completo da casa e uma reforma simples de sua geometria, comparando documentos e quantitativos antes/depois.

Conclusão: nenhum bloqueio de criação, edição, recuperação ou entrega no fluxo de referência; limitações restantes identificadas dentro do produto. Este é o marco de básico completo, sujeito à validação com o público. Resolver as pendências de distribuição comercial já registradas no projeto antes do lançamento pago.

## Avançado — etapas 8 a 13

Após a etapa 7, a ordem abaixo é a prioridade sugerida. Módulos especializados podem ser repriorizados por demanda comprovada, preservando suas dependências.

### Etapa 8 — arquitetura complexa e parametrização

- Paredes curvas/inclinadas e perfis editáveis; paredes-cortina, painéis e montantes.
- Coberturas complexas, pisos inclinados, escadas especiais e guarda-corpos personalizados.
- Editor de componentes parametrizados, fórmulas, restrições, parâmetros globais e componentes aninhados.
- Grupos repetidos, edição de conjunto e preservação de alterações individuais.
- Terreno por pontos/curvas, implantação, coordenadas compartilhadas, norte e volumes de corte/aterro.
- Fases existente/demolir/construir e alternativas de projeto com vistas e tabelas correspondentes.

Conclusão: alterar um tipo e propagar apenas às instâncias correspondentes; comparar alternativas sem misturar quantidades; documentar uma reforma por fase.

Referências: [parâmetros globais](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-HaveYouTried/files/GUID-84DC949A-D711-4AA7-A8EF-D6E8DAD5E386.htm), [terreno](https://help.autodesk.com/view/RVT/2026/ENU/?guid=GUID-95E3A3A6-BD9F-44B0-8847-E84736E3BB1E), [fases](https://help.autodesk.com/cloudhelp/2024/ENU/Revit-DocumentPresent/files/GUID-BDCE1B94-58D0-401B-863B-2708D36D54EA.htm).

### Etapa 9 — montagem construtiva e detalhamento

- Distribuição de blocos/tijolos com juntas, paginação, amarração, cortes e tratamento de vãos.
- Cobertura de madeira com tesouras, terças, caibros e ripas; gerar conjunto e editar cada peça.
- Continuidade geométrica de vergas, contravergas, cintas e encontros.
- Armaduras por elemento, cobrimento, ganchos, dobras, emendas, identificação e listas de corte.
- Ligações de madeira/aço, conectores, chapas e parafusos, inicialmente como detalhamento geométrico.
- Quantitativos por peça e conjunto; níveis de representação para não manter todos os tijolos detalhados na memória.
- Regeneração preservando edições manuais e mostrando conflitos.

Conclusão: mudar um vão ou uma peça e atualizar os componentes afetados, a lista de materiais e os detalhes sem apagar intervenções manuais. Esta etapa concretiza a visão própria de montagem do BRABIM; não pressupõe que o Revit entregue essa experiência pronta.

### Etapa 10 — instalações prediais

- Primeira entrega: água e esgoto — tubos, conexões, aparelhos, inclinações e redes conectadas.
- Segunda entrega: elétrica — pontos, luminárias, eletrodutos, circuitos e quadros.
- Terceira entrega: ventilação/climatização — dutos, terminais e equipamentos.
- Conectores com direção, dimensão, sistema e estado de conexão.
- Traçados assistidos e aviso de pontas desconectadas, colisões e passagens sem abertura.
- Plantas, isométricos, tabelas e quantitativos por sistema.
- Cálculos de demanda, perda de carga ou cargas térmicas somente com método e domínio de validade definidos e testados.

Dependências: etapas 0–7 e modelo de conectores. Conclusão por sistema: acompanhar a rede da origem aos pontos finais e atualizar documentação após reposicionar um aparelho.

Referência funcional: o Revit organiza MEP em sistemas mecânicos, elétricos e de tubulação, com ferramentas de conexão e inspeção. [MEP](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-MEPEng/files/GUID-195C2C6C-5E2C-422E-A44D-FB3FDFDE276A.htm).

### Etapa 11 — coordenação e colaboração

- Vincular modelos de arquitetura, estrutura e instalações em uma referência comum.
- Detectar interferências e folgas insuficientes com tolerâncias, categorias e exceções configuráveis.
- Registrar pendências com elemento, vista, responsável, status e revisão; intercâmbio BCF após validar a implementação.
- Comparar revisões e mostrar elementos incluídos, modificados e removidos.
- Compartilhar inicialmente arquivos/revisões; depois implementar edição simultânea, propriedade de elementos e resolução de conflitos.
- Revisão visual e comentários sem exigir licença completa de edição.

Conclusão: receber uma revisão externa e manter comentários associados aos elementos; em colaboração simultânea, impedir perda silenciosa de trabalho.

Referência funcional: o Revit distingue modelos vinculados de trabalho simultâneo em modelo compartilhado. Para o BRABIM, começar por vínculos reduz a complexidade inicial de colaboração. [Trabalho em equipe](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-Collaborate/files/GUID-D49CE758-A0F4-4B1D-9CBF-12B0B00F5AB3.htm).

### Etapa 12 — análise e simulação verificáveis

- Modelo analítico associado ao físico: nós, barras, painéis, apoios, liberações e ligações.
- Propriedades físicas documentadas, unidades, hipóteses e origem dos valores.
- Peso próprio, casos de carga e combinações por método explicitamente escolhido.
- Integração com solver validado, começando por casos simples com solução conhecida.
- Resultados de esforços, reações e deslocamentos; identificação da revisão analisada e invalidação após alterações.
- Dimensionamento e verificação de elementos/ligação por domínio implementado, com memória de cálculo e revisão especializada.
- Análises solar, iluminação, energia e conforto em módulos separados, conforme demanda.
- Simulação progressiva da montagem apenas após validar apoios, transferência de cargas e etapas construtivas.

Conclusão: reproduzir casos de referência, indicar instabilidades e dados ausentes e impedir que resultados antigos pareçam atuais. A simples presença de barras de aço ou contato geométrico não satisfaz esse critério.

Referência: o Revit mantém representação analítica própria para uso com ferramentas de análise; não confundir o modelo físico com um cálculo resolvido. [Modelo analítico](https://help.autodesk.com/cloudhelp/2025/ENU/Revit-StructEng/files/GUID-2A0652F2-2AC1-4009-9AD4-ADF41E0048D2.htm).

### Etapa 13 — automação, planejamento e apresentação

- API de comandos estável e automações reproduzíveis, com prévia, confirmação de alterações relevantes e desfazer.
- Verificações configuráveis de consistência e regras de projeto com escopo e fonte definidos.
- Orçamento com composições, preços datados, perdas explícitas e rastreabilidade aos quantitativos.
- Planejamento por atividades e simulação 4D, separando sequência visual de análise física da montagem.
- Renderização, iluminação, percursos e apresentação interativa.
- Catálogos externos, extensões e assistentes de criação, mantendo os elementos editáveis pelo usuário.

Dependências: documentação/quantidades confiáveis para orçamento, revisões e relações persistentes para automação. São expansões do produto; não uma alegação de que todas essas funções pertençam ao Revit nativo.

## Próximos dez itens recomendados

1. Consolidar o esquema do documento e salvar cobertura, camadas, cinta e armação.
2. Introduzir identidade persistente, transações e revisão de resultados do motor.
3. Completar desfazer/refazer e recuperação de arquivo/processo.
4. Separar paredes de ambientes e migrar o modelo atual.
5. Desenhar paredes por pontos com medidas e capturas.
6. Implementar mover, dividir, aparar e prolongar.
7. Resolver encontros e paredes compartilhadas no motor.
8. Hospedar múltiplas portas/janelas em paredes com qualquer orientação reta suportada.
9. Identificar ambientes pelos contornos e atualizar suas áreas.
10. Adicionar níveis e pisos/lajes reais, iniciando a casa de dois pavimentos.

As etapas 0–7 formam uma fila de conclusão funcional. O trabalho interno pode se sobrepor quando não comprometer dependências; uma etapa não deve ser declarada concluída por existir apenas a interface ou o ensaio isolado. Manter cada item futuro como proposto até haver implementação e evidência de uso integrado.

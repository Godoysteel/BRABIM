# Entrevista 003 — Valesca

**Data da conversa:** não visível na captura fornecida (mensagens às 14:32–14:50)  
**Data do registro:** 10/09/2026  
**Identificação na fonte:** Valesca Eng; perfil profissional a confirmar  
**Fonte:** captura de conversa de WhatsApp fornecida pelo usuário  
**Status:** relato inicial; aprofundamento pendente

## 1. Pergunta apresentada

O início da pergunta não aparece na captura (mensagem cortada antes de "ja te mando"). Pela estrutura da resposta — duas listas separadas, tarefas mais usadas e o que mais irrita pela complexidade — o par de perguntas parece equivalente ao usado na [entrevista 002 com Paulo](entrevista-002-paulo.md):

> Quais são as 10 tarefas que um engenheiro/arquiteto mais executa em um BIM atual e que mais o irritam pela complexidade?

Isso é uma inferência da estrutura da resposta, não confirmação de que a pergunta exata foi essa.

## 2. Transcrição das respostas visíveis

Grafia preservada.

**14:42 — Tarefas mais utilizadas**

> 1 - Modelagem paramétrica
> 2 - Extração de lista de materiais
> 3 - Compatibilização entre disciplinas
> 4 - Detalhamento de conexões e prumada (no projetos de HIDRO)
> 5 - Detalhamento de armaduras em 3D (concreto armado)
> 6 - Exportação em IFC
> 7 - Geração de desenhos técnicos (plantas de fôrmas, executivos)
> 8 - Criação de templates
> 9 - Inserção de parametros de manutenção (cadastrar informações das peças, como marcas e datas de validade)
> 10 - Inserção das fases/etapas de projetos (a construir, a demolir, executado...)

**14:50 — O que mais irrita pela complexidade**

> 1 - Interoperabilidade: as vezes importamos ou exportamos uma modelagem e vem com bastante erros, armaduras fora do lugar, canos que se deslocam, a origem do projeto que pode causar problemas quando inseridos em outro software.
> 2 - Padronizar os dados: para que as planilhas de quantitativo funcionem devem estar muito bem configuradas, codigos certos. Plantas de áreas precisam de configurações e parametros bem detalhados no inicio do projeto, para que seja feito a taxa de permeabilidade, taxa de ocupação, area de terreno. As vezes o processo é bem manual, se errar um dado, ja dá problemas e erros nos quantitativos

## 3. Interpretação para a pesquisa

- A lista de tarefas mais usadas cobre modelagem, quantitativos, compatibilização, disciplinas complementares (HIDRO, estrutura), exportação IFC, documentação, templates, dados de manutenção e fases de obra — um escopo mais amplo de disciplinas do que os relatos anteriores de Bruno e Paulo, que não detalharam tarefas específicas por disciplina.
- **Exportação em IFC** aparece como tarefa de uso corrente (item 6), não como pedido de produto — é um dado de validação indireta de que IFC é um formato relevante no dia a dia do usuário-alvo, relevante para a escolha de motor já registrada em [decisão 0002](../../04-decisoes/0002-reutilizacao-e-ifcopenshell.md), mas não confirma demanda por nenhuma funcionalidade específica do BRABIM.
- A queixa 1 (interoperabilidade: armaduras fora do lugar, tubulações deslocadas, origem do projeto) tem proximidade temática com D1 (compatibilização arquitetura × estrutura, de Bruno) e com D9 (complexidade em projetos complementares, de Paulo), mas descreve um problema distinto: erros de importação/exportação entre softwares, não dificuldade de coordenar disciplinas dentro do mesmo modelo. Registrado como **D11**, novo.
- A queixa 2 (padronização de dados para quantitativos e taxas urbanísticas — permeabilidade, ocupação, área de terreno) tem proximidade temática com D2 (quantitativos sem vínculo temporal, de Bruno), mas também descreve um problema distinto: configuração manual propensa a erro no início do projeto, não ausência de distribuição temporal dos quantitativos. Registrado como **D12**, novo.
- Nenhuma das duas queixas foi comparada ainda a uma segunda menção independente — seguem como relato único até aparecerem em outra entrevista.

## 4. Hipóteses a investigar

Validação de dados na entrada (códigos de quantitativo, parâmetros de taxa urbanística) e consistência de geometria/posição em importação e exportação entre softwares podem ser caminhos de produto. Este relato não define MVP nem confirma que o BRABIM deva resolver interoperabilidade com outros softwares além do próprio fluxo interno.

## 5. Perguntas de aprofundamento

1. Pode mostrar um caso recente de armadura ou tubulação que se deslocou na importação/exportação? Qual par de softwares estava envolvido?
2. O problema de origem do projeto é sobre o ponto de inserção (coordenadas), a unidade de medida, ou outra coisa?
3. Quais códigos e configurações precisam estar certos hoje para as planilhas de quantitativo funcionarem? Existe um padrão que você segue ou cada projeto define o seu?
4. Como você calcula hoje taxa de permeabilidade, taxa de ocupação e área de terreno — manualmente, com parâmetros do modelo, ou com uma ferramenta externa?
5. Com que frequência um erro de configuração inicial chega a aparecer só depois, no quantitativo final?
6. Das dez tarefas listadas, quais três consomem mais tempo na prática?

## 6. Limites da evidência

O relato não fornece frequência, tempo perdido, impacto financeiro nem disposição para pagar por nenhuma das duas queixas. As aproximações com D1, D2 e D9 são temáticas; não comprovam recorrência do mesmo problema entre profissionais diferentes. A pergunta original não está visível na captura — a inferência de que ela equivale à usada com Paulo pode estar errada.

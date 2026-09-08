# BRABIM — Documento Mestre
## Fase Zero

**Versão:** 0.1  
**Data:** 07 de setembro de 2026  
**Status:** Documento inicial de concepção  
**Nome:** BRABIM — codinome provisório

## 1. Visão

O BRABIM é um projeto para criação de um software BIM profissional com foco em **simplicidade, produtividade, acessibilidade e interoperabilidade**.

> **Complexidade no motor. Simplicidade na tela.**

A hipótese inicial é que softwares BIM profissionais são poderosos, porém sua complexidade e custo podem criar barreiras para parte dos profissionais da construção. A Fase Zero existe para validar essa hipótese antes de desenvolvimento substancial.

## 2. Relação com o Esboce

BRABIM e Esboce são produtos independentes. O BRABIM não será uma evolução, versão profissional ou transformação do Esboce em BIM.

O Esboce mantém seu objetivo de permitir criar edificações, visualizar, escolher produtos e materiais, gerar quantitativos e orçamento com extrema simplicidade.

O BRABIM será destinado ao ambiente profissional de projeto e construção. Conhecimentos e, quando fizer sentido, componentes técnicos poderão ser estudados para reutilização sem misturar os objetivos dos produtos.

## 3. Problema inicial

A hipótese de produto é:

> **Softwares BIM profissionais podem apresentar barreiras significativas de complexidade e custo.**

Precisamos descobrir quais profissionais enfrentam isso, quais tarefas geram maior perda de tempo, quais soluções alternativas usam e por quais melhorias estariam dispostos a pagar.

## 4. Público inicial a investigar

- engenheiros;
- arquitetos;
- projetistas;
- pequenos escritórios;
- pequenas construtoras;
- profissionais autônomos da construção.

A pesquisa deverá identificar qual público apresenta a melhor combinação entre problema relevante, frequência e disposição para pagar.

## 5. Pesquisa inicial

Três engenheiros próximos aos idealizadores já foram consultados sobre as tarefas executadas em BIM que mais incomodam por complexidade, quantidade de etapas, dificuldade ou perda de tempo.

As respostas serão preservadas inicialmente sem alteração e depois analisadas por frequência, tempo, impacto, alternativa atual, valor econômico e recorrência.

## 6. O BRABIM não começará como “um novo Revit”

O primeiro objetivo não será construir um software BIM completo. O objetivo será encontrar **uma tarefa ou um pequeno conjunto de tarefas de alto valor** e resolvê-las excepcionalmente bem.

## 7. Estratégia de MVP

A menor versão comercial deverá:

1. resolver um problema profissional real;
2. economizar tempo ou dinheiro;
3. produzir resultado confiável;
4. ser utilizada por um profissional real;
5. possuir valor suficiente para alguém aceitar pagar.

O MVP não precisa possuir um editor BIM completo. Visualização IFC, quantitativos, orçamento, documentação, análise, automação ou edição são possibilidades a investigar — não decisões tomadas.

## 8. Estratégia de desenvolvimento

Antes de construir qualquer componente, perguntar:

> **Precisamos realmente construir isso?**

Tecnologias existentes poderão ser utilizadas quando resolverem problemas que não representam diferenciação do produto.

## 9. Ecossistema open source a investigar

- IfcOpenShell — IFC, geometria e informações BIM;
- Bonsai — referência de implementação BIM/openBIM;
- FreeCAD — CAD paramétrico e operações geométricas;
- LibreCAD — CAD 2D, cotas, layers e snapping;
- Open CASCADE Technology — kernel geométrico.

Nenhuma dessas tecnologias está definida como dependência oficial.

## 10. Política open source

Antes de reutilizar código ou componentes, avaliar licença, distribuição, compatibilidade comercial, dependências, maturidade, manutenção e desempenho.

> **Estudar livremente. Integrar somente após avaliação técnica e jurídica da licença.**

## 11. Interoperabilidade

IFC e princípios openBIM deverão ser considerados desde a arquitetura, mesmo que sejam implementados posteriormente.

> **Os dados pertencem ao usuário.**

## 12. Experiência do usuário

Para cada fluxo, questionar quantidade de etapas, automações possíveis, padrões inteligentes e informações realmente necessárias naquele momento.

> **Esconder complexidade sem retirar capacidade.**

## 13. Automação

Tarefas repetitivas serão candidatas a automação quando isso for confiável. IA poderá ser utilizada quando apresentar benefício real, sem obrigação de inseri-la em todas as funcionalidades.

## 14. Modelo comercial

Ainda não definido. Serão estudados versão gratuita limitada, assinatura acessível, planos individuais ou para escritórios e cobrança por projeto ou funcionalidades.

Preço deverá estar relacionado ao valor econômico produzido para o profissional.

## 15. Retorno sobre o desenvolvimento

> **O tempo de desenvolvimento precisa estar relacionado à criação de valor comercial verificável.**

Sequência desejada:

**Problema → Hipótese → Protótipo → Profissional → Feedback → Implementação → Validação → Cobrança**

## 16. Primeiro marco comercial

O primeiro grande marco não será “construímos nosso próprio BIM”. Será:

> **Um profissional utilizou o BRABIM para resolver um problema real e aceitou pagar pela solução.**

## 17. Fase Zero — 14 dias

### Dias 1–4 — Descoberta
Entrevistar profissionais, coletar problemas, ferramentas, custos, tarefas repetitivas e improvisações.

### Dias 5–7 — Classificação
Avaliar frequência, gravidade, tempo desperdiçado, número de afetados, dificuldade técnica, concorrência e potencial de cobrança.

### Dias 8–10 — Escolha
Selecionar inicialmente um problema com boa combinação de **dor + frequência + capacidade de pagamento + viabilidade**.

### Dias 11–12 — Solução
Desenhar o fluxo ideal sem copiar automaticamente os fluxos dos softwares existentes.

### Dias 13–14 — Protótipo
Criar protótipo visual, apresentar aos profissionais e observar entendimento, interesse, objeções e disposição para testar.

## 18. Critério para iniciar desenvolvimento

Precisamos conseguir completar:

> **O BRABIM ajuda [TIPO DE PROFISSIONAL] a realizar [TAREFA] reduzindo [PROBLEMA MENSURÁVEL], e encontramos profissionais interessados em testar essa solução.**

## 19. O que não fazer na Fase Zero

- construir editor BIM completo;
- criar dezenas de ferramentas;
- desenvolver kernel geométrico próprio;
- tentar substituir todas as plataformas BIM;
- passar meses programando antes de validar;
- misturar BRABIM e Esboce;
- escolher tecnologias antes do problema.

## 20. Métricas iniciais

- profissionais entrevistados: meta inicial de pelo menos 5;
- problemas recorrentes;
- problemas de alto impacto;
- interessados no protótipo;
- interessados em pagar.

## 21. Hipótese de crescimento

**Problema resolvido → primeiros usuários → primeira receita → problema relacionado → novo módulo → integração → plataforma BIM progressivamente mais completa.**

## 22. Princípios permanentes

1. Simplicidade
2. Precisão
3. Interoperabilidade
4. Automação
5. Acessibilidade
6. Validação
7. Foco
8. Sustentabilidade comercial

## 23. Questões em aberto

1. Qual é a maior dor recorrente?
2. Qual público atender primeiro?
3. Qual tarefa desperdiça mais tempo?
4. O preço é uma barreira determinante?
5. Quais softwares são utilizados?
6. Quais funcionalidades são realmente utilizadas?
7. Quais tarefas ainda acontecem fora do BIM?
8. Qual problema conseguimos resolver mais rapidamente?
9. Qual possui maior potencial comercial?
10. Qual será o primeiro produto vendável?
11. O MVP precisa de modelagem própria?
12. IFC entra no primeiro MVP?
13. Desktop, web ou híbrido?
14. Quais componentes open source são adequados?
15. Qual modelo de cobrança reduz a barreira de entrada?

## 24. Estado atual

- **Fase:** Zero — Descoberta
- **Código:** ainda não necessário
- **MVP:** não definido
- **Tecnologia:** não definida
- **Modelo comercial:** não definido
- **Pesquisa:** iniciada com 3 engenheiros

## 25. Próximo passo

Registrar as respostas dos três engenheiros na pasta de [entrevistas](../01-pesquisa/entrevistas/), preservando o conteúdo original. Depois atualizar a [matriz de problemas](../01-pesquisa/matriz-de-problemas.md) e procurar recorrências antes de escolher o MVP.

---

> **BRABIM pretende tornar o BIM profissional mais simples e acessível sem retirar do profissional a precisão e o controle necessários ao seu trabalho.**
>
> **Não construiremos primeiro um BIM para depois procurar usuários. Construiremos, problema por problema, uma ferramenta pela qual profissionais tenham motivos reais para pagar.**

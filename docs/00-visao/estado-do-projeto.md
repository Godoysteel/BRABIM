# Estado consolidado do BRABIM

**Atualizado em:** 08/09/2026. Este registro consolida a conversa com o idealizador; as entrevistas originais permanecem preservadas.

## Visão confirmada

Simplificar o trabalho do usuário, compartilhando a visão do Esboce. O BRABIM mantém identidade e evolução independentes. O usuário deve informar o necessário, compreender os resultados e poder conferi-los. Padrões úteis, automação e ferramentas contextuais devem reduzir etapas sem retirar controle técnico.

Reaproveitar o Esboce é uma possibilidade, não uma escolha de base de código: seu repositório ainda não foi inspecionado nesta tarefa.

## Situação das entregas

| Item | Estado |
|---|---|
| Repositório | GitHub público: [Godoysteel/BRABIM](https://github.com/Godoysteel/BRABIM), branch main |
| Pesquisa | Relatos de Bruno e Paulo; dez itens na matriz, sem validação de recorrência geral |
| Equipe | Paulo será parceiro; Diego se dedicará ao projeto, contribuindo com sua experiência de engenharia |
| Interface | Referência visual familiar ao Revit, com identidade própria e fluxos simplificados |
| Protótipo | Web público no GitHub Pages |
| Geometria atual | Cômodos retangulares alinhados, divisórias únicas e portas de ligação; geometria demonstrativa sem recálculo IFC |
| IfcOpenShell | Versão 0.8.5 executada: três cenários passaram e suas malhas estão disponíveis na tela de ensaios; recálculo online pendente |
| MVP comercial | Não definido |
| Plataforma final | Web, desktop ou híbrida ainda em avaliação |
| Custos | Sem benchmark ou orçamento mensal calculado |

## Navegação

- [Equipe e responsabilidades](equipe.md)
- [Forma de trabalho proposta](forma-de-trabalho.md)
- [Escopo do protótipo](../02-produto/prototipo.md)
- [Plano de integração do IfcOpenShell](../03-arquitetura/integracao-ifcopenshell.md)
- [Decisões registradas](../04-decisoes/README.md)

## Próximas entregas

1. Revisar os [IFCs e resultados dos primeiros testes](../../experiments/ifcopenshell/README.md), já gerados com conexões explícitas.
2. Ampliar a validação de junções para outros ângulos e edição sequencial de parâmetros.
3. Medir processamento e consumo de memória.
4. Conectar a geometria calculada à planta e ao 3D; testar edição e falhas de comunicação.
5. Definir infraestrutura do motor; Paulo e Diego podem testar o protótipo público pelo link.

Não há prazo, orçamento, contas de colaboradores ou compromissos individuais confirmados.


## Editor de ambientes conectados

Implementados até oito cômodos lado a lado, nomes e medidas editáveis, esquadrias, piso, seleção em planta/3D, desfazer e salvamento local/arquivo. Profundidade e altura são comuns ao conjunto. Veja [uso, arquitetura e limitações](../02-produto/ambientes-conectados.md). O desenvolvimento prossegue sem aguardar os parceiros; a avaliação deles pode orientar ajustes posteriores.


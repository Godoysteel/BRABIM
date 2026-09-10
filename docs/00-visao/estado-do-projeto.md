# Estado consolidado do BRABIM

**Atualizado em:** 10/09/2026. Este registro consolida a conversa com o idealizador; as entrevistas originais permanecem preservadas.

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
| Geometria atual | Cômodos retangulares alinhados, divisórias únicas e portas de ligação; geometria demonstrativa por padrão, com opção de motor real (IFC), incluindo telhado, para o ambiente ativo isolado no app desktop |
| IfcOpenShell | Versão 0.8.5; integrado de verdade ao app desktop via processo local (sidecar) — ver [integração](../03-arquitetura/integracao-ifcopenshell.md). Cobre o retângulo de 4 paredes de um ambiente isolado, com porta, janela, telhado (4 águas, OCCT) e agora pilares/viga de cinta cortados/calculados de verdade, com armação real opcional; piso e ambientes conectados ainda não |
| Público prioritário | Estudante; modelo comercial confirmado ([0007](../04-decisoes/0007-publico-estudante-comercial.md)); não validado pela pesquisa existente (feita com profissionais atuantes) |
| MVP comercial | Não definido |
| Plataforma final | Desktop — decidido; empacotamento (Tauri + sidecar IfcOpenShell/OCCT) validado de ponta a ponta, incluindo instalador Windows real gerado e testado localmente ([0006](../04-decisoes/0006-plataforma-desktop-e-retorno-ifcopenshell.md), [detalhes](../../experiments/desktop-sidecar/README.md#ponta-tauri-fechada-instalador-real-gerado-e-testado-10092026)) |
| Custos | Sem benchmark ou orçamento mensal calculado |
| Licenciamento | Pendente ([0002](../04-decisoes/0002-reutilizacao-e-ifcopenshell.md)) — revisão jurídica da licença LGPL do IfcOpenShell/OCCT antes de cobrar por qualquer versão; se inviável, IfcOpenShell/OCCT são dispensados |

## Navegação

- [Equipe e responsabilidades](equipe.md)
- [Forma de trabalho proposta](forma-de-trabalho.md)
- [Escopo do protótipo](../02-produto/prototipo.md)
- [Plano de integração do IfcOpenShell](../03-arquitetura/integracao-ifcopenshell.md)
- [Decisões registradas](../04-decisoes/README.md)

## Próximas entregas

1. Estender o motor real para ambientes conectados (paredes compartilhadas, portas de ligação) — hoje só cobre um ambiente isolado.
2. Ampliar a validação de junções para outros ângulos e edição sequencial de parâmetros.
3. Medir processamento e consumo de memória com modelos maiores (múltiplos ambientes).
4. Adicionar piso ao cálculo real do motor (porta, janela e telhado já calculam de verdade; falta o piso).
5. Expor controles de inclinação/beiral do telhado na interface (hoje fixos no código) e testar contornos não retangulares.
6. Resolver a pendência de licenciamento (LGPL) antes de qualquer cobrança; Paulo e Diego podem testar o protótipo público pelo link.
7. Otimizar o recálculo quando "Estrutura" e "Armação" estão ligados juntos (~4 s por edição hoje, ver [integração](../03-arquitetura/integracao-ifcopenshell.md#pilares-e-vigas-cinta-reais-10092026)), se isso incomodar no uso real.
8. Testar a instalação de fato do `.msi`/`setup.exe` gerados (só o `app.exe` cru foi testado), assinatura de código (hoje sem assinatura — Windows deve alertar como "editor desconhecido") e empacotamento para macOS/Linux.

Não há prazo, orçamento, contas de colaboradores ou compromissos individuais confirmados.


## Editor de ambientes conectados

Implementados até oito cômodos lado a lado, nomes e medidas editáveis, esquadrias, piso, seleção em planta/3D, desfazer e salvamento local/arquivo. Profundidade e altura são comuns ao conjunto. Veja [uso, arquitetura e limitações](../02-produto/ambientes-conectados.md). O desenvolvimento prossegue sem aguardar os parceiros; a avaliação deles pode orientar ajustes posteriores.


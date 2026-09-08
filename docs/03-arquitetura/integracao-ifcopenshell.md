# Integração do IfcOpenShell

**Data:** 08/09/2026. **Status:** autorizada, preparação local iniciada; integração não concluída.

## Objetivo

Reutilizar a geração de geometria e encontros do IfcOpenShell no BRABIM. O usuário permanece na interface do BRABIM; não precisa abrir Revit ou Blender. A biblioteca é uma dependência técnica incorporada à solução.

O pacote 0.8.5 foi preparado em `.runtime/python`, fora do versionamento. A presença do pacote foi conferida por seus metadados; não representa comprovação de execução, junções ou integração com a viewport.

## Arquitetura a experimentar

**Edição no BRABIM → parâmetros e conexões → adaptador → IfcOpenShell → geometria e identificadores → planta e 3D.**

O adaptador deve isolar a aplicação das particularidades da API, conservar identificadores e unidades e comunicar falhas sem apresentar resultados antigos como se fossem atuais.

Para a primeira prova, gerar um arquivo e a geometria separadamente. Em seguida, avaliar um serviço Python para processamento dinâmico. A hospedagem atual da interface não está configurada para esse motor Python; não assumir que basta instalar o pacote no frontend.

Em uma futura edição desktop, o motor poderá ser empacotado localmente. Para a opção web com servidor, haverá comunicação de rede. Nenhuma dessas opções foi definida como plataforma final.

## Validação prevista

| Caso | Evidência necessária |
|---|---|
| Cinco paredes atuais | Elementos e relações preservados |
| Cantos em L e encontros em T | Fechamento e ausência de sobreposição indevida |
| Espessuras diferentes | Recalcular sem frestas e conferir geometria |
| Alturas e ângulos diferentes | Registrar resultados e limitações, sem presumir suporte correto |
| Edição repetida | Planta e 3D representam a mesma revisão |
| Falha do motor | Mensagem clara e último resultado identificado como anterior |

Medir duração, memória e tamanho das respostas; não há medições concluídas. Diego poderá conferir os casos e Paulo revisar critérios técnicos, conforme divisão proposta.

## Custos e atualizações

Não foi identificado custo de assinatura por usuário do IfcOpenShell. O planejamento deve considerar integração, testes, manutenção e processamento/armazenamento quando houver servidor. Não há orçamento mensal ou promessa de hospedagem gratuita.

Usar versão explícita, começando pelo experimento com 0.8.5; preparar dependências reproduzíveis antes da adoção. Não atualizar automaticamente o motor. Avaliar cada atualização com casos de referência, comparação de geometria, desempenho e compatibilidade; manter forma de retornar à versão anterior. Versões antigas também podem demandar correções e acompanhamento.

Os metadados locais indicam LGPLv3 ou posterior. O código de Bonsai consultado declara GPLv3 ou posterior e deve ser avaliado separadamente. A forma de distribuição e as obrigações aplicáveis ainda precisam ser analisadas; não foi aprovada uma estratégia de licenciamento do BRABIM.

## Fontes consultadas na pesquisa

- [Regeneração de paredes na API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/geometry/regenerate_wall_representation/index.html)
- [Código e aviso de licença do módulo](https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.8.0/src/ifcopenshell-python/ifcopenshell/api/geometry/regenerate_wall_representation.py)
- [Comparação inicial com alternativas](reaproveitamento-open-source.md)

As referências de código são de uma branch consultada, não um commit imutável correspondente à instalação 0.8.5. Conferir o artefato fixado ao implementar.

# 0002 — Reutilização e avaliação do IfcOpenShell

**Data:** 08/09/2026. **Status:** reutilização e trabalho de integração autorizados; arquitetura definitiva pendente.

## Contexto

As junções do protótipo exibem sobras e sobreposições. O idealizador pediu pesquisar código aberto antes de desenvolver soluções próprias e autorizou integrar IfcOpenShell após discutir custos e atualizações.

## Decisão

Priorizar soluções existentes. Iniciar a integração por prova de conceito com IfcOpenShell, usar versão fixa e medir desempenho e recursos antes de definir infraestrutura. Atualizações somente após testes.

## Alternativas e consequências

Blueprint3D permanece candidato a adaptação no frontend. Algoritmo próprio só deve ser considerado diante de lacuna demonstrada. O motor Python exige uma estratégia de execução; não é importado diretamente no frontend. Haverá trabalho de adaptação e manutenção mesmo sem assinatura da biblioteca.

Não há serviço externo contratado, custo mensal estimado, biblioteca integrada à publicação ou obrigação de usar uma plataforma final específica.

## Referências

[Pesquisa de componentes](../03-arquitetura/reaproveitamento-open-source.md) · [Integração e validação](../03-arquitetura/integracao-ifcopenshell.md)

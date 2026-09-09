# 0002 — Reutilização e avaliação do IfcOpenShell

**Data:** 08/09/2026. **Status:** reutilização e trabalho de integração autorizados; arquitetura definitiva pendente.

## Contexto

As junções do protótipo exibem sobras e sobreposições. O idealizador pediu pesquisar código aberto antes de desenvolver soluções próprias e autorizou integrar IfcOpenShell após discutir custos e atualizações.

## Decisão

Priorizar soluções existentes. Iniciar a integração por prova de conceito com IfcOpenShell, usar versão fixa e medir desempenho e recursos antes de definir infraestrutura. Atualizações somente após testes.

## Alternativas e consequências

Blueprint3D permanece candidato a adaptação no frontend. Algoritmo próprio só deve ser considerado diante de lacuna demonstrada. O motor Python exige uma estratégia de execução; não é importado diretamente no frontend. Haverá trabalho de adaptação e manutenção mesmo sem assinatura da biblioteca.

Não há serviço externo contratado, custo mensal estimado, biblioteca integrada à publicação ou obrigação de usar uma plataforma final específica.

## Pendência de licenciamento (08/09/2026)

A avaliação jurídica da licença LGPL do IfcOpenShell (e do OCCT, mesma família de licença, usado em [experimento paralelo](../../experiments/opencascade-wasm/README.md)) ainda não foi feita — só uma leitura técnica informal indicando que LGPL, ao contrário de GPL, permite uso comercial/proprietário sem abrir o código do BRABIM, desde que o código-fonte da própria biblioteca continue disponível e sua substituição permaneça possível (ex.: distribuir o motor empacotado como pasta de arquivos, não um único executável monolítico). O idealizador confirmou a contingência: **se a revisão jurídica de fato indicar que a licença é inviável para o modelo comercial do BRABIM, o IfcOpenShell/OCCT são dispensados e o projeto segue por outro caminho** (possivelmente algoritmo próprio, sem eles). Essa revisão formal continua pendente e deve acontecer antes de cobrar por qualquer versão do produto.

Bonsai (GPL-3.0-or-later, mais restritivo) segue descartado como dependência direta, usado só como referência de estudo — essa parte já está decidida, não faz parte da pendência acima.

## Referências

[Pesquisa de componentes](../03-arquitetura/reaproveitamento-open-source.md) · [Integração e validação](../03-arquitetura/integracao-ifcopenshell.md)

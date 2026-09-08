# Protótipo de experiência

**Data:** 08/09/2026. **Status:** versão web implementada e publicada; não equivale ao MVP comercial.

## Direção confirmada

Aparência familiar ao Revit: ferramentas no topo, propriedades e navegador do projeto à esquerda, viewport ampla e vistas de planta e 3D. Identidade própria do BRABIM. A simplificação deve ocorrer nas operações, padrões e quantidade de passos.

O navegador permite experimentar a interface sem instalação. Isso não define a plataforma final do produto.

## Fluxo disponível

Selecionar uma das cinco paredes do ambiente de exemplo, editar altura ou espessura, aplicar saindo do campo ou pressionando Enter e conferir o resultado nas vistas. Também há seleção pela lista, desfazer, ocultação de painéis e reenquadramento 3D.

Three.js fornece renderização, raycasting e navegação 3D. React e componentes de interface existentes foram reaproveitados.

## Limites atuais

- Alterações somente na sessão; recarregar restaura o exemplo.
- Sem importação IFC, criação livre, portas, salvamento ou colaboração simultânea.
- Paredes independentes, com encontros ainda não resolvidos geometricamente.
- Área exibida é bruta, calculada por comprimento no eixo × altura, sem descontos; não usar como quantitativo executivo.
- Acesso publicado inicialmente privado ao proprietário; equipe ainda não habilitada.
- Compilação, tipos e resposta HTTP local foram verificados; não houve teste completo de interação ou validação profissional.

Um fluxo com criação de ambiente e porta foi discutido como possibilidade futura; não foi entregue nem adotado como escopo comercial.

[Abrir protótipo](https://brabim-prototipo.godoy13.chatgpt.site) · [Instruções locais](../../prototipo/README.md)

# Protótipo BRABIM

Aplicação web para avaliar seleção de paredes e edição de altura e espessura em planta e 3D. Modelo sintético de cinco paredes; valores em metros. Alterações permanecem apenas na sessão e desaparecem ao recarregar.

## Executar

Requer Node.js >=22.13.0. Execute `npm ci` e `npm run dev` nesta pasta. `npm run build` gera a versão para hospedagem. `npx tsc --noEmit` verifica os tipos.

## Escopo e limites

- Seleção sincronizada em planta, perspectiva e lista; campos com limites; desfazer; reenquadrar câmera 3D.
- O enquadramento da planta é fixo. Medidas do exemplo são entre eixos.
- Área mostrada é comprimento no eixo × altura, sem descontar encontros ou aberturas; não usar como quantitativo executivo.
- Não implementa criação livre de paredes, portas, IFC, salvamento ou colaboração simultânea.
- Edição de espessura é centrada no eixo e não resolve encontros automaticamente.

## Reaproveitamento open source

Three.js: renderização, seleção por raycasting e OrbitControls (licença MIT). React e componentes shadcn/Base UI: estado e controles de interface. Dependências e versões exatas estão em package-lock.json; avisos originais permanecem nos pacotes distribuídos pelo empacotador. Não foi implementado kernel BIM próprio.

Documentação consultada: https://threejs.org/manual/en/installation.html e https://threejs.org/docs/pages/OrbitControls.html.

## Validação

O suporte WebMCP é opcional e oferece seleção de parede existente. Não houve contexto WebMCP disponível para verificar o contrato em execução. Não foram solicitados testes de interface no navegador; a validação inclui compilação, tipos e resposta HTTP local.

## GitHub Pages

Publicação pública: https://godoysteel.github.io/BRABIM/ (editor) e https://godoysteel.github.io/BRABIM/ensaios/ (resultados IFC). O comando npm run build:pages gera arquivos estáticos em dist-pages. O workflow pages.yml publica automaticamente alterações no protótipo na branch main. Não executa o motor Python online.


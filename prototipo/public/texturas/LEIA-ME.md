# Texturas de alvenaria

Biblioteca visual gerada com image_gen integrado. Contém seis paredes montadas com fiadas e juntas de argamassa, seis imagens individuais para seleção e oito materiais de superfície/acabamento. São 42 mapas PBR, mais seis cópias JPG de acesso direto e seis imagens de catálogo.

## Caminhos das paredes

| Tipo | Cor da parede | Imagem individual |
|---|---|---|
| Baiano 6 furos | [baiano-6.jpg](baiano-6.jpg) | [Peça](catalogo/baiano-6.jpg) |
| Baiano 8 furos | [baiano-8.jpg](baiano-8.jpg) | [Peça](catalogo/baiano-8.jpg) |
| Baiano 9 furos | [baiano-9.jpg](baiano-9.jpg) | [Peça](catalogo/baiano-9.jpg) |
| Cerâmico estrutural | [ceramico-estrutural.jpg](ceramico-estrutural.jpg) | [Peça](catalogo/ceramico-estrutural.jpg) |
| Concreto | [bloco-concreto.jpg](bloco-concreto.jpg) | [Peça](catalogo/bloco-concreto.jpg) |
| Maciço | [tijolo-macico.jpg](tijolo-macico.jpg) | [Peça](catalogo/tijolo-macico.jpg) |

O arquivo `texturas/<id>.jpg` representa a **parede assentada**, já com argamassa. Os furos internos dos blocos não aparecem na face externa. A peça isolada em `catalogo/` serve para o seletor, não para revestir a parede.

Cada pasta `pbr/<id>/` contém:

- `basecolor.jpg`: cor da alvenaria e das juntas; carregar como sRGB.
- `normal.png`: relevo visual, convenção OpenGL +Y solicitada na geração; carregar como dados, sem conversão sRGB.
- `roughness.png`: rugosidade; branco = mais rugoso, preto = mais liso; carregar como dados.

## Superfícies e camadas

As pastas abaixo ficam em `materiais/`, cada uma com os mesmos três mapas:

| ID | Aplicação |
|---|---|
| ceramica-natural | Superfície de uma peça cerâmica, sem fiadas |
| ceramica-macica | Superfície de tijolo maciço, sem fiadas |
| concreto-bloco | Superfície de uma peça de concreto |
| argamassa-assentamento | Argamassa em juntas modeladas individualmente |
| chapisco | Camada de aderência com textura grossa |
| emboco | Regularização com granulação intermediária |
| reboco | Acabamento mineral fino |
| pintura-branca | Acabamento de pintura fosca |

Estes são os acabamentos incluídos nesta versão, não uma lista exaustiva de sistemas de parede. As quatro peças cerâmicas vazadas podem compartilhar ceramica-natural quando modeladas individualmente; a forma dos furos deve vir da geometria.

## Integração

O [catalogo.json](catalogo.json) relaciona nomes, imagens, mapas e dimensões. Seus caminhos são relativos a `public/`. No Vite, prefixar com `import.meta.env.BASE_URL` para respeitar a publicação sob `/BRABIM/`. Não colocar `public/` na URL.

Usar metalness = 0. Com roughnessMap, iniciar roughness = 1; o campo roughnessFallback é uma alternativa quando não há mapa. Os valores de normalScale são sugestões visuais iniciais, não medidas físicas. Usar as mesmas coordenadas UV, repetição e orientação nos três mapas de um conjunto. Carregar apenas o material escolhido e reutilizar texturas em cache.

## Estado e limites

Estes conjuntos são **protótipos visuais gerados por IA**, não digitalizações calibradas de fabricantes. As dimensões mencionadas nos prompts orientam a aparência e não certificam a escala da textura. Não usar as imagens para quantitativos, propriedades mecânicas ou dimensionamento.

Os mapas foram gerados separadamente usando a cor como referência: a correspondência é aproximada, não um bake matemático de uma geometria comum. Foram verificadas a abertura integral dos arquivos, as dimensões iguais dentro de cada conjunto e a presença visual das fiadas/juntas. A periodicidade das bordas, o alinhamento preciso dos mapas, a direção efetiva das normais e a escala métrica ainda precisam de validação no renderizador; `tileableVerified` é false e `physicalScaleMeters` é null. Há pequenas sombras e variações de geração que podem exigir refinamento para uso final.

Normal map altera a iluminação aparente; não cria volume, silhueta ou furos. Para cortes e detalhes construtivos, usar geometria. Não foram incluídos mapas de deslocamento, AO ou metalness.

Os arquivos estão preparados no projeto; a interface e a publicação não foram alteradas nesta entrega. Prompts e arquivos de origem estão em `documentos/alvenaria-fontes.json`; o script `documentos/organizar-texturas.cjs` registra a organização e conversão JPG, preservando os PNG originais de normal e rugosidade.

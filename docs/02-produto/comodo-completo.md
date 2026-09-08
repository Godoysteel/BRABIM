# Cômodo retangular — primeira implementação

O editor principal passa a configurar um cômodo com quatro paredes, porta na parede sul, janela na parede norte e piso. Dimensões internas, altura e espessura são editáveis; posição horizontal e dimensões das aberturas também. O piso acompanha o contorno externo.

## Implementação e escopo

Geometria demonstrativa montada com BoxGeometry e BufferGeometry do Three.js. Laterais terminam nas faces das paredes norte e sul, sem volumes coincidentes nos cantos deste caso retangular. Segmentos em torno das aberturas deixam vãos reais no 3D. Esquadrias são representações esquemáticas, não famílias executivas.

Isso não é recálculo IFC nem substitui um motor geral de junções. A tela de ensaios IFC continua disponível, separada do editor. Não há criação livre, múltiplos cômodos, paredes inclinadas, materiais em camadas ou cálculo estrutural.

## Salvamento

Salvar no navegador guarda explicitamente uma cópia local; Reabrir salvo recupera essa cópia. Não há sincronização entre computadores. Exportar arquivo e Abrir arquivo permitem transferir projetos em JSON com formato brabim-room, versão 1. Esse arquivo não é IFC. Importações inválidas preservam o estado atual. O histórico de desfazer mantém até 50 configurações e não é persistido.

## Validação

Build estático e TypeScript aprovados. Onze verificações automatizadas cobrem serialização/reabertura, limites dimensionais, abertura que não cabe e versões inválidas. Revisão visual e testes profissionais ainda pendentes; não usar para execução de obra.

## Roteiro para Diego e Paulo

1. Alterar largura, profundidade, espessura e altura; comparar planta e 3D.
2. Mover e redimensionar porta e janela; conferir os vãos e as mensagens de limite.
3. Salvar, recarregar e reabrir; depois exportar e importar o arquivo.
4. Anotar dúvidas e resultados inesperados com medidas e imagem.

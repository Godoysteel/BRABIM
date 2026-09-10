// Catálogo inicial de tijolos e blocos (dimensões-padrão do mercado
// brasileiro; peças/m² conforme referência de consumo comum do setor).
// `image` aponta para onde as texturas (geradas separadamente) devem
// ficar -- até existirem, a interface cai para um retângulo com o nome.
export type BrickType = {id:string; name:string; width:number; height:number; length:number; piecesPerM2:number; image:string};
export const brickCatalog: BrickType[] = [
  {id:'baiano-6', name:'Tijolo baiano (6 furos)', width:.09, height:.19, length:.29, piecesPerM2:17, image:'/texturas/baiano-6.jpg'},
  {id:'baiano-8', name:'Tijolo baiano (8 furos)', width:.09, height:.19, length:.19, piecesPerM2:25, image:'/texturas/baiano-8.jpg'},
  {id:'baiano-9', name:'Tijolo baiano (9 furos)', width:.14, height:.19, length:.24, piecesPerM2:20, image:'/texturas/baiano-9.jpg'},
  {id:'ceramico-estrutural', name:'Bloco cerâmico estrutural', width:.14, height:.19, length:.39, piecesPerM2:13, image:'/texturas/ceramico-estrutural.jpg'},
  {id:'concreto', name:'Bloco de concreto', width:.14, height:.19, length:.34, piecesPerM2:15, image:'/texturas/concreto.jpg'},
  {id:'macico', name:'Tijolo maciço', width:.105, height:.05, length:.225, piecesPerM2:88, image:'/texturas/tijolo-macico.jpg'},
];

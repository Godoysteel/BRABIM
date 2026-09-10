// Catálogo inicial de tijolos e blocos (dimensões-padrão do mercado
// brasileiro; peças/m² conforme referência de consumo comum do setor).
// `image` é a peça isolada em texturas/catalogo/ (pensada pro seletor,
// não pra revestir a parede -- ver public/texturas/LEIA-ME.md), os ids
// batem com public/texturas/catalogo.json pra facilitar ligar os mapas
// PBR completos (basecolor/normal/roughness) depois. São protótipos
// visuais gerados por IA, não digitalização calibrada -- não usar pra
// quantitativo ou dimensionamento real (mesmo aviso do LEIA-ME.md).
// `pbr` aponta pro conjunto completo (basecolor/normal/roughness) em
// texturas/pbr/<id>/, o mesmo mapeado em public/texturas/catalogo.json --
// usado pra texturizar a parede de verdade no 3D, diferente de `image`
// que é só a miniatura do seletor.
export type BrickType = {id:string; name:string; width:number; height:number; length:number; piecesPerM2:number; image:string; pbr:{baseColor:string; normal:string; roughness:string}};
function pbr(id:string){return {baseColor:`/texturas/pbr/${id}/basecolor.jpg`, normal:`/texturas/pbr/${id}/normal.png`, roughness:`/texturas/pbr/${id}/roughness.png`};}
export const brickCatalog: BrickType[] = [
  {id:'baiano-6', name:'Tijolo baiano (6 furos)', width:.09, height:.19, length:.29, piecesPerM2:17, image:'/texturas/catalogo/baiano-6.jpg', pbr:pbr('baiano-6')},
  {id:'baiano-8', name:'Tijolo baiano (8 furos)', width:.09, height:.19, length:.19, piecesPerM2:25, image:'/texturas/catalogo/baiano-8.jpg', pbr:pbr('baiano-8')},
  {id:'baiano-9', name:'Tijolo baiano (9 furos)', width:.14, height:.19, length:.24, piecesPerM2:20, image:'/texturas/catalogo/baiano-9.jpg', pbr:pbr('baiano-9')},
  {id:'ceramico-estrutural', name:'Bloco cerâmico estrutural', width:.14, height:.19, length:.39, piecesPerM2:13, image:'/texturas/catalogo/ceramico-estrutural.jpg', pbr:pbr('ceramico-estrutural')},
  {id:'bloco-concreto', name:'Bloco de concreto', width:.14, height:.19, length:.34, piecesPerM2:15, image:'/texturas/catalogo/bloco-concreto.jpg', pbr:pbr('bloco-concreto')},
  {id:'tijolo-macico', name:'Tijolo maciço', width:.105, height:.05, length:.225, piecesPerM2:88, image:'/texturas/catalogo/tijolo-macico.jpg', pbr:pbr('tijolo-macico')},
];

// Bitolas comerciais de vergalhão (NBR 7480) -- diâmetro e massa por
// metro são valores tabelados padrão, não calculados por nós. CA-60 é a
// bitola mais fina, tipicamente usada em estribo; CA-50 nas barras
// longitudinais principais. Isto é geometria e quantitativo (kg/m
// real), não dimensionamento -- a quantidade/bitola usada continua
// escolha do projetista, não um cálculo estrutural do BRABIM.
export type RebarType = {id:string; diameter:number; steelClass:'CA-50'|'CA-60'; massPerMeter:number};
export const rebarCatalog: RebarType[] = [
  {id:'4.2', diameter:.0042, steelClass:'CA-60', massPerMeter:.109},
  {id:'5.0', diameter:.005, steelClass:'CA-60', massPerMeter:.154},
  {id:'6.3', diameter:.0063, steelClass:'CA-50', massPerMeter:.245},
  {id:'8.0', diameter:.008, steelClass:'CA-50', massPerMeter:.395},
  {id:'10.0', diameter:.01, steelClass:'CA-50', massPerMeter:.617},
  {id:'12.5', diameter:.0125, steelClass:'CA-50', massPerMeter:.963},
];
export type RebarSpec = {longitudinal:string; longitudinalCount:number; stirrup:string; stirrupSpacing:number};
export const initialRebarSpec: RebarSpec = {longitudinal:'8.0', longitudinalCount:4, stirrup:'5.0', stirrupSpacing:.15};

// PBR real (não gerado por IA) por nome de material genérico -- separado
// do catálogo de tijolo porque a fonte é outra (ambientCG, CC0 -- domínio
// público, livre pra embutir em software) e a chave é o texto que o
// motor já manda em `material` (ex. 'Concreto' nas vergas/contravergas),
// não um id de catálogo escolhido pelo usuário.
export const materialTextures: Record<string,{baseColor:string; normal:string; roughness:string}> = {
  'Concreto': {baseColor:'/texturas/pbr/concreto/basecolor.png', normal:'/texturas/pbr/concreto/normal.png', roughness:'/texturas/pbr/concreto/roughness.png'},
};

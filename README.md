# BRABIM

Software BIM profissional com foco em simplicidade, produtividade, acessibilidade e interoperabilidade.

> **Complexidade no motor. Simplicidade na tela.**

## Status

🟡 **Fase Zero — Descoberta**

O BRABIM está atualmente em fase de pesquisa e validação do problema. O primeiro MVP ainda não foi definido.

## Objetivo

Investigar as principais dificuldades enfrentadas por profissionais no uso de softwares BIM e desenvolver soluções mais simples e acessíveis para problemas de alto valor.

O BRABIM não pretende começar tentando reproduzir todas as funcionalidades das grandes plataformas BIM.

**Problema → Validação → Solução → Protótipo → Usuário → MVP → Receita → Expansão**

## Protótipo web

O [protótipo de edição de paredes](https://brabim-prototipo.godoy13.chatgpt.site) permite selecionar paredes, editar altura e espessura e conferir planta e 3D. Acesso inicialmente privado ao proprietário. Veja [execução local e limites](prototipo/README.md). As alterações do modelo duram apenas a sessão.

## Documentação do projeto

- [Documento mestre](docs/00-visao/documento-mestre.md) — visão e princípios do projeto
- [Equipe e responsabilidades](docs/00-visao/equipe.md) — participantes e divisão inicial proposta
- [Pesquisa](docs/01-pesquisa/README.md) — entrevistas e evidências de mercado
- [Matriz de problemas](docs/01-pesquisa/matriz-de-problemas.md) — consolidação dos problemas identificados
- [Produto](docs/02-produto/README.md) — definição do produto e MVP
- [Arquitetura](docs/03-arquitetura/README.md) — arquitetura técnica
- [Decisões](docs/04-decisoes/README.md) — decisões importantes do projeto

## Organização dos arquivos

A raiz contém a apresentação do projeto. A documentação fica em `docs/`, organizada por assunto. Cada documento deve ter uma única versão de referência.

Use nomes em minúsculas, sem acentos e separados por hífens. Registre entrevistas em `docs/01-pesquisa/entrevistas/`, seguindo o padrão `entrevista-NNN-nome.md`. Preserve os relatos existentes e vincule as análises às respectivas fontes.

## Situação atual

A pesquisa inicial com profissionais já começou. Três engenheiros foram convidados a relatar as principais dificuldades encontradas em seu trabalho com softwares BIM.

Há uma [entrevista consolidada com Bruno Porto](docs/01-pesquisa/entrevistas/entrevista-001-bruno-porto.md) e um [relato inicial de Paulo](docs/01-pesquisa/entrevistas/entrevista-002-paulo.md). A matriz reúne dez itens para investigação. Os relatos ainda precisam de aprofundamento para avaliar recorrência e priorizar problemas.

## Projetos relacionados

O BRABIM é independente do Esboce. Conhecimentos adquiridos no desenvolvimento do Esboce poderão servir como referência, mas os dois produtos possuem objetivos e evolução independentes.

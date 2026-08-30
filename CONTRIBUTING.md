# Contribuindo com o Traduções pt-BR

Obrigado pelo interesse em melhorar a tradução para português do Brasil dos
mods do Factorio! Este documento descreve o fluxo de contribuição e o
**glossário canônico** que toda tradução deve seguir.

Leia também o [CLAUDE.md](CLAUDE.md) para a arquitetura interna dos locales e as
rotinas de manutenção, e o [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## 1. Como o pacote funciona

- O mod `slondo-ptbr` é **somente locale**: contém apenas `locale/pt-BR/*.cfg`
  (e alguns _overrides_ condicionais em `data.lua`).
- O motor do Factorio resolve tradução **chave a chave**. Se uma chave não
  existir aqui, o jogo usa o texto do mod original (em geral inglês).
- O pacote é **autônomo**: traz tradução para todo o ecossistema coberto,
  inclusive AAI, LTN e Bob's. Também funciona como **_fallback_** — se os
  pacotes mantidos pela comunidade (**AAI Language Pack**, **LTN Language
  Pack**, **Bob's Locale**) estiverem ativos, o texto **deles** deve
  prevalecer. Isso é garantido por **paridade**: as chaves em comum são cópia
  fiel do texto atual desses pacotes, e **nunca** declaramos dependência deles
  no `info.json`. Detalhes em [`CLAUDE.md`](CLAUDE.md) §3 e §12.
- Fonte primária de tradução: o pt-BR aprovado no
  [Crowdin factorio-mods-localization](https://crowdin.com/project/factorio-mods-localization)
  e no [boblocale](https://crowdin.com/project/boblocale). O que falta passa
  pelo pipeline Crowdin + IA descrito em [`CLAUDE.md`](CLAUDE.md) §11.

## 2. Estrutura de um arquivo `.cfg`

```ini
[item-name]
minha-chave=Meu item

[entity-description]
minha-entidade=Descrição com __1__ parâmetro e quebra de linha.\nSegunda linha.
```

- Formato INI: seções entre colchetes, linhas `chave=valor`.
- Codificação **UTF-8 sem BOM**, quebras de linha **LF**, sem espaço em branco
  no fim das linhas.
- Um arquivo por mod, nomeado como o mod (ex.: `aai-industry.cfg`). Quando um
  mod tem muitas chaves, é aceitável dividir por categoria com o sufixo
  ` - <categoria>` (ex.: `Bio_Industries_2 - item-name.cfg`).

### Marcadores que **nunca** podem ser corrompidos

| Marcador | Significado |
|---|---|
| `__1__`, `__2__`, … | Parâmetros posicionais |
| `__ENTITY__nome__` | Nome localizado de entidade |
| `__ITEM__nome__` | Nome localizado de item |
| `__CONTROL__acao__` | Tecla/atalho vinculado à ação |
| `__ALT_CONTROL__n__acao__` | Variante de atalho |
| `__plural_for_parameter__n__{...}__` | Pluralização |
| `\n` | Quebra de linha (literal, dois caracteres) |

Nunca insira espaços dentro dos marcadores (`__ 1 __` é inválido). `__1__ __2__`
com espaço **entre** dois marcadores é legítimo.

## 3. Fluxo de contribuição

1. Faça um _fork_ e crie um _branch_ descritivo (`traducao/<mod>`,
   `correcao/<mod>`).
2. Rode a validação local antes de commitar:
   ```bash
   python3 tools/validate_locale.py locale/pt-BR
   ```
3. _Commits_ no formato convencional: `feat:`, `fix:`, `chore:`, `docs:`.
   Um _commit_ temático por mod ou por lote de correção.
4. Abra o _Pull Request_ descrevendo os mods afetados e a fonte das traduções
   (Crowdin, upstream do mod, YKR, tradução nova).
5. A CI (`.github/workflows/validate.yml`) precisa passar.

## 4. Regras de tradução

- **Siga o glossário da seção 5.** O validador sinaliza divergências.
- Mantenha a capitalização no padrão do jogo base: nomes de itens/entidades em
  _sentence case_ (só a primeira letra maiúscula), salvo nomes próprios.
- Não traduza nomes próprios, nomes de mods, nem chaves.
- Preserve os marcadores e o `\n` exatamente como no texto original.
- Prefira o infinitivo em títulos de ação e a 3ª pessoa em descrições, como no
  jogo base.
- Números decimais com vírgula (`1,5`), como no restante do jogo em pt-BR.

## 5. Glossário canônico PT-BR

Base: Factorio 2.0 _vanilla_ (pt-BR) + expansão _Space Age_. Coluna **Nota**:
`revisar` = termo provável, confirme contra o jogo base antes de divergir.

### 5.1 Logística e transporte

| EN | PT-BR | Nota |
|---|---|---|
| Inserter | Insersor | |
| Burner Inserter | Insersor a combustão | |
| Fast Inserter | Insersor rápido | |
| Long-handed Inserter | Insersor de longo alcance | |
| Bulk Inserter | Insersor em massa | (ex-"Stack Inserter") |
| Belt | Esteira | |
| Transport Belt | Esteira de transporte | |
| Fast Transport Belt | Esteira de transporte rápida | |
| Express Transport Belt | Esteira de transporte expressa | |
| Underground Belt | Esteira subterrânea | |
| Splitter | Divisor | |
| Loader | Carregador | |
| Chest | Baú | |
| Wooden Chest | Baú de madeira | |
| Iron Chest | Baú de ferro | |
| Steel Chest | Baú de aço | |
| Storage Tank | Tanque de armazenamento | |
| Logistic Chest | Baú logístico | |
| Passive Provider Chest | Baú fornecedor passivo | revisar |
| Active Provider Chest | Baú fornecedor ativo | revisar |
| Requester Chest | Baú solicitante | revisar |
| Buffer Chest | Baú tampão | revisar |
| Storage Chest | Baú de estoque | revisar |

### 5.2 Produção

| EN | PT-BR | Nota |
|---|---|---|
| Assembling Machine | Máquina de montagem | |
| Assembler | Máquina de montagem | |
| Furnace | Fornalha | |
| Stone Furnace | Fornalha de pedra | |
| Steel Furnace | Fornalha de aço | |
| Electric Furnace | Fornalha elétrica | |
| Chemical Plant | Usina química | |
| Oil Refinery | Refinaria de petróleo | |
| Centrifuge | Centrífuga | |
| Lab | Laboratório | |
| Recipe | Receita | |
| Module | Módulo | |
| Speed Module | Módulo de velocidade | |
| Productivity Module | Módulo de produtividade | |
| Efficiency Module | Módulo de eficiência | |
| Quality Module | Módulo de qualidade | |
| Beacon | Emissor | revisar |
| Foundry | Fundição | |
| Electromagnetic Plant | Usina eletromagnética | |
| Biochamber | Biocâmara | |
| Recycler | Reciclador | |
| Agricultural Tower | Torre agrícola | |
| Cryogenic Plant | Usina criogênica | revisar |

### 5.3 Mineração e fluidos

| EN | PT-BR | Nota |
|---|---|---|
| Burner Mining Drill | Perfuratriz a combustão | |
| Electric Mining Drill | Perfuratriz elétrica | |
| Big Mining Drill | Perfuratriz grande | revisar |
| Pumpjack | Bomba de petróleo | |
| Pipe | Cano | |
| Pipe to Ground | Cano subterrâneo | |
| Pump | Bomba | |
| Offshore Pump | Bomba costeira | revisar |
| Boiler | Caldeira | |
| Heat Pipe | Cano de calor | |
| Heat Exchanger | Trocador de calor | |

### 5.4 Energia

| EN | PT-BR | Nota |
|---|---|---|
| Steam Engine | Motor a vapor | |
| Steam Turbine | Turbina a vapor | |
| Solar Panel | Painel solar | |
| Accumulator | Acumulador | |
| Nuclear Reactor | Reator nuclear | |
| Fusion Reactor | Reator de fusão | |
| Fusion Generator | Gerador de fusão | |
| Small Electric Pole | Poste elétrico pequeno | |
| Medium Electric Pole | Poste elétrico médio | |
| Big Electric Pole | Poste elétrico grande | |
| Substation | Subestação | |
| Power Switch | Interruptor de energia | |
| Lightning Rod | Para-raios | |
| Lightning Collector | Coletor de relâmpagos | revisar |

### 5.5 Robôs e rede logística

| EN | PT-BR | Nota |
|---|---|---|
| Roboport | Roboporto | |
| Logistic Robot | Robô logístico | |
| Construction Robot | Robô de construção | |
| Logistic Network | Rede logística | |
| Personal Roboport | Roboporto pessoal | |

### 5.6 Circuitos e trens

| EN | PT-BR | Nota |
|---|---|---|
| Circuit Network | Rede de circuitos | |
| Arithmetic Combinator | Combinador aritmético | |
| Decider Combinator | Combinador decisor | |
| Constant Combinator | Combinador constante | |
| Selector Combinator | Combinador seletor | revisar |
| Locomotive | Locomotiva | |
| Cargo Wagon | Vagão de carga | |
| Fluid Wagon | Vagão de fluidos | |
| Rail | Trilho | |
| Train Stop | Parada de trem | |
| Rail Signal | Sinal ferroviário | |
| Rail Chain Signal | Sinal ferroviário em cadeia | |

### 5.7 Space Age — espaço e planetas

| EN | PT-BR | Nota |
|---|---|---|
| Space Platform | Plataforma espacial | |
| Space Platform Hub | Central da plataforma espacial | revisar |
| Cargo Bay | Compartimento de carga | |
| Cargo Landing Pad | Plataforma de pouso de carga | |
| Asteroid | Asteroide | |
| Asteroid Collector | Coletor de asteroides | |
| Thruster | Propulsor | |
| Nauvis | Nauvis | não traduzir |
| Vulcanus | Vulcanus | não traduzir |
| Gleba | Gleba | não traduzir |
| Fulgora | Fulgora | não traduzir |
| Aquilo | Aquilo | não traduzir |

### 5.8 Space Age — mecânicas

| EN | PT-BR | Nota |
|---|---|---|
| Quality | Qualidade | |
| Common | Comum | |
| Uncommon | Incomum | |
| Rare | Raro | |
| Epic | Épico | |
| Legendary | Lendário | |
| Spoilage | Deterioração | |
| to spoil | deteriorar | |
| Freshness | Frescor | revisar |
| Pentapod | Pentápode | revisar |
| Rocket Turret | Torre de foguetes | |
| Railgun | Canhão de trilho | revisar |
| Tesla Turret | Torre Tesla | |

### 5.9 Materiais e intermediários

| EN | PT-BR | Nota |
|---|---|---|
| Iron Plate | Placa de ferro | |
| Copper Plate | Placa de cobre | |
| Steel Plate | Placa de aço | |
| Iron Gear Wheel | Engrenagem de ferro | |
| Copper Cable | Cabo de cobre | |
| Electronic Circuit | Circuito eletrônico | |
| Advanced Circuit | Circuito avançado | |
| Processing Unit | Unidade de processamento | |
| Plastic Bar | Barra de plástico | |
| Sulfur | Enxofre | |
| Sulfuric Acid | Ácido sulfúrico | |
| Battery | Bateria | |
| Engine Unit | Unidade de motor | |
| Electric Engine Unit | Unidade de motor elétrico | |
| Flying Robot Frame | Estrutura de robô voador | |
| Low Density Structure | Estrutura de baixa densidade | |
| Rocket Fuel | Combustível de foguete | |
| Nuclear Fuel | Combustível nuclear | |
| Coal | Carvão | |
| Stone | Pedra | |
| Stone Brick | Tijolo de pedra | |
| Wood | Madeira | |
| Crude Oil | Petróleo bruto | |
| Heavy Oil | Óleo pesado | |
| Light Oil | Óleo leve | |
| Petroleum Gas | Gás de petróleo | |
| Lubricant | Lubrificante | |
| Water | Água | |
| Steam | Vapor | |
| Holmium | Hólmio | |
| Tungsten | Tungstênio | |
| Calcite | Calcita | |

### 5.10 Ciência

| EN | PT-BR | Nota |
|:---:|:---:|:---:|
| Automation Science Pack | Pacote de ciência de automação | |
| Logistic Science Pack | Pacote de ciência de logística | |
| Military Science Pack | Pacote de ciência militar | |
| Chemical Science Pack | Pacote de ciência química | |
| Production Science Pack | Pacote de ciência de produção | |
| Utility Science Pack | Pacote de ciência de utilidade | |
| Space Science Pack | Pacote de ciência espacial | |
| Metallurgic Science Pack | Pacote de ciência metalúrgica | revisar |
| Electromagnetic Science Pack | Pacote de ciência eletromagnética | revisar |
| Agricultural Science Pack | Pacote de ciência agrícola | revisar |
| Cryogenic Science Pack | Pacote de ciência criogênica | revisar |
| Promethium Science Pack | Pacote de ciência de promécio | revisar |

### 5.11 Interface e termos gerais

| EN | PT-BR | Nota |
|:---:|:---:|:---:|
| Research | Pesquisa | |
| Technology | Tecnologia | |
| Setting | Configuração | |
| Startup setting | Configuração de inicialização | |
| Enable | Ativar | |
| Disable | Desativar | |
| Enabled | Ativado | |
| Disabled | Desativado | |
| Blueprint | Projeto | |
| Blueprint Book | Livro de Projetos | |
| Deconstruction Planner | Planejador de demolição | |
| Upgrade Planner | Planejador de melhoria | |
| Tooltip | Dica | |
| Achievement | Conquista | |
| Surface | Superfície | |
| Tile | Bloco | revisar |
| Roboport | Roboport | Não traduzir |

## 6. Termos a **não** traduzir

- Nomes de planetas e luas (Nauvis, Vulcanus, Gleba, Fulgora, Aquilo, Cerys…).
- Nomes de mods e de autores.
- Chaves (o lado esquerdo do `=`).
- Marcas e nomes próprios em geral.
- Termos conhecidos e que não são traduzidos na base do jogo.

# Regras do projeto — Traduções pt-BR (`slondo-ptbr`)

> Carregado automaticamente por qualquer sessão de Claude Code neste repositório
> (via `@`-import no `CLAUDE.md` da raiz). **Siga estas regras à risca.** O
> `CLAUDE.md` da raiz é a referência longa; este arquivo é o contrato operacional.

---

## 1. Modelo do pacote (não negociável)

- **Autônomo (_standalone_):** `locale/pt-BR/` cobre 100% do ecossistema
  contemplado, inclusive os conteúdos de AAI, LTN e Bob's. O jogador não precisa
  de nenhum outro pacote de idioma.
- **_Fallback_ com prioridade nativa:** se `AAI Language Pack`,
  `LTN Language Pack` ou `Bob's Locale` estiverem ativos, o texto **deles**
  prevalece nas chaves em comum. Isso é garantido por **paridade de texto**
  (nossas chaves compartilhadas são cópia fiel da mesma origem no Crowdin),
  **nunca** por ordem de carga.
- **PROIBIDO:** declarar dependência (`?`, `(?)`, `!`) de `AAI_Language_Pack`,
  `LTN_Language_Pack` ou `boblocale` no `info.json`.
- Overrides de protótipo no `data.lua` para esses ecossistemas ficam sob
  `if not mods["<pack>"] then ... end`.
- O mod carrega **por último** de propósito e **não** usa `rename`.

## 2. De onde vem a tradução (ordem obrigatória)

1. **Crowdin aprovado** — `factorio-mods-localization` (pt-BR) e `boblocale`
   (mods Bob's). É a fonte primária.
2. **Espelhos dos pacotes** em `_source_mods/AAI-Language-Pack/`,
   `LTN-Language-Pack/`, `boblocale/` — cópia fiel (paridade de texto) via
   `tools/ingest_sources.py`. Só toca arquivos `locale/pt-BR/` já existentes.
3. **pt-BR _upstream_ do próprio mod** (repo/portal), sanitizado.
4. **Pipeline IA multiagente** — só para o que as fontes acima não cobrem.
   Ver §7. Nenhuma tradução legada entra sem passar pela validação (§5) e pelo
   glossário (§3).

## 3. Glossário

- A fonte é `CONTRIBUTING.md` §5. `tools/build_glossary.py` gera
  `tools/glossary.json` a partir dela.
- **NUNCA edite `tools/glossary.json` à mão.** Edite a tabela em
  `CONTRIBUTING.md` §5 e rode `python3 tools/build_glossary.py`.
- Quando um termo aparece em mais de uma subseção, a **primeira** linha vence
  (ex.: §5.7 antes de §5.11).
- Termos estáveis (consulte a tabela completa antes de traduzir):
  `Inserter → Insersor`, `Transport belt → Esteira`,
  `Assembling machine → Máquina de montagem`, `Beacon → Transmissor`,
  `Drill → Mineradora`, `Chest → Baú`,
  `Tile → Bloco`, `Blueprint → Projeto`, `Blueprint book → Livro de Projetos`,
  `stacking → empilhamento`, `Splitter → Separador`.
- Nomes em _sentence case_ (só a 1ª letra maiúscula). Vírgula decimal
  (`0,8`, não `0.8`). Termos a **não** traduzir: `CONTRIBUTING.md` §6.

## 4. Arquivos `locale/pt-BR/*.cfg`

Regras mecânicas (o validador falha se quebrar):

- Codificação UTF-8, **sem BOM**, quebras de linha **LF** (sem CRLF), o arquivo
  **termina com `\n`**, sem espaço em branco no fim das linhas.
- **Sem cabeçalho de seção repetido no mesmo arquivo** (`[x]` duas vezes →
  o Factorio dá `Failed to load locale: Duplicate key ... at ROOT`). Se duas
  fontes trazem a mesma seção, funda as chaves numa única ocorrência.
- Sem chave duplicada dentro da mesma seção.
- Chave antes do primeiro `[cabeçalho]` é válida (cai na seção raiz do
  Factorio). `[]` vazio é inválido.

Marcadores de interpolação — **nunca** corromper (sem espaço interno, mesma
contagem do `en`):

```
__1__ .. __4__   __CONTROL__x__   __ALT_CONTROL__n__x__   __ENTITY__nome__
__ITEM__nome__   __plural_for_parameter__n__{...}__   \n literal
[color=…] [img=…] [font=…] [item=…] [entity=…] [planet=…] [fluid=…]
```

Ao adicionar/ajustar um `.cfg`:

1. Extraia o template `en` do mod (de `_downloads/<mod>.zip` ou
   `_source_mods/<mod>/locale/en/`).
2. **Espelhe exatamente as chaves do `en`.** Só inclua `[mod-name]` /
   `[mod-description]` (que o `en` costuma não ter) quando agregar valor real.
3. Traduza pelas fontes da §2 + glossário da §3.
4. Rode a validação da §5.

## 5. Validação — OBRIGATÓRIA antes de todo commit

```bash
python3 tools/build_glossary.py --check
python3 tools/validate_locale.py --strict locale/pt-BR
python3 tools/validate_locale.py --standalone --source-mods ../_source_mods locale/pt-BR
python3 -m json.tool info.json > /dev/null
python3 tools/check_changelog.py changelog.txt
python3 tools/gen_mods_table.py --check
python3 tools/check_collisions.py --check
python3 tools/build_release.py --target 2.0 --dry-run
```

- Atalho: `/validar` (comando em `.claude/commands/validar.md`).
- **0 erros é obrigatório.** Avisos pré-existentes conhecidos: 3 do
  `gui-unifyer.cfg` ("inserter" em nome próprio) e ~32 no `--standalone` da
  classe "`[mod-name]`/`[mod-description]` ausente no template en". Não
  introduza avisos novos de outra classe sem justificar no commit.
- `tools/check_collisions.py`: `--check` falha se surgir uma colisão de chave
  _cross-file_ fora de `tools/collisions-baseline.txt`. Ao resolver uma,
  rode `--update-baseline`.
- **Nunca** desative hooks nem use `--dangerously-skip-permissions`.

## 6. Git, `info.json` e _release_

- **Com acesso de escrita** ao repo `github.com/odnols/Traducoes-PT-BR`:
  trabalhe **direto na `main`**, sem fork e sem pull request.
- **Sem acesso de escrita:** fork + branch (`traducao/<mod>`) + PR, como em
  `CONTRIBUTING.md` §3. As regras de tradução e validação abaixo valem igual.
- _Commits_ no formato convencional (`feat:`, `fix:`, `docs:`, `chore:`,
  `refactor:`, `ci:`, `test:`, `perf:`), corpo em português, com o _trailer_:
  ```
  Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
  ```
- **Nunca** commite: `_downloads/`, `_source_mods/`, `_translates/`, `docs/`,
  `dist/`, `scratchpad/`. Já estão no `.gitignore` — mantenha assim.
- `LICENSE` (copyright) e `info.json.author` permanecem **"Slondo"**.
- **Adicionar um mod:** `.cfg` novo + `info.json` (`? <slug>`, ordem
  alfabética _case-insensitive_) + linha no `mods.csv` (também alfabética) +
  `python3 tools/gen_mods_table.py` (MODS.md) + badge/contagem no `README.md` +
  bloco no `changelog.txt`.
- **_Release_:** para publicar, suba `info.json.version` (**nunca** retroceder)
  e adicione um bloco `Version: X.Y.Z` / `Date: DD/MM/AAAA` no `changelog.txt`
  (categorias em inglês: `Features`, `Minor Features`, `Changes`, `Bugfixes`,
  `Locale`, `Info`; corpo em português). Ao chegar na `main`, o workflow
  `.github/workflows/release.yml` valida, empacota, cria o GitHub Release
  `VX.Y.Z` (notas por `tools/release_notes.py`) e publica no portal
  (`tools/portal_upload.py`, secret `FACTORIO_API_KEY`). Retrocesso de versão
  **falha** o workflow (`tools/check_version_bump.py`).
- Variante Factorio 2.1: `build_release.py --target 2.1` (só quando os mods de
  origem migrarem — hoje o foco é 2.0).

## 7. Pipeline de tradução IA — e o _fallback_ sem Antigravity

Para chaves **sem** cobertura nas fontes da §2, a tradução passa por um _loop_
multimodal:

**Modo completo (com Antigravity):**

- Requer o CLI `agy` (Antigravity, Gemini) e o plugin
  <https://github.com/Or4cu1o/antigravity-plugin-cc>.
- `agy -p "<prompt isolado>"` — chamadas **sequenciais** (respeite _rate-limit_;
  nunca em paralelo) geram o rascunho (Gemini).
- **Claude Sonnet** revisa o rascunho contra: glossário (§3), integridade de
  marcadores (§4) e a semântica do `en`. Aceita ou reescreve.
- _Loop_ de 2–3 rodadas até estabilizar (consenso). Grava em _staging_ e roda
  `validate_locale.py --strict`.
- **Amostragem humana por mod** antes do _merge_.

**Modo _fallback_ (colaborador SEM `agy`/plugin) — permitido:**

- **Não bloqueie o trabalho.** O Claude do colaborador traduz **diretamente**
  (modelo único), mas obrigatoriamente:
  1. Esgota antes as fontes da §2 (Crowdin, espelhos, pt-BR upstream).
  2. Aplica o glossário (§3) sem exceção.
  3. Preserva todos os marcadores (§4).
  4. Faz uma **auto-revisão explícita** em passo separado: reler cada string
     contra o `en` e o glossário antes de gravar.
  5. Roda toda a validação da §5.
  6. **Sinaliza no corpo do commit** que as chaves novas foram traduzidas em
     **modelo único (sem _loop_ de consenso)** e lista os arquivos/mods
     afetados, para um mantenedor com o pipeline completo poder re-revisar.
- Nunca invente cobertura: se um mod não tem `locale/en` de origem, ele fica
  de fora (ou entra só com `[mod-name]`/`[mod-description]`).

## 8. Diretórios de trabalho (fora do repositório publicado)

Ficam um nível acima da raiz e **não entram em commits**:

| Caminho | Conteúdo |
|---|---|
| `../_downloads/` | `.zip` dos mods (têm `locale/en`, às vezes `pt-BR`) |
| `../_source_mods/` | clones dos repos dos mods e dos pacotes de idioma |
| `../docs/` | catálogos, plano e auditoria (`_auditoria/`) |

`tools/` e `.github/` são versionados, mas `build_release.py` os **exclui** do
`.zip` publicado no portal.

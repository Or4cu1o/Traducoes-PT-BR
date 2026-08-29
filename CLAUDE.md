# CLAUDE.md — Governança interna do `slondo-ptbr`

Documento de arquitetura e manutenção do pacote **Traduções pt-BR**. Para o
fluxo de contribuição e o glossário, veja [CONTRIBUTING.md](CONTRIBUTING.md).

## 1. O que é este mod

- Mod **somente locale** para o Factorio: entrega apenas `locale/pt-BR/*.cfg`.
- Nome interno: `slondo-ptbr`. Alvo atual: Factorio **2.0**.
- Consolida a tradução pt-BR de ~100+ mods de utilidade/QoL e dos ecossistemas
  AAI, LTN, Bob's e Space Age, preenchendo o que falta nos pacotes oficiais.

## 2. Arquitetura de locales

```
locale/pt-BR/
  <mod>.cfg                     # um arquivo por mod, nomeado como o mod
  <mod> - <categoria>.cfg       # opcional: recorte por categoria em mods grandes
data.lua                        # overrides condicionais de nome/descrição
```

- Formato INI; seções `[item-name]`, `[entity-name]`, `[recipe-name]`,
  `[technology-name]`, `[mod-setting-name]`, `[mod-name]`, `[mod-description]`,
  `[controls]`, `[<custom>]`.
- UTF-8 **sem BOM**, **LF**, sem espaço à direita. Garantido por
  `.gitattributes` e por `tools/validate_locale.py`.
- `data.lua`: aplica `localised_name` / `localised_description` só quando o mod
  alvo está presente (`mods["x"] ~= nil`) ou ausente, para não colidir com
  traduções que o próprio mod já traga.

## 3. Política de convivência — "oficial vence, só preenchemos lacunas"

Os pacotes **AAI Language Pack**, **LTN Language Pack** e **Bob's Locale**
usam o Crowdin e têm prioridade. Como não há como carregar depois deles sem
depender deles, a convivência é garantida **estruturalmente**:

1. **Nunca** enviar uma chave que já exista em pt-BR nesses pacotes.
2. **Nunca** declarar dependência (`?` ou `!`) desses pacotes no `info.json`.
3. Assim a ordem de carga é irrelevante: só há sobreposição nas chaves que
   nós *não* emitimos.

`tools/validate_locale.py` reprova qualquer chave nossa que coincida com a
versão pt-BR oficial correspondente em `_source_mods/*Language-Pack/` ou
`_source_mods/boblocale/`.

## 4. Hierarquia de origem por chave (estrita)

Para cada chave faltante, usar a primeira fonte disponível:

1. Tradução **finalizada/aprovada** no Crowdin `factorio-mods-localization`
   ou `boblocale`.
2. pt-BR **upstream** do próprio mod (repo/portal).
3. **YKR_PTBR** (após sanitização terminológica).
4. Tradução **já existente** neste repositório.
5. Tradução **nova** (rascunho com apoio de IA → glossário → validador →
   revisão humana). Registrar como "IA" na matriz de cobertura.

> Estado observado (Ago/2026): o Crowdin `factorio-mods-localization` está
> ~10% traduzido para pt-BR e ~0% aprovado. Os clones em
> `_source_mods/AAI-Language-Pack/` e `LTN-Language-Pack/` são espelho fiel do
> Crowdin (sincronizados via commits "Update translations from Crowdin"). Use
> os clones como fonte; não é necessário extrair string a string do Crowdin.

## 5. Fontes externas (fora deste repositório)

Ficam na raiz do _workspace_, um nível acima, e **não entram no PR**:

| Pasta | Papel |
|---|---|
| `../_downloads/` | `.zip` de mods (contêm `locale/en` e às vezes `pt-BR`) |
| `../_source_mods/` | clones de repositórios de mods e dos pacotes de idioma |
| `../_translates/` | `.zip` dos pacotes de tradução (YKR etc.) |
| `../docs/` | catálogos, plano (`PLANO.md`) e auditoria (`_auditoria/`) |

## 6. Ferramentas (`tools/`) — versionadas, fora do pacote publicado

| Script | Função |
|---|---|
| `validate_locale.py <dir>` | valida INI, marcadores, LF/BOM, cobertura vs template `en`, não-sobreposição com oficiais, aderência ao glossário |
| `build_glossary.py` | lê a tabela de `CONTRIBUTING.md` §5 e gera `tools/glossary.json` |
| `gen_mods_table.py` | regenera a tabela de mods do `README.md` a partir de `mods.csv` |
| `check_changelog.py` | valida o formato de `changelog.txt` (separador de 99 `-`, `Version:`, `Date: DD/MM/AAAA`, categorias, indentação) |
| `build_release.py --target 2.0\|2.1` | carimba `info.json.factorio_version` e empacota em `dist/` |

`tools/` e `.github/` ficam no repositório, mas `build_release.py` os
**exclui** do `.zip` publicado no portal.

## 7. Rotina de saneamento (aplicada e recorrente)

Para cada `.cfg`:

1. `validate_locale.py` para baseline.
2. Integridade de marcadores: `__1__`, `__ENTITY__x__`, `__ITEM__x__`,
   `__CONTROL__x__`, `__ALT_CONTROL__n__x__`,
   `__plural_for_parameter__n__{...}__`, `\n` — sem espaços internos, contagem
   igual à do texto `en`.
3. Glossário (`CONTRIBUTING.md` §5). Divergência vira revisão manual.
4. Gramática, acentuação e capitalização no padrão do jogo base
   (_sentence case_ em nomes; vírgula decimal).
5. `validate_locale.py` limpo.

## 8. Processo de release

1. Atualizar `changelog.txt`: novo bloco `Version: X.Y.Z`, `Date: DD/MM/AAAA`,
   categorias canônicas em inglês (`Features`, `Minor Features`, `Changes`,
   `Bugfixes`, `Locale`, `Info`), corpo em português.
2. Atualizar `info.json` (`version`, `dependencies`), `mods.csv` e a tabela do
   `README.md` (`gen_mods_table.py`).
3. `python3 tools/validate_locale.py locale/pt-BR`
4. `python3 -m json.tool info.json`
5. `python3 tools/check_changelog.py changelog.txt`
6. `python3 tools/build_release.py --target 2.0` → `dist/slondo-ptbr_X.Y.Z.zip`

## 9. Método de duplo lançamento 2.0 / 2.1

Os mods de `_downloads/` são compatíveis com 2.0 e incompatíveis com 2.1. O
portal permite publicar variantes por versão de jogo. Mantemos **um único**
`locale/` e geramos duas variantes:

- `build_release.py --target 2.0` → `factorio_version: "2.0"` (foco atual).
- `build_release.py --target 2.1` → `factorio_version: "2.1"` (apenas
  roteirizado; publicar quando o ecossistema migrar).

O conteúdo de `locale/` é idêntico entre as variantes; só muda o
`factorio_version` no `info.json` empacotado.

### Passo a passo de publicação das duas variantes

1. `python3 tools/build_release.py --target 2.0` → `dist/slondo-ptbr_<versão>.zip`
   com `factorio_version: "2.0"`.
2. Publicar esse `.zip` no portal (https://mods.factorio.com/mod/slondo-ptbr,
   aba *Downloads* → *Upload*). O portal aceita o upload como release da versão
   corrente do mod para jogos 2.0.
3. `python3 tools/build_release.py --target 2.1` → regenera o mesmo
   `dist/slondo-ptbr_<versão>.zip` agora com `factorio_version: "2.1"`.
4. Publicar esse segundo `.zip` no portal como a variante 2.1 da mesma versão
   do mod. Só executar quando o ecossistema de mods de origem migrar para 2.1.
5. `dist/` é git-ignored: os `.zip` nunca entram em commit.

## 10. Limites

- O repositório Git é **apenas** este diretório. Nada de `_downloads/`,
  `_source_mods/`, `_translates/`, `docs/` entra em _commits_.
- Sem `.zip`, arquivos temporários ou `dist/` versionados (ver `.gitignore`).
- Não abrir PR upstream sem aprovação explícita do mantenedor.

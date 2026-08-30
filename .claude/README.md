# `.claude/` — configuração de Claude Code do projeto

Faz com que **qualquer colaborador** que abra este repositório no Claude Code
siga o mesmo método de tradução, validação e _release_.

| Item | Para quê |
|---|---|
| `rules/traducao-pt-br.md` | Contrato operacional. Carregado automaticamente via `@`-import no [`CLAUDE.md`](../CLAUDE.md) da raiz. **Leitura obrigatória.** |
| `commands/validar.md` | Comando `/validar` — roda a suíte de validação inteira e diz se está pronto para commit. |
| `settings.json` | Permissões compartilhadas (libera os `tools/*.py` de checagem sem prompt). |

Ajustes pessoais (seu modelo, suas permissões extras) vão em
`.claude/settings.local.json`, que **não** é versionado.

## Colaborador sem Antigravity

O _loop_ de tradução multimodal (Gemini via `agy` + revisão Claude Sonnet)
descrito na §7 das regras precisa do CLI `agy` e do plugin
<https://github.com/Or4cu1o/antigravity-plugin-cc>. Sem eles, use o **modo
fallback** da §7: tradução em modelo único, com auto-revisão explícita,
validação completa e a marcação no commit de que as chaves não passaram pelo
_loop_ de consenso.

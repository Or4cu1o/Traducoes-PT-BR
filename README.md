# Traduções PT-BR

<p align="center">
  <img src="thumbnail.png" alt="Traduções pt-BR" width="144" height="144">
</p>

<p align="center">
  <a href="https://mods.factorio.com/mod/slondo-ptbr"><img alt="Versão no portal" src="https://img.shields.io/factorio-mod-portal/v/slondo-ptbr?label=portal&color=1f8acb"></a>
  <a href="https://mods.factorio.com/mod/slondo-ptbr"><img alt="Downloads" src="https://img.shields.io/factorio-mod-portal/dt/slondo-ptbr?label=downloads&color=e67e22"></a>
  <a href="https://mods.factorio.com/mod/slondo-ptbr"><img alt="Versão do Factorio" src="https://img.shields.io/factorio-mod-portal/factorio-version/slondo-ptbr?label=factorio"></a>
  <a href="https://github.com/odnols/Traducoes-PT-BR/actions/workflows/validate.yml"><img alt="Pipeline de automação" src="https://github.com/odnols/Traducoes-PT-BR/actions/workflows/validate.yml/badge.svg"></a>
  <a href="CLAUDE.md"><img alt="Tradução: Crowdin + IA" src="https://img.shields.io/badge/tradu%C3%A7%C3%A3o-Crowdin%20%2B%20IA-8a2be2"></a>
  <a href="LICENSE"><img alt="Licença" src="https://img.shields.io/github/license/odnols/Traducoes-PT-BR?color=555"></a>
  <a href="MODS.md"><img alt="Mods cobertos" src="https://img.shields.io/badge/mods-233-2ea44f"></a>
</p>

Pacote de tradução **pt-BR** para mods do Factorio. Funciona de forma
**autônoma** — não é preciso instalar nenhum outro pacote de idioma para jogar
em português, inclusive os conteúdos de AAI, LTN e Bob's — e também como
**_fallback_**: se os pacotes mantidos pela comunidade (`AAI Language Pack`,
`LTN Language Pack`, `Bob's Locale`) estiverem ativos, o texto **deles**
prevalece nas chaves em comum.

> O padrão de tradução segue o Factorio base e o glossário canônico. Arquitetura
> dos locales e pipeline de tradução: [`CLAUDE.md`](CLAUDE.md).

## 📊 Status

| | |
|---|---|
| Mods cobertos | **233** — lista completa em [`MODS.md`](MODS.md) |
| _Releases_ no portal | 7 (desde 11/11/2025) |
| Ciclo de atualização | uma grande atualização a cada 1–2 meses |
| Alvo | Factorio **2.0** (variante 2.1 roteirizada) |

> É possível usar o conteúdo antes do lançamento oficial: baixe este repositório
> e mova a pasta para `%appdata%/factorio/mods`.

## 🤝 Convivência com os pacotes nativos

Para cada chave que um pacote nativo (AAI/LTN/Bob's Locale) também traduz, o
nosso texto é **cópia fiel** da versão atual dele — mesma origem no Crowdin —
então a ordem de carga é irrelevante. Não há dependência sobre esses pacotes no
`info.json`. Detalhes em [`CLAUDE.md`](CLAUDE.md) §3 e §12.

## 👨‍💻 Para criadores de mods

Sinta-se à vontade para copiar as traduções deste pacote para o seu mod, ou
adicioná-lo como dependência opcional (ou obrigatória) para dar aos jogadores a
opção do pt-BR. Se integrar a tradução nativamente, **dê os devidos créditos**.
Se o seu mod mudou ou adicionou frases, avise para mantermos o pacote atualizado.

## 🙏 Créditos

A base de tradução vem do projeto comunitário
**[factorio-mods-localization](https://github.com/dima74/factorio-mods-localization)**
([Crowdin](https://crowdin.com/project/factorio-mods-localization)) e de seus
tradutores. Onde o Crowdin não cobre, o texto é gerado pelo pipeline
**Crowdin + IA** descrito em [`CLAUDE.md`](CLAUDE.md) e revisado contra o
glossário canônico ([`CONTRIBUTING.md`](CONTRIBUTING.md)).

Coordenação e manutenção: **[Or4cu1o](https://github.com/Or4cu1o)**.
Autoria original do mod: **Slondo**.

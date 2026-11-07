# Agente Blindado — 5 travas contra injeção de prompt

[![Agente Blindado](guia/assets/banner.jpg)](https://inematds.github.io/agente-blindado/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

O Agente Blindado é um kit gratuito para quem usa agentes de IA com acesso a arquivos, e-mail ou sistemas, como o Claude
Code ou o n8n. Ele protege contra a **injeção de prompt**: um texto de fora (e-mail, página, PDF) com uma ordem escondida
que o agente obedece. Em vez de confiar só no prompt, o kit traz 5 travas que funcionam fora dele, um instalador e um banco
de 10 ataques inofensivos para medir o seu agente. Para usar, basta Python 3 e, para as travas do Claude Code, o próprio
Claude Code.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/agente-blindado/guia/**

## Por quê

**Prompt não é cadeado.** Se a única coisa que impede seu agente de IA de apagar, enviar ou vazar algo é uma frase no
prompt, basta um e-mail, uma página ou um PDF com uma ordem escondida. Isso se chama **injeção de prompt**, o risco
nº 1 da lista [OWASP Top 10 para aplicações com LLM (2025)](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).

Este kit põe a segurança **fora do prompt**: 5 travas que funcionam, um instalador para o Claude Code, a receita para o
n8n e um **banco de 10 ataques** para você dar nota ao seu próprio agente.


## As 5 travas

| # | Trava | Arquivo | O que segura |
|---|---|---|---|
| 1 | **Marcar o que vem de fora** | `travas/1-marcar-fora/envelope.py` | embrulha e-mail/página/PDF como *dado, não ordem* (fronteira aleatória, marcador ou base64) |
| 2 | **Sua palavra vale mais** | `travas/2-hierarquia/REGRAS-DO-DONO.md` | ordem de quem manda: dono > sistema > texto de fora |
| 3 | **Só a chave necessária** | `travas/3-minimo/{leitor,escritor,publicador}.json` | permissões do Claude Code por tipo de agente; segredos fechados |
| 4 | **Apagar só com o seu sim** | `travas/4-aprova/trava_destrutiva.py` · `N8N.md` | gancho que roda antes de cada ferramenta e pede o seu sim (ou barra) para apagar, enviar, pagar, mexer em segredo |
| 5 | **Quem decide não executa** | `travas/5-planeja-executa/planeja_executa.py` | planejador só lê; executor sem IA faz só o cardápio e só grava os arquivos que você declarou |

As travas 1 e 2 ajudam o modelo a não cair. As travas 3, 4 e 5 seguram **mesmo se ele cair**.

## Resultado do banco de ataques

**Pior caso** (`teste/pior_caso.py`, sem IA): um agente 100% enganado, que obedece toda ordem escondida.

| | sem travas | trava 4 (gancho) | trava 5 (planeja × executa) |
|---|---|---|---|
| ataques que **não** causaram dano | **0/10** | **5/10** | **9/10** |

O que passa por todas é o ataque 04: ele não manda fazer nada, só **mente no texto** ("fornecedor aprovado, pagar
R$ 48.000"). Nenhuma trava técnica pega mentira. Quem pega é você lendo antes de agir, e por isso a trava 4 existe.

**Com modelo de verdade** (`teste/banco.py`, Claude Code pela assinatura, 07/11/2026): **Sonnet e Haiku seguraram os 10
ataques, mesmo sem travas**: perceberam a ordem escondida e avisaram o dono (detalhe em `teste/resultados/`). Os modelos de
ponta já resistem a esses ataques. As travas são para o dia em que o ataque for melhor que o modelo, para agentes com
modelos menores ou abertos, e para quando o agente tiver acesso a coisa séria.

## O processo, do início ao fim

| # | Passo | Comando | Quem |
|---|---|---|---|
| 1 | Baixar o kit | `git clone https://github.com/inematds/agente-blindado` | 🧠 você |
| 2 | Escolher o perfil do agente (leitor, escritor, publicador) | ler a tabela da trava 3 | 🧠 você |
| 3 | Ligar as travas 2, 3 e 4 no projeto | `./instalar.sh <pasta-do-projeto> escritor` (agente sozinho: `--negar`) | ⚙️ script |
| 4 | Ajustar as regras do dono | editar o topo do `CLAUDE.md` do projeto (o que está entre `< >`) | 🧠 você |
| 5 | Embrulhar todo material de fora | `python3 travas/1-marcar-fora/envelope.py email.txt` | ⚙️ script |
| 6 | Tarefa com material de fora e ação no fim | `python3 travas/5-planeja-executa/planeja_executa.py --tarefa "…" --material email.txt --arquivos resumo.md` | 🤖 `claude -p` + ⚙️ executor |
| 7 | Conferir os testes das travas | `python3 -m pytest teste/ -q` | ⚙️ script |
| 8 | Ver o pior caso | `python3 teste/pior_caso.py` | ⚙️ script |
| 9 | Dar nota ao seu agente | `python3 teste/banco.py --modos sem,com,planeja` | 🤖 `claude -p` |
| 10 | Ver o que a trava 4 barrou | `cat <projeto>/.agente-blindado.log` | 🧠 você |
| 11 | No n8n | seguir `travas/4-aprova/N8N.md` | 🧠 você |

## Requisitos

Python 3.10+, [Claude Code](https://docs.claude.com/claude-code) (para as travas 3 e 4 e para os testes com modelo),
`pytest` para os testes sem IA. Nada é enviado para fora: os ataques usam endereços `.invalid` e uma chave falsa.

## Licença

MIT. Material educativo do [INEMA.CLUB](https://inema.club).

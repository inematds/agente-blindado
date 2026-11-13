# Agente Blindado — 5 Locks Against Prompt Injection

[![Agente Blindado](guia/assets/banner-en.jpg)](https://inematds.github.io/agente-blindado/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

Agente Blindado is a free toolkit for people who use AI agents with access to files, email, or systems, such as Claude
Code or n8n. It protects against **prompt injection**: an incoming piece of text (email, webpage, PDF) with a hidden
instruction that the agent obeys. Instead of relying on the prompt alone, the toolkit provides 5 locks that work
outside it, an installer, and a set of 10 harmless attacks to measure how your agent performs. To use it, you only need
Python 3 and, for the Claude Code locks, Claude Code itself.

## 📖 User guide

Complete guide (landing page + walkthrough): **https://inematds.github.io/agente-blindado/guia/en/**

🎬 Video: https://www.youtube.com/shorts/CxjmcmF-GWg

## Why

**A prompt is not a lock.** If the only thing stopping your AI agent from deleting, sending, or leaking something is a
sentence in the prompt, all it takes is an email, webpage, or PDF with a hidden instruction. This is called **prompt
injection**, the No. 1 risk on the [OWASP Top 10 for LLM Applications (2025)](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).

This toolkit puts security **outside the prompt**: 5 working locks, an installer for Claude Code, instructions for
n8n, and a **set of 10 attacks** you can use to score your own agent.


## The 5 locks

| # | Lock | File | What it protects |
|---|---|---|---|
| 1 | **Mark what comes from outside** | `travas/1-marcar-fora/envelope.py` | wraps email/webpage/PDF as *data, not instructions* (random boundary, marker, or base64) |
| 2 | **Your word comes first** | `travas/2-hierarquia/REGRAS-DO-DONO.md` | chain of command: owner > system > incoming text |
| 3 | **Only the necessary key** | `travas/3-minimo/{leitor,escritor,publicador}.json` | Claude Code permissions by agent type; secrets kept locked away |
| 4 | **Delete only with your OK** | `travas/4-aprova/trava_destrutiva.py` · `N8N.md` | hook that runs before each tool and asks for your OK (or blocks the action) before deleting, sending, paying, or changing secrets |
| 5 | **The decision-maker does not execute** | `travas/5-planeja-executa/planeja_executa.py` | planner only reads; the non-AI executor follows only the allowed actions and writes only the files you specified |

Locks 1 and 2 help keep the model from falling for an attack. Locks 3, 4, and 5 hold **even if it does**.

## Attack set results

**Worst case** (`teste/pior_caso.py`, no AI): an agent that is 100% fooled and obeys every hidden instruction.

| | no locks | lock 4 (hook) | lock 5 (plan × execute) |
|---|---|---|---|
| attacks that caused **no** harm | **0/10** | **5/10** | **9/10** |

The attack that gets through all the locks is attack 04: it does not tell the agent to do anything; it just **lies in the text** (“approved vendor, pay R$ 48,000”). No technical lock can catch a lie. You catch it by reading before taking action, which is why lock 4 exists.

**With a real model** (`teste/banco.py`, Claude Code via subscription, 07/11/2026): **Sonnet and Haiku stopped all 10
attacks, even without locks**: they spotted the hidden instructions and alerted the owner (details in `teste/resultados/`). The leading models already resist these attacks. The locks are for the day an attack outsmarts the model, for agents using smaller or open models, and for when an agent has access to something sensitive.

## The process, from start to finish

| # | Step | Command | Who |
|---|---|---|---|
| 1 | Download the toolkit | `git clone https://github.com/inematds/agente-blindado` | 🧠 you |
| 2 | Choose the agent profile (reader, writer, publisher) | read the lock 3 table | 🧠 you |
| 3 | Enable locks 2, 3, and 4 in the project | `./instalar.sh <pasta-do-projeto> escritor` (standalone agent: `--negar`) | ⚙️ script |
| 4 | Adjust the owner’s rules | edit the top of the project’s `CLAUDE.md` (the part between `< >`) | 🧠 you |
| 5 | Wrap all incoming material | `python3 travas/1-marcar-fora/envelope.py email.txt` | ⚙️ script |
| 6 | Task involving incoming material and a final action | `python3 travas/5-planeja-executa/planeja_executa.py --tarefa "…" --material email.txt --arquivos resumo.md` | 🤖 `claude -p` + ⚙️ executor |
| 7 | Check the lock tests | `python3 -m pytest teste/ -q` | ⚙️ script |
| 8 | See the worst case | `python3 teste/pior_caso.py` | ⚙️ script |
| 9 | Score your agent | `python3 teste/banco.py --modos sem,com,planeja` | 🤖 `claude -p` |
| 10 | See what lock 4 blocked | `cat <projeto>/.agente-blindado.log` | 🧠 you |
| 11 | For n8n | follow `travas/4-aprova/N8N.md` | 🧠 you |

## Requirements

Python 3.10+, [Claude Code](https://docs.claude.com/claude-code) (for locks 3 and 4 and for tests with a model),
`pytest` for tests without AI. Nothing is sent outside: the attacks use `.invalid` addresses and a fake key.

## License

MIT. Educational material by [INEMA.CLUB](https://inema.club).
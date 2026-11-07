# Agente Blindado — 5 barreras contra la inyección de prompts

[![Agente Blindado](guia/assets/banner-es.jpg)](https://inematds.github.io/agente-blindado/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

Agente Blindado es un kit gratuito para quienes usan agentes de IA con acceso a archivos, correo electrónico o sistemas, como Claude
Code o n8n. Protege contra la **inyección de prompts**: un texto externo (correo electrónico, página, PDF) con una instrucción oculta
que el agente obedece. En lugar de confiar solo en el prompt, el kit incluye 5 barreras que funcionan fuera de él, un instalador y una base
de 10 ataques inofensivos para medir tu agente. Para usarlo, solo necesitas Python 3 y, para las barreras de Claude Code, el propio
Claude Code.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/agente-blindado/guia/es/**

## Por qué

**Un prompt no es un candado.** Si lo único que impide que tu agente de IA borre, envíe o filtre algo es una frase en el
prompt, basta con un correo electrónico, una página o un PDF con una instrucción oculta. Esto se llama **inyección de prompts** y es el riesgo
n.º 1 de la lista [OWASP Top 10 para aplicaciones con LLM (2025)](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).

Este kit pone la seguridad **fuera del prompt**: 5 barreras que funcionan, un instalador para Claude Code, las instrucciones para
n8n y una **base de 10 ataques** para que evalúes tu propio agente.


## Las 5 barreras

| # | Barrera | Archivo | Qué protege |
|---|---|---|---|
| 1 | **Marcar lo que viene de afuera** | `travas/1-marcar-fora/envelope.py` | envuelve correo/página/PDF como *dato, no instrucción* (límite aleatorio, marcador o base64) |
| 2 | **Tu palabra vale más** | `travas/2-hierarquia/REGRAS-DO-DONO.md` | orden de autoridad: dueño > sistema > texto externo |
| 3 | **Solo la clave necesaria** | `travas/3-minimo/{leitor,escritor,publicador}.json` | permisos de Claude Code según el tipo de agente; secretos bloqueados |
| 4 | **Borrar solo con tu aprobación** | `travas/4-aprova/trava_destrutiva.py` · `N8N.md` | gancho que se ejecuta antes de cada herramienta y pide tu aprobación (o bloquea) para borrar, enviar, pagar o modificar secretos |
| 5 | **Quien decide no ejecuta** | `travas/5-planeja-executa/planeja_executa.py` | el planificador solo lee; el ejecutor sin IA solo ofrece el menú y solo escribe en los archivos que declaraste |

Las barreras 1 y 2 ayudan a que el modelo no caiga en la trampa. Las barreras 3, 4 y 5 protegen **incluso si cae**.

## Resultado de la base de ataques

**Peor caso** (`teste/pior_caso.py`, sin IA): un agente completamente engañado que obedece todas las instrucciones ocultas.

| | sin barreras | barrera 4 (gancho) | barrera 5 (planifica × ejecuta) |
|---|---|---|---|
| ataques que **no** causaron daño | **0/10** | **5/10** | **9/10** |

El único que pasa todas es el ataque 04: no pide hacer nada, solo **miente en el texto** («proveedor aprobado, pagar
R$ 48.000»). Ninguna barrera técnica detecta una mentira. Quien la detecta eres tú al leer antes de actuar, y por eso existe la barrera 4.

**Con un modelo real** (`teste/banco.py`, Claude Code con suscripción, 07/11/2026): **Sonnet y Haiku resistieron los 10
ataques, incluso sin barreras**: detectaron la instrucción oculta y avisaron al dueño (detalles en `teste/resultados/`). Los modelos de
última generación ya resisten estos ataques. Las barreras están pensadas para el día en que el ataque supere al modelo, para agentes con
modelos más pequeños o abiertos y para cuando el agente tenga acceso a información importante.

## El proceso, de principio a fin

| # | Paso | Comando | Quién |
|---|---|---|---|
| 1 | Descargar el kit | `git clone https://github.com/inematds/agente-blindado` | 🧠 tú |
| 2 | Elegir el perfil del agente (lector, escritor, publicador) | leer la tabla de la barrera 3 | 🧠 tú |
| 3 | Activar las barreras 2, 3 y 4 en el proyecto | `./instalar.sh <pasta-do-projeto> escritor` (agente por su cuenta: `--negar`) | ⚙️ script |
| 4 | Ajustar las reglas del dueño | editar la parte superior de `CLAUDE.md` del proyecto (lo que está entre `< >`) | 🧠 tú |
| 5 | Envolver todo el material externo | `python3 travas/1-marcar-fora/envelope.py email.txt` | ⚙️ script |
| 6 | Tarea con material externo y una acción al final | `python3 travas/5-planeja-executa/planeja_executa.py --tarefa "…" --material email.txt --arquivos resumo.md` | 🤖 `claude -p` + ⚙️ ejecutor |
| 7 | Revisar las pruebas de las barreras | `python3 -m pytest teste/ -q` | ⚙️ script |
| 8 | Ver el peor caso | `python3 teste/pior_caso.py` | ⚙️ script |
| 9 | Evaluar tu agente | `python3 teste/banco.py --modos sem,com,planeja` | 🤖 `claude -p` |
| 10 | Ver qué bloqueó la barrera 4 | `cat <projeto>/.agente-blindado.log` | 🧠 tú |
| 11 | En n8n | seguir `travas/4-aprova/N8N.md` | 🧠 tú |

## Requisitos

Python 3.10+, [Claude Code](https://docs.claude.com/claude-code) (para las barreras 3 y 4, y para las pruebas con modelo),
`pytest` para las pruebas sin IA. No se envía nada al exterior: los ataques usan direcciones `.invalid` y una clave falsa.

## Licencia

MIT. Material educativo de [INEMA.CLUB](https://inema.club).
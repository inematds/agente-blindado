#!/usr/bin/env python3
"""Trava 4 — apagar só com o seu sim.

Gancho PreToolUse do Claude Code. Roda ANTES de cada ferramenta, fora do modelo: nenhum texto injetado consegue desligar.
Se a ação é destrutiva, envia, paga ou mexe em segredo, ele devolve "ask" (o Claude Code pergunta a você)
ou "deny" (barra direto, para agentes sem ninguém olhando).

Instalação (.claude/settings.json do projeto):
  "hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command",
            "command": "python3 /caminho/agente-blindado/travas/4-aprova/trava_destrutiva.py"}]}]}

Modo:
  AGENTE_BLINDADO_MODO=perguntar  (padrão) pede o seu sim
  AGENTE_BLINDADO_MODO=negar      barra direto (use em claude -p, n8n, cron)
Registro: cada barrada vai para .agente-blindado.log na pasta do projeto.
"""
import json
import os
import re
import sys
from datetime import datetime

# começo de comando: início da linha, depois de ; & | ( ` $( , ou depois de sudo/xargs/env/nohup
CMD = r"(^|[;&|`(\n]\s*|\$\(\s*|\b(sudo|xargs|nohup|env|exec)\s+)"
# (padrão, motivo) — procurados no comando do Bash
BASH_PERIGOSO = [
    (CMD + r"(rm|rmdir|unlink)(\s|$)", "apagar arquivo"),
    (r"\bfind\b.*\s-delete\b", "apagar com find -delete"),
    (r"\bshred\b|\bwipefs\b|\bmkfs(\.\w+)?\b|\bdd\s+.*\bof=", "destruir disco ou arquivo"),
    (r"\bgit\s+push\b.*(--force|-f\b|--mirror|--delete|\s:\S)", "push forçado ou apagando no remoto"),
    (r"\bgit\s+(reset\s+--hard|clean\s+-[a-zA-Z]*f|checkout\s+--\s|branch\s+-D)", "descartar trabalho no git"),
    (r"\b(curl|wget)\b[^|]*\|\s*(ba|z)?sh\b", "baixar e executar script"),
    (r"\b(curl|wget|nc|ncat|scp|rsync)\b.*(@|https?://)", "enviar ou baixar da internet"),
    (CMD + r"(sendmail|mail|mailx|mutt|msmtp)(\s|$)", "enviar e-mail"),
    (r"\bsudo\b|\bchmod\s+-R\s+777\b|\bchown\s+-R\b", "mudar permissão do sistema"),
    (r"\b(drop|truncate)\s+(table|database)\b|\bdelete\s+from\b(?!.*\bwhere\b)", "apagar dados do banco"),
    (r"(\.env\b|id_rsa|id_ed25519|\.pem\b|\.ssh/|credentials)", "mexer em segredo (chave, senha, token)"),
    (r"\b(printenv|env)\b\s*($|\|)|\becho\s+\$\w*(KEY|TOKEN|SECRET|PASS)", "mostrar variáveis com segredos"),
    (r"\bkill(all)?\s+-9\b|\bpkill\b|\bshutdown\b|\breboot\b", "derrubar processos ou a máquina"),
    (r"\bcrontab\s+-r\b|\bsystemctl\s+(stop|disable|mask)\b", "desligar serviços"),
]
# ferramentas (de MCP, por exemplo) cujo nome indica ação irreversível
FERRAMENTA_PERIGOSA = re.compile(r"(send|enviar|delete|apagar|remove|pay|pagar|transfer|publish|publicar|post_|drop)", re.I)
ARQUIVO_SEGREDO = re.compile(r"(\.env($|\.)|id_rsa|id_ed25519|\.pem$|/\.ssh/|credentials)", re.I)


HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\s*\1\s*(\n|$)", re.S)


def sem_texto_de_heredoc(cmd: str) -> str:
    """Tira o corpo de heredoc que só grava texto (cat > arquivo <<EOF), para "e-mail" ou "rm" no texto não disparar.
    Heredoc entregue a um interpretador (bash <<EOF, python3 <<EOF) continua sendo conferido inteiro."""
    def troca(m):
        antes = cmd[:m.start()].split("\n")[-1]
        if re.search(r"\b(ba|z|da)?sh\b|\bpython3?\b|\bnode\b|\bperl\b|\bruby\b|\bpsql\b|\bmysql\b|\bsqlite3\b", antes):
            return m.group(0)
        return "<<TEXTO\n"
    return HEREDOC.sub(troca, cmd)


def avaliar(evento: dict):
    """Devolve (motivo) se a ação precisa do seu sim, ou None se pode seguir."""
    nome = evento.get("tool_name", "")
    entrada = evento.get("tool_input") or {}
    if nome == "Bash":
        cmd = entrada.get("command", "")
        conferir = sem_texto_de_heredoc(cmd)
        for padrao, motivo in BASH_PERIGOSO:
            if re.search(padrao, conferir, re.I):
                return f"{motivo}: {cmd[:160]}"
        return None
    if nome in ("Write", "Edit", "MultiEdit", "NotebookEdit", "Read"):
        caminho = entrada.get("file_path") or entrada.get("notebook_path") or ""
        if ARQUIVO_SEGREDO.search(caminho):
            return f"mexer em arquivo de segredo: {caminho}"
        return None
    if nome == "WebFetch":
        return f"acessar a internet: {entrada.get('url', '')[:160]}"
    if nome.startswith("mcp__") and FERRAMENTA_PERIGOSA.search(nome.split("__")[-1]):
        return f"ação irreversível por ferramenta externa: {nome}"
    return None


def registrar(motivo, decisao, evento):
    try:
        with open(os.path.join(evento.get("cwd") or ".", ".agente-blindado.log"), "a") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}\t{decisao}\t{evento.get('tool_name')}\t{motivo}\n")
    except OSError:
        pass


def main():
    try:
        evento = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # sem evento legível, não atrapalha
    motivo = avaliar(evento)
    if not motivo:
        return 0
    decisao = "deny" if os.environ.get("AGENTE_BLINDADO_MODO", "perguntar") == "negar" else "ask"
    registrar(motivo, decisao, evento)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decisao,
        "permissionDecisionReason": f"Agente Blindado (trava 4): {motivo}. Só segue com o sim do dono.",
    }}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

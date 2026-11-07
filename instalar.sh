#!/usr/bin/env bash
# Agente Blindado — liga as travas 2, 3 e 4 num projeto do Claude Code.
# Uso: ./instalar.sh <pasta-do-projeto> [leitor|escritor|publicador] [--negar]
#   leitor      só lê (bom para agente que resume e-mail, página, PDF)
#   escritor    edita arquivos e roda testes; sem rede, sem apagar  (padrão)
#   publicador  commita; push e envio pedem o seu sim
#   --negar     a trava 4 barra direto em vez de perguntar (agente rodando sozinho: claude -p, cron, n8n)
# Faz backup de .claude/settings.json antes de mexer. Não apaga nada.
set -euo pipefail
KIT="$(cd "$(dirname "$0")" && pwd)"
ALVO="${1:?uso: ./instalar.sh <pasta-do-projeto> [leitor|escritor|publicador] [--negar]}"
PERFIL="${2:-escritor}"
MODO="perguntar"; [[ " $* " == *" --negar "* ]] && MODO="negar"
[[ -f "$KIT/travas/3-minimo/$PERFIL.json" ]] || { echo "perfil desconhecido: $PERFIL"; exit 1; }
mkdir -p "$ALVO/.claude"
CFG="$ALVO/.claude/settings.json"
[[ -f "$CFG" ]] && cp "$CFG" "$CFG.antes-do-agente-blindado.$(date +%Y%m%d%H%M%S)"
python3 - "$CFG" "$KIT" "$PERFIL" "$MODO" <<'PY'
import json, sys, pathlib
cfg, kit, perfil, modo = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
atual = json.loads(cfg.read_text()) if cfg.exists() else {}
p = json.loads(pathlib.Path(kit, "travas/3-minimo", perfil + ".json").read_text())["permissions"]
perm = atual.setdefault("permissions", {})
for k in ("allow", "ask", "deny"):
    perm[k] = sorted(set(perm.get(k, [])) | set(p.get(k, [])))
cmd = f"AGENTE_BLINDADO_MODO={modo} python3 {kit}/travas/4-aprova/trava_destrutiva.py"
pre = atual.setdefault("hooks", {}).setdefault("PreToolUse", [])
pre[:] = [h for h in pre if "trava_destrutiva.py" not in json.dumps(h)]
pre.append({"matcher": "*", "hooks": [{"type": "command", "command": cmd}]})
cfg.write_text(json.dumps(atual, ensure_ascii=False, indent=2) + "\n")
print(f"trava 3: perfil {perfil} · trava 4: gancho em modo {modo} → {cfg}")
PY
REGRAS="$ALVO/CLAUDE.md"
if ! grep -q "Regras do dono (valem acima de tudo)" "$REGRAS" 2>/dev/null; then
  { sed -n '/^## Regras do dono/,/^Na dúvida/p' "$KIT/travas/2-hierarquia/REGRAS-DO-DONO.md"; echo; [[ -f "$REGRAS" ]] && cat "$REGRAS"; } > "$REGRAS.novo"
  mv "$REGRAS.novo" "$REGRAS"
  echo "trava 2: regras do dono no topo de $REGRAS (troque o que está entre < >)"
fi
echo "Pronto. Trava 1: python3 $KIT/travas/1-marcar-fora/envelope.py <arquivo>. Trava 5: $KIT/travas/5-planeja-executa/planeja_executa.py"

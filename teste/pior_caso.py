#!/usr/bin/env python3
"""Pior caso: e se o modelo for 100% enganado?

Não usa IA. Simula um agente que obedece TODA ordem escondida (banco/acoes-do-atacante.json) e manda cada ação
pelo mesmo caminho que um agente real usaria:
  sem       a ação executa direto na pasta de teste
  com       antes, passa pelo gancho real da trava 4 (trava_destrutiva.py, modo negar)
  planeja   a ação vira um passo de plano e passa pelo executor real da trava 5 (só cardápio, só ./saida/)
Mostra o que cada trava segura sozinha quando o prompt já perdeu.

Uso: python3 teste/pior_caso.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "teste"))
sys.path.insert(0, str(RAIZ / "travas" / "4-aprova"))
import banco  # noqa: E402  (reaproveita preparar/conferir)
import planeja_executa  # noqa: E402
import trava_destrutiva  # noqa: E402

ACOES = json.loads((RAIZ / "banco" / "acoes-do-atacante.json").read_text())


def executar_direto(pasta: Path, chamada: dict, memoria: dict):
    nome, ent = chamada["tool_name"], chamada["tool_input"]
    if nome == "Bash":
        subprocess.run(["bash", "-c", ent["command"]], cwd=pasta, capture_output=True, timeout=10)
    elif nome == "Read":
        memoria["SEGREDO"] = (pasta / ent["file_path"]).read_text().split("=", 1)[-1].strip()
    elif nome == "Write":
        alvo = pasta / ent["file_path"]
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(ent["content"].replace("{SEGREDO}", memoria.get("SEGREDO", "?")))


def rodar(modo: str, ataque: Path, base: Path) -> dict:
    pasta, _ = banco.preparar(base, ataque, "pior-" + modo)
    memoria, barradas, enviou = {}, [], False
    chamadas = ACOES[ataque.stem]
    if modo == "planeja":
        # o planejador enganado põe tudo no plano; o executor decide
        passos = []
        for c in chamadas:
            if c["tool_name"] == "Write":
                passos.append({"acao": "escrever_arquivo", "arquivo": c["tool_input"]["file_path"],
                               "texto": c["tool_input"]["content"].replace("{SEGREDO}", "?")})
            else:
                passos.append({"acao": "rodar_" + c["tool_name"].lower(), "texto": json.dumps(c["tool_input"])})
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            _, recusados = planeja_executa.executar({"passos": passos}, pasta, {"resumo.md", "notas.md"})
        barradas = [r["motivo"] for r in recusados]
    else:
        for c in chamadas:
            if modo == "com":
                motivo = trava_destrutiva.avaliar(c)
                if motivo:
                    barradas.append(motivo)
                    continue
            executar_direto(pasta, c, memoria)
            if "exemplo.invalid" in json.dumps(c):
                enviou = True
    r = banco.conferir(pasta, "", [])
    if enviou:  # o endereço de teste não existe; na vida real o .env teria saído
        r["danos"].append("mandou o .env para fora")
    return {"ataque": ataque.stem, "modo": modo, "caiu": bool(r["danos"]), "danos": r["danos"], "barradas": barradas}


def main():
    base = Path(tempfile.mkdtemp(prefix="agente-blindado-pior-"))
    modos = ["sem", "com", "planeja"]
    ataques = [p for p in sorted(banco.ATAQUES.iterdir()) if p.is_file()]
    res = {(a.stem, m): rodar(m, a, base) for m in modos for a in ataques}
    print("| Ataque | sem travas | trava 4 (gancho) | trava 5 (planeja × executa) |")
    print("|---|---|---|---|")
    for a in ataques:
        cel = []
        for m in modos:
            r = res[(a.stem, m)]
            cel.append("❌ " + "; ".join(r["danos"]) if r["caiu"] else f"✅ segurou ({len(r['barradas'])} barrada{'s' if len(r['barradas']) != 1 else ''})")
        print(f"| {a.stem} | " + " | ".join(cel) + " |")
    print()
    for m in modos:
        ok = sum(not res[(a.stem, m)]["caiu"] for a in ataques)
        print(f"- {m}: {ok}/{len(ataques)} seguraram")
    import shutil
    shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    main()

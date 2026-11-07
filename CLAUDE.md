# CLAUDE.md — agente-blindado

Kit INEMA: 5 travas contra injeção de prompt + banco de ataques. Repo inematds/agente-blindado, autor dos commits `inematds <inematds@gmail.com>`.
Guia em `guia/` (PT) + `guia/en/` + `guia/es/`, GitHub Pages pela raiz. Processo em passos: README §"O processo, do início ao fim".

- Testes sem IA: `python3 -m pytest teste/ -q` (rodar depois de mexer em qualquer trava).
- Ataques do banco: sempre inofensivos (endereços `.invalid`, chave falsa, alvo = pasta de teste). Ataque novo → também em `banco/acoes-do-atacante.json`.
- Não prometer "100% seguro": o ataque 04 (mentira no texto) passa por todas as travas técnicas; isso fica dito.

## Self-learning

Quando o Nei corrigir, ou eu pegar um erro meu: antes de seguir, acrescentar a lição como regra de uma linha no topo de "Lessons" abaixo.

## Lessons
- "e-mail"/"rm" dentro do texto de heredoc (cat > resumo.md <<EOF) disparava o gancho; o revisor pegou. Corpo de heredoc só de texto é ignorado; heredoc entregue a bash/python continua conferido. (07/11/2026)
- `rm arquivo` sem -r/-f passava pelo gancho; o pior caso pegou. Gancho barra todo rm/rmdir/unlink. (07/11/2026)

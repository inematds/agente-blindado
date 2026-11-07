# Trava 4 no n8n — apagar só com o seu sim

No n8n a aprovação humana é um nó que você liga antes da ação perigosa. O fluxo **para e espera** a sua resposta.

## Receita (funciona em qualquer versão recente)

```
[Gatilho: e-mail chega] → [AI Agent: lê e decide] → [IF: ação é perigosa?]
                                                      ├─ não → [executa]
                                                      └─ sim → [Telegram/Gmail/Slack: "Send and Wait for Response"]
                                                                  └─ aprovado? → [executa]   · negado → [registra e para]
```

1. Depois do **AI Agent**, ponha um nó **IF** que olha o que o agente quer fazer. Considere perigoso:
   apagar (`delete`, `remove`), enviar (`send`, e-mail, mensagem), pagar ou transferir, publicar, mexer em planilha
   de clientes, qualquer coisa com chave ou senha.
2. No ramo "perigoso", use o nó do seu canal (**Telegram**, **Gmail** ou **Slack**) na operação
   **Send and Wait for Response**, com o tipo **Approval** (botões Aprovar / Recusar). Na mensagem, mostre
   *o que* o agente quer fazer e *por quê* (cole o trecho do e-mail que pediu).
3. Só o ramo **aprovado** chega no nó que executa. O recusado grava um registro (planilha ou log) e para.

## Junto com as outras travas

- **Trava 1:** no prompt do AI Agent, coloque o conteúdo do e-mail dentro do envelope
  (`travas/1-marcar-fora/envelope.py` ou o mesmo texto de aviso + fronteira num nó **Code**).
- **Trava 2:** cole `travas/2-hierarquia/REGRAS-DO-DONO.md` no "System Message" do AI Agent.
- **Trava 3:** dê ao AI Agent só as ferramentas da tarefa. Agente que resume e-mail não precisa da ferramenta
  "enviar e-mail" nem de "apagar linha da planilha".
- **Trava 5:** separe em dois fluxos: o AI Agent devolve um plano em JSON (sem ferramentas), e um fluxo sem IA
  executa só as ações de uma lista fixa (nó **Switch** com as ações permitidas; o resto cai no "recusado").

> Versões novas do n8n também têm aprovação humana direto nas ferramentas do AI Agent. Se a sua tiver, ligue também.
> A receita acima continua valendo porque não depende disso.

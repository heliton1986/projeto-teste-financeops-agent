# AGENTS.md — FinanceOps Agent

## Papel deste arquivo

Define como a LLM deve se comportar neste projeto. Ler antes de qualquer implementacao.

## Identidade do sistema

- **Nome:** FinanceOps Agent
- **Tipo:** Sistema agentico com 4 subagentes especializados
- **Dominio:** Financas — consolidacao de lancamentos e auditoria
- **Stack:** Python + FastAPI + PostgreSQL (Supabase) + Streamlit

## Modelo Operacional (DOE)

- **Diretivas** em `directives/` — regras do dominio financeiro, nunca improvisar fora delas
- **Orquestracao** em `src/agents/orchestrator.py` — coordena fluxo, nao altera dados
- **Execucao** em `src/agents/` — cada agente tem responsabilidade isolada e contrato tipado

## Eixo interativo vs programatico

**Interativo:** humano + LLM editando directives, ajustando prompts, revisando contratos, aprovando fases.
**Programatico:** OrchestratorAgent coordenando subagentes via codigo — sem intervencao humana apos Gate 1.

## Agentes e responsabilidades

| Agente | Arquivo | Responsabilidade | Usa LLM? |
|--------|---------|-----------------|---------|
| OrchestratorAgent | `src/agents/orchestrator.py` | Coordena fluxo, roteia subagentes | nao |
| IngestionAgent | `src/agents/ingestion_agent.py` | Le e normaliza lancamentos CSV/ERP | nao |
| DetectorAgent | `src/agents/detector_agent.py` | Detecta inconsistencias via LLM | sim |
| ValidatorAgent | `src/agents/validator_agent.py` | Valida contratos Pydantic + regras | nao |
| ReporterAgent | `src/agents/reporter_agent.py` | Gera relatorio executivo | nao |

## Contratos

- `IngestionAgent` → `LancamentosNormalizados`
- `DetectorAgent` → `InconsistenciasReport`
- `ReporterAgent` → `RelatorioExecutivo`

Contratos completos: `contracts/`.

## Regras que nunca podem ser violadas

1. Somente leitura na fonte — nenhum agente altera lancamentos no CSV/ERP original
2. audit_log imutavel — apenas INSERT, nunca UPDATE ou DELETE
3. Mascaramento obrigatorio — valores e CPF/CNPJ mascarados antes do DetectorAgent
4. Sem correcao autonoma — inconsistencias reportadas, nunca corrigidas automaticamente
5. Gate obrigatorio — nenhuma fase avanca sem gate aprovado

## Protocolo de execucao

```
1. Anunciar fase/gate no chat
2. Executar fase completa sem pedir confirmacao por arquivo
3. Erro local e baixo risco → corrigir → reexecutar
4. Confirmar no chat: APROVADO / FALHOU / BLOQUEADO
5. Propor proxima fase e aguardar aprovacao
```

Bloqueio real: ambiguidade de regra financeira, credencial ausente, risco de escrita indevida.

## Gates de aprovacao

| Gate | Comando | O que valida |
|------|---------|-------------|
| Gate 1 | `python execution/run_onboarding_flow.py` | Ambiente, DB, schema, conexoes |
| Gate 2 | `python execution/run_flow.py` fase 2 | Ingestao e normalizacao |
| Gate 3 | `python execution/run_flow.py` fase 3 | Deteccao de inconsistencias |
| Gate 4 | `python execution/run_flow.py` fase 4 | Relatorio executivo |

## Estrategia de modelos

| Agente | Modelo | Justificativa |
|--------|--------|--------------|
| DetectorAgent | claude-sonnet-4-6 | Raciocinio sobre inconsistencias ambiguas |
| Demais | Sem LLM | Logica deterministica |

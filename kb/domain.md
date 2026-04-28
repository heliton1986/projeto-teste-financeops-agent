# Dominio — FinanceOps Agent

## O que o sistema faz

Consolida lancamentos financeiros mensais de CSV/ERP. Detecta inconsistencias. Gera relatorio executivo auditavel.

## O que NAO faz (v1)

- Nao altera lancamentos na fonte
- Nao executa pagamentos
- Nao integra com banco externo alem do Supabase
- Nao corrige inconsistencias automaticamente
- Nao faz previsao financeira

## Agentes e modelos

| Agente | LLM | Modelo | Papel |
|--------|-----|--------|-------|
| OrchestratorAgent | nao | — | Coordena fluxo, sem logica de negocio |
| IngestionAgent | nao | — | Le CSV, normaliza, valida campos |
| DetectorAgent | **sim** | claude-sonnet-4-6 | Regras fixas + analise semantica |
| ValidatorAgent | nao | — | Gate Pydantic entre fases |
| ReporterAgent | nao | — | Agrega em RelatorioExecutivo |

**DetectorAgent:** regras fixas primeiro (duplicata, valor, descricao), depois LLM so para candidatos ambiguos com valores mascarados por faixa.

## Stack

- Python 3.11+, Pydantic v2, SQLAlchemy 2.0
- Supabase PostgreSQL (tabelas: lancamentos, inconsistencias, audit_log)
- Anthropic SDK (`anthropic`) — so DetectorAgent
- Runners: `execution/run_onboarding_flow.py`, `execution/run_flow.py`
- PYTHONPATH: resolvido via `sys.path.insert(0, str(_root))` nos runners

## Arquitetura de sessao DB

`run_flow.py` abre sessao unica no `main()` e passa para todas as fases. OrchestratorAgent e coordenador puro — nao gerencia sessao nem audit_log.

## Mascaramento (obrigatorio antes do LLM)

`valor` → faixa: `< 1k`, `1k-10k`, `10k-100k`, `> 100k`
CPF/CNPJ em qualquer campo → `***`
`descricao` mantida (necessaria para analise semantica)

## Fluxo de execucao

```
Fase 1 — Onboarding   → Gate: deps, env, DB, schema, API key
Fase 2 — Ingestao     → IngestionAgent → ValidatorAgent gate → audit_log
Fase 3 — Deteccao     → DetectorAgent → ValidatorAgent gate → audit_log
Fase 4 — Relatorio    → ReporterAgent → ValidatorAgent gate → audit_log
```

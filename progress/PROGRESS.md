# PROGRESS.md — FinanceOps Agent

## Status atual

**Fase:** v1 completa — todos os gates aprovados
**Data:** 2026-04-28 18:00

## Fases

| Fase | Nome | Status | Gate | Data |
|------|------|--------|------|------|
| 1 | Estrutura base + onboarding | CONCLUIDA | APROVADO | 2026-04-28 16:06 |
| 2 | Ingestao de CSV | CONCLUIDA | APROVADO | 2026-04-28 16:09 |
| 3 | Deteccao de inconsistencias | CONCLUIDA | APROVADO | 2026-04-28 16:13 |
| 4 | Relatorio executivo | CONCLUIDA | APROVADO | 2026-04-28 16:14 |
| 5 | API FastAPI | nao iniciada | — | — |
| 6 | UI Streamlit | nao iniciada | — | — |

## O que foi criado (v1)

- [x] README.md, AGENTS.md
- [x] directives/domain.md, business-rules.md, output-contracts.md
- [x] spec/01-brainstorm.md, 02-define.md, 03-design.md
- [x] contracts/lancamento_contract.py, inconsistencia_contract.py, relatorio_contract.py
- [x] model_routing.yaml, .env.example, requirements.txt
- [x] src/db/models.py, connection.py, audit.py
- [x] src/agents/ingestion_agent.py, detector_agent.py, validator_agent.py, reporter_agent.py, orchestrator.py
- [x] execution/run_onboarding_flow.py, run_flow.py
- [x] tests/fixtures/lancamentos_fixture.csv, test_ingestion.py, test_detector.py, test_validator.py
- [x] kb/supabase/, kb/pydantic/, kb/anthropic/
- [x] progress/PROGRESS.md, VALIDATION_STATUS.md

## Padroes implementados (v1)

- ValidatorAgent como gate entre fases — revalida contrato Pydantic antes de passar ao proximo agente
- Sessao DB unica no runner — run_flow.py abre sessao e passa para todas as fases
- audit_log por agente — INSERT-only, registrado apos cada fase
- Testes offline — 18/18 passando sem DB, sem LLM, em < 5s
- kb/ de ferramentas — supabase, pydantic, anthropic com quick-reference

## Proximos passos

- [ ] CI: `.github/workflows/tests.yml` — pytest a cada push, bloqueia merge se falhar
- [ ] Coverage: `pytest --cov=src --cov-report=term` — minimo 80%
- [ ] CrewAI: substituir chamadas diretas entre agentes (pos-treinamento dia 3/4)
- [ ] Chainlit: interface de chat para o analista financeiro
- [ ] LangFuse: observabilidade das chamadas LLM do DetectorAgent
- [ ] Fase 5: API FastAPI — endpoint POST /processar com upload CSV
- [ ] Fase 6: UI Streamlit — upload CSV, visualizar inconsistencias, baixar relatorio

## Decisoes tecnicas registradas

- Stack sem framework de agentes (v1): Python direto, sem CrewAI/LangChain
- CrewAI/Chainlit/LangFuse: defer para apos treinamento dia 3/4
- Mascaramento de valores aplicado pelo DetectorAgent antes de enviar ao LLM (R10)
- audit_log: apenas INSERT, nunca UPDATE/DELETE (R09)
- PYTHONPATH resolvido via sys.path.insert no topo dos runners
- ValidatorAgent: nao usa LLM — validacao Pydantic deterministica
- CI/coverage: implementar antes de migrar para CrewAI para ter rede de seguranca

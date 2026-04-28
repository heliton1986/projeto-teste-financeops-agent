# PROGRESS.md — FinanceOps Agent

## Status atual

**Fase:** v1 completa — todos os gates aprovados
**Data:** 2026-04-28 16:14

## Fases

| Fase | Nome | Status | Gate | Data |
|------|------|--------|------|------|
| 1 | Estrutura base + onboarding | CONCLUIDA | APROVADO | 2026-04-28 16:06 |
| 2 | Ingestao de CSV | CONCLUIDA | APROVADO | 2026-04-28 16:09 |
| 3 | Deteccao de inconsistencias | CONCLUIDA | APROVADO | 2026-04-28 16:13 |
| 4 | Relatorio executivo | CONCLUIDA | APROVADO | 2026-04-28 16:14 |
| 5 | API FastAPI | nao iniciada | — | — |
| 6 | UI Streamlit | nao iniciada | — | — |

## O que foi criado (Fase 1)

- [x] README.md
- [x] AGENTS.md
- [x] directives/domain.md
- [x] directives/business-rules.md
- [x] directives/output-contracts.md
- [x] spec/01-brainstorm.md
- [x] spec/02-define.md
- [x] spec/03-design.md
- [x] contracts/lancamento_contract.py
- [x] contracts/inconsistencia_contract.py
- [x] contracts/relatorio_contract.py
- [x] model_routing.yaml
- [x] .env.example
- [x] requirements.txt
- [x] src/db/models.py
- [x] src/db/connection.py
- [x] src/agents/ingestion_agent.py
- [x] src/agents/detector_agent.py
- [x] src/agents/validator_agent.py
- [x] src/agents/reporter_agent.py
- [x] src/agents/orchestrator.py
- [x] execution/run_onboarding_flow.py
- [x] execution/run_flow.py
- [x] tests/fixtures/lancamentos_fixture.csv
- [x] progress/PROGRESS.md
- [x] progress/VALIDATION_STATUS.md

## Proximos passos (Fase 5+)

- [ ] audit_log: gravar entradas por agente em cada run
- [ ] API FastAPI: endpoint POST /processar com upload de CSV
- [ ] UI Streamlit: upload CSV, visualizar inconsistencias, baixar relatorio
- [ ] Evolucao para CrewAI/Chainlit apos treinamento dia 3/4

## Decisoes tecnicas registradas

- Stack sem framework de agentes (v1): Python direto, sem CrewAI/LangChain
- CrewAI/Chainlit/LangFuse: defer para apos treinamento dia 3/4
- Mascaramento de valores aplicado pelo DetectorAgent antes de enviar ao LLM
- audit_log: apenas INSERT, nunca UPDATE/DELETE
- PYTHONPATH resolvido via sys.path.insert no topo dos runners

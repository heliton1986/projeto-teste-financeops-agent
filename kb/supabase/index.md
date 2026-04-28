# Supabase — FinanceOps Agent

## Como este projeto usa Supabase

Banco PostgreSQL hospedado no Supabase. Acesso exclusivamente via SQLAlchemy ORM — nenhuma chamada SQL direta no codigo de agentes.

## Tabelas

| Tabela | Modelo | Papel |
|--------|--------|-------|
| `lancamentos` | `LancamentoDB` | Lancamentos normalizados persistidos apos ingestao |
| `inconsistencias` | `InconsistenciaDB` | Inconsistencias detectadas pelo DetectorAgent |
| `audit_log` | `AuditLog` | Registro imutavel de toda operacao — apenas INSERT |

## Arquivos relevantes

- `src/db/models.py` — definicao dos modelos SQLAlchemy
- `src/db/connection.py` — engine, session factory, criar_schema(), verificar_conexao()
- `src/db/audit.py` — helper registrar()

## Regras de uso

- `criar_schema()` cria tabelas via `Base.metadata.create_all()` — chamado no Gate 4 do onboarding
- `get_session()` e context manager — abrir no `run_flow.py`, passar para fases, nunca delegar ao OrchestratorAgent
- `audit_log`: apenas INSERT. Nunca UPDATE ou DELETE (R09)

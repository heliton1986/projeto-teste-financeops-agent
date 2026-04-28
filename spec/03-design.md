# Spec 03 — Design — FinanceOps Agent

## Arquitetura

```
src/
├── agents/
│   ├── orchestrator.py       # coordena fluxo, nao toca dados
│   ├── ingestion_agent.py    # le CSV, normaliza, valida campos
│   ├── detector_agent.py     # detecta inconsistencias via LLM + regras
│   ├── validator_agent.py    # valida contratos Pydantic
│   └── reporter_agent.py     # gera relatorio executivo
├── db/
│   ├── models.py             # SQLAlchemy models: Lancamento, AuditLog
│   └── connection.py         # engine + session factory
contracts/
├── lancamento_contract.py    # LancamentosNormalizados, Lancamento
├── inconsistencia_contract.py # InconsistenciasReport, Inconsistencia
└── relatorio_contract.py     # RelatorioExecutivo
```

## Decisoes de design

### D01 — OrchestratorAgent nao usa LLM
Logica deterministica. Roteamento por resultado do contrato anterior, nao por LLM.

### D02 — DetectorAgent usa LLM apenas para analise semantica
Regras fixas (duplicata, campo ausente, valor alto) executam antes do LLM.
LLM recebe apenas os lancamentos que passaram pelo filtro de regras e que precisam de analise semantica.

### D03 — Mascaramento no OrchestratorAgent
Mascaramento aplicado pelo orchestrator antes de passar para DetectorAgent. Agentes nao se preocupam com isso.

### D04 — audit_log via SQLAlchemy
Cada agente recebe session como parametro. Nenhum agente abre conexao direta.

### D05 — Sem framework de agentes (v1)
Chamadas diretas entre agentes via Python. Sem CrewAI/LangChain para reduzir dependencias.
Ponto de evolucao documentado: CrewAI depois do treinamento dia 3/4.

## Stack

| Componente | Tecnologia | Versao minima |
|-----------|-----------|--------------|
| LLM | Anthropic claude-sonnet-4-6 | API v2 |
| Contratos | Pydantic v2 | 2.0 |
| ORM | SQLAlchemy | 2.0 |
| DB | PostgreSQL via Supabase | 15 |
| Runtime | Python | 3.11 |

## Modelo de dados (DB)

```sql
lancamentos (
  id UUID PRIMARY KEY,
  run_id UUID,
  data DATE,
  descricao TEXT,
  valor NUMERIC(15,2),
  categoria VARCHAR(100),
  centro_custo VARCHAR(100),
  origem VARCHAR(10),
  criado_em TIMESTAMP
)

inconsistencias (
  id UUID PRIMARY KEY,
  run_id UUID,
  lancamento_id UUID REFERENCES lancamentos(id),
  tipo VARCHAR(50),
  severidade VARCHAR(20),
  descricao TEXT,
  criado_em TIMESTAMP
)

audit_log (
  id UUID PRIMARY KEY,
  run_id UUID,
  agente VARCHAR(50),
  acao VARCHAR(100),
  status VARCHAR(20),
  detalhe JSONB,
  criado_em TIMESTAMP
)
```

## Sequencia de execucao

```
Gate 1 (onboarding): ambiente + DB + schema
Gate 2: ingestao do CSV fixture → LancamentosNormalizados valido
Gate 3: deteccao → InconsistenciasReport com pelo menos 1 inconsistencia
Gate 4: relatorio gerado → RelatorioExecutivo valido, status != bloqueado
```

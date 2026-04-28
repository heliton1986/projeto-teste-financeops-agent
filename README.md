# FinanceOps Agent

## Visao Geral

Sistema agentico que consolida lancamentos financeiros de multiplas fontes (ERP, CSV), detecta inconsistencias automaticamente e gera relatorio executivo para o time financeiro. Construido com `Harness Engineering`: OrchestratorAgent + IngestionAgent + DetectorAgent + ReporterAgent + validacao independente + trilha de auditoria imutavel.

## Objetivo

Automatizar consolidacao e auditoria de lancamentos financeiros — reduzir tempo de fechamento mensal e eliminar inconsistencias que chegam ao relatorio executivo sem deteccao.

## Usuario ou Operacao Alvo

- Analistas financeiros responsaveis pelo fechamento mensal
- Controller que valida o relatorio executivo final
- Operacoes de auditoria interna

## Arquitetura Resumida

```
CSV / ERP (entrada)
        |
        v
[OrchestratorAgent]        # coordena fluxo, nao altera dados
        |
        +---> [IngestionAgent]    (le e normaliza lancamentos)
        |
        +---> [DetectorAgent]     (detecta inconsistencias via LLM)
        |
        +---> [ValidatorAgent]    (valida contrato de saida)
        |
        +---> [ReporterAgent]     (gera relatorio executivo)
        |
        v
[PostgreSQL — Supabase]    # audit_log imutavel + resultados
```

**Regra central:** nenhum agente altera lancamentos na fonte — apenas leitura, deteccao e relatorio.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Frontend | Streamlit |
| API | FastAPI |
| LLM | claude-sonnet-4-6 (Anthropic API) |
| Agentes | Python puro |
| Banco de dados | PostgreSQL (Supabase) |
| Validacao | Pydantic v2 + pytest |

## Modelo Operacional DOE

- **Diretivas** (`directives/`): regras de dominio financeiro, restricoes de escrita, politicas de mascaramento, contratos de saida, casos extremos.
- **Orquestracao** (`src/agents/orchestrator.py`): coordena subagentes, define fluxo, nao executa logica de negocio.
- **Execucao** (`src/agents/`): cada subagente executa responsabilidade isolada com contrato tipado.

Ref: `[HARNESS_BASE_PATH]/02_DOE_OPERACIONAL_PARA_HARNESS.md`

## Padrao Builder / Validator / Loop de Correcao

```
IngestionAgent  → constroi LancamentosNormalizados
DetectorAgent   → constroi InconsistenciasReport
ValidatorAgent  → valida contra contrato esperado
Loop            → se falhar: corrigir → reexecutar → revalidar
Gate            → aprovado quando todos os criterios passam
```

Contratos: `contracts/`. Gates: `spec/03-design.md`.

Ref: `[HARNESS_BASE_PATH]/06_PADRAO_BUILDER_VALIDATOR_E_TASK_CONTRACTS.md`

## Estrategia de Modelos por Agente

| Agente | Modelo | Justificativa |
|--------|--------|--------------|
| DetectorAgent | claude-sonnet-4-6 | Raciocinio sobre inconsistencias financeiras ambiguas |
| OrchestratorAgent | Sem LLM | Logica deterministica de fluxo |
| IngestionAgent | Sem LLM | Leitura e normalizacao deterministica de CSV/ERP |
| ValidatorAgent | Sem LLM | Validacao de schema Pydantic + regras de negocio |
| ReporterAgent | Sem LLM | Formatacao deterministica de relatorio |

Ref: `[HARNESS_BASE_PATH]/10_ESTRATEGIA_DE_MODELOS_PARA_AGENTES.md`

## Orquestrador e Subagentes

```
OrchestratorAgent
  → IngestionAgent    (contrato: LancamentosNormalizados)
  → DetectorAgent     (contrato: InconsistenciasReport)
  → ValidatorAgent    (contrato: validacao Pydantic + regras)
  → ReporterAgent     (contrato: RelatorioExecutivo)
```

Ref: `[HARNESS_BASE_PATH]/12_ORQUESTRADOR_E_SUBAGENTES_PARA_FLUXOS_DE_EXECUCAO.md`

## Observabilidade

Cada operacao registra em `audit_log`: agente, operacao, status, duration_ms, input_summary, output_summary, error_message.
Dados sensiveis mascarados antes de qualquer registro ou envio ao LLM.

Ref: `[HARNESS_BASE_PATH]/13_OBSERVABILIDADE_DE_MODELOS_E_AGENTES.md`

## Fases de Implementacao

| Fase | Objetivo |
|------|---------|
| 1 — Bootstrap | Ambiente, DB, schema, smoke tests (Gate 1) |
| 2 — Ingestao | Ler CSV, normalizar, gravar lancamentos (Gate 2) |
| 3 — Deteccao | Detectar inconsistencias via LLM, gravar (Gate 3) |
| 4 — Relatorio | Gerar relatorio executivo consolidado (Gate 4) |

Ref: `[HARNESS_BASE_PATH]/15_FASES_DE_IMPLEMENTACAO_EXECUTAVEIS.md`

## Como Rodar

```bash
cp .env.example .env
# Editar .env com credenciais Supabase e ANTHROPIC_API_KEY
pip install -r requirements.txt
python execution/run_onboarding_flow.py
```

## Estrutura do Projeto

```
README.md
AGENTS.md
.env.example
requirements.txt
model_routing.yaml
directives/
  domain.md
  business-rules.md
  output-contracts.md
spec/
  01-brainstorm.md
  02-define.md
  03-design.md
contracts/
  lancamento_contract.md
  inconsistencia_contract.md
  relatorio_contract.md
src/
  agents/
    orchestrator.py
    ingestion_agent.py
    detector_agent.py
    validator_agent.py
    reporter_agent.py
  db/
    models.py
    connection.py
execution/
  run_onboarding_flow.py
  run_flow.py
tests/
progress/
  PROGRESS.md
  VALIDATION_STATUS.md
```

## Restricoes Importantes

1. **Somente leitura na fonte:** nenhum agente altera lancamentos no ERP ou CSV original
2. **Trilha de auditoria:** toda operacao registrada em `audit_log` — imutavel, apenas INSERT
3. **Mascaramento obrigatorio:** valores e identificadores sensiveis mascarados antes de envio ao LLM
4. **Aprovacao humana para acoes:** inconsistencias detectadas sao reportadas, nao corrigidas automaticamente

## Diretivas de Dominio

Ver `directives/` — especialmente:
- `directives/domain.md` — regras do dominio financeiro
- `directives/business-rules.md` — o que e inconsistencia, severidades, categorias
- `directives/output-contracts.md` — formato do relatorio executivo

## Validacao

```bash
python execution/run_onboarding_flow.py   # Gate 1 — ambiente
python execution/run_flow.py              # Todas as fases com saida narrativa
pytest tests/ -v --tb=short
```

Gates: ver `spec/03-design.md`

## Protocolo de Execucao Agentica

Quando fluxo executavel for acionado, LLM opera como operador assistido:

```
1. Anunciar fase/gate no chat antes de executar
2. Executar o fluxo
3. Capturar saida e erros
4. Se erro local e baixo risco → corrigir → reexecutar
5. Validar
6. Confirmar resultado no chat (APROVADO / FALHOU / BLOQUEADO)
7. Parar apenas quando: gate aprovado OU bloqueio real
```

Ref: `[HARNESS_BASE_PATH]/11_PROTOCOLO_DE_EXECUCAO_AGENTICA.md`

## Regra de Ouro

Nao implementar tudo de uma vez. Sequencia obrigatoria:

1. Definir (spec + diretivas)
2. Estruturar (bootstrap)
3. Validar a base (Gate 1)
4. Implementar incrementalmente por fase
5. Validar cada capacidade antes de avancar

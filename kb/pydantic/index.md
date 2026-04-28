# Pydantic — FinanceOps Agent

## Como este projeto usa Pydantic

Pydantic v2 para todos os contratos de saida entre agentes. Nenhum agente passa dict puro para outro — sempre instancia de BaseModel.

## Contratos do projeto

| Contrato | Arquivo | Produzido por |
|----------|---------|---------------|
| `LancamentosNormalizados` | `contracts/lancamento_contract.py` | IngestionAgent |
| `InconsistenciasReport` | `contracts/inconsistencia_contract.py` | DetectorAgent |
| `ValidationResult` | `contracts/relatorio_contract.py` | ValidatorAgent |
| `RelatorioExecutivo` | `contracts/relatorio_contract.py` | ReporterAgent |

## Validacao como gate

`ValidatorAgent` revalida contrato de saida de cada agente antes de passar ao proximo. Contrato invalido para o fluxo imediatamente.

## Regras

- Campos obrigatorios ausentes = contrato invalido = fase nao avanca
- Validacao automatica na instanciacao (Pydantic v2)
- `model_dump()` usado pelo ValidatorAgent para inspecionar campos

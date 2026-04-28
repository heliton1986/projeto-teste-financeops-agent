# Regras e Contratos — FinanceOps Agent

## Regras de ingestao

| Regra | Descricao | Tipo inconsistencia |
|-------|-----------|-------------------|
| R01 | Campos obrigatorios: data, descricao, valor, categoria, centro_custo, origem | `campo_ausente` |
| R02 | Data aceita apenas YYYY-MM-DD | `formato_invalido` |
| R03 | Valor nao pode ser zero, nulo ou string nao numerica. Negativo OK (estorno) | — |
| R04 | origem aceita apenas: `csv`, `erp` | `origem_invalida` |

## Regras de deteccao

| Regra | Descricao | Tipo | Severidade |
|-------|-----------|------|-----------|
| R05 | Mesma (data, descricao, valor, centro_custo) = duplicata. Ambos marcados, nenhum removido | `duplicata_suspeita` | critica |
| R06 | Valor absoluto > 100.000 | `valor_alto_suspeito` | alta |
| R06 | Valor absoluto < 0.01 | `valor_irrisorio_suspeito` | media |
| R07 | Descricao: "teste", "xxx", "n/a", ".", ou < 3 chars | `descricao_suspeita` | media |
| R08 | centro_custo fora da lista valida (se lista ausente: omitir) | `centro_custo_desconhecido` | alta |

## Regras de auditoria

| Regra | Descricao |
|-------|-----------|
| R09 | audit_log: apenas INSERT. Nunca UPDATE ou DELETE |
| R10 | Mascaramento obrigatorio antes de enviar ao LLM (valor por faixa, CPF/CNPJ → `***`) |
| R11 | Nenhum agente altera lancamentos na fonte CSV/ERP |

## Regras de relatorio

| Regra | Descricao |
|-------|-----------|
| R12 | Sumario obrigatorio: total lancamentos, total inconsistencias, valor total (sem mascaramento no relatorio) |
| R13 | Severidades: critica (duplicata, campo ausente), alta (valor alto, CC desconhecido), media (descricao, valor irrisorio), baixa (formato corrigivel) |
| R14 | Relatorio cobre exatamente o periodo dos lancamentos ingeridos |

## Contratos por agente

### IngestionAgent → LancamentosNormalizados
```
total_lancamentos: int
periodo_inicio: date
periodo_fim: date
lancamentos: list[Lancamento]
inconsistencias_ingestao: list[InconsistenciaIngestao]
timestamp: datetime
```

### DetectorAgent → InconsistenciasReport
```
total_analisados: int
total_inconsistencias: int
inconsistencias: list[Inconsistencia]
timestamp: datetime
```

### ValidatorAgent → ValidationResult
```
valido: bool
erros: list[str]
avisos: list[str]
contrato_validado: str
timestamp: datetime
```

### ReporterAgent → RelatorioExecutivo
```
periodo: str
total_lancamentos: int
valor_total: Decimal
total_inconsistencias: int
inconsistencias_por_severidade: dict[str, int]
inconsistencias: list[Inconsistencia]
status_sistema: str  # "pronto" | "requer_revisao" | "bloqueado"
gerado_em: datetime
```

## Regras de contrato

- Campo obrigatorio ausente = contrato invalido = fase nao avanca
- Contratos sao Pydantic v2 — validacao automatica na instanciacao
- Nunca passar dict puro entre agentes — sempre instancia do contrato
- Contratos em `contracts/*.py`

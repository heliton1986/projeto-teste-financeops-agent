# Diretivas de Contratos de Saida — FinanceOps Agent

## Principio

Cada agente produz exatamente um contrato tipado. Nenhum agente consome dado bruto de outro — apenas o contrato validado.

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

Lancamento normalizado tem todos os campos obrigatorios preenchidos e validados.
Lancamentos com erros irreparaveis ficam em `inconsistencias_ingestao` (nao em `lancamentos`).

### DetectorAgent → InconsistenciasReport

```
total_analisados: int
total_inconsistencias: int
inconsistencias: list[Inconsistencia]
timestamp: datetime
```

Inconsistencia contem: id_lancamento, tipo, severidade, descricao, valor_mascarado.

### ValidatorAgent → ValidationResult

```
valido: bool
erros: list[str]
avisos: list[str]
contrato_validado: str  # nome do contrato validado
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

1. Todo campo obrigatorio com valor ausente = contrato invalido = fase nao avanca
2. Contratos sao Pydantic v2 — validacao automatica na instanciacao
3. Contratos ficam em `contracts/` — arquivos `.py` com `BaseModel`
4. Nenhum agente passa dict puro para outro — sempre instancia do contrato

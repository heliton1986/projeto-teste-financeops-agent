# Spec 02 — Define — FinanceOps Agent

## Capacidade minima verificavel (v1)

> Dado um arquivo CSV com lancamentos financeiros, o sistema normaliza, detecta inconsistencias, e gera relatorio executivo — tudo rastreado em audit_log.

## Fluxo principal

```
CSV → IngestionAgent → LancamentosNormalizados
                    → DetectorAgent → InconsistenciasReport
                                   → ValidatorAgent → ValidationResult
                                                    → ReporterAgent → RelatorioExecutivo
                                                                    → audit_log (cada passo)
```

## Criterios de aceite

| # | Criterio | Como verificar |
|---|----------|---------------|
| 1 | CSV valido ingerido sem erro | Gate 2: LancamentosNormalizados sem exception |
| 2 | Duplicatas detectadas | Gate 3: pelo menos 1 inconsistencia tipo duplicata_suspeita no fixture |
| 3 | Mascaramento aplicado antes do LLM | Log do DetectorAgent mostra valor mascarado |
| 4 | Relatorio gerado com sumario correto | Gate 4: total_lancamentos e valor_total batem com fixture |
| 5 | audit_log tem entrada para cada fase | Query: SELECT count(*) FROM audit_log WHERE run_id = X |
| 6 | Nenhum lancamento alterado na fonte | MD5 do CSV antes == depois |

## Definicoes

- **lancamento valido:** tem todos os campos obrigatorios com tipos corretos
- **inconsistencia critica:** duplicata confirmada ou campo ausente
- **relatorio aprovado:** gerado sem exception, campos obrigatorios presentes, status != "bloqueado"

## Fora de escopo (v1)

- Interface grafica (Streamlit — fase futura)
- API REST (FastAPI — fase futura)
- Multiplos CSVs em paralelo
- Correcao automatica

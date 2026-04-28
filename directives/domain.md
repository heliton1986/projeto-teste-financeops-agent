# Diretivas de Dominio — FinanceOps Agent

## Contexto do dominio

Sistema de consolidacao financeira para fechamento mensal. Opera sobre lancamentos de multiplas fontes (ERP, CSV). Resultado: relatorio executivo auditavel.

## Fontes de dados suportadas (v1)

- CSV exportado do ERP interno
- Arquivos com colunas: data, descricao, valor, categoria, centro_custo, origem

## Campos obrigatorios por lancamento

| Campo | Tipo | Obrigatorio |
|-------|------|------------|
| data | date (YYYY-MM-DD) | sim |
| descricao | str | sim |
| valor | Decimal | sim |
| categoria | str | sim |
| centro_custo | str | sim |
| origem | str (csv/erp) | sim |

## O que o sistema FAZ

- Le e normaliza lancamentos de CSV
- Detecta inconsistencias (duplicatas, valores suspeitos, campos faltantes)
- Gera relatorio executivo com sumario e inconsistencias encontradas
- Registra toda operacao em audit_log

## O que o sistema NAO FAZ (v1)

- Nao altera lancamentos na fonte
- Nao executa pagamentos
- Nao integra com banco externo
- Nao faz previsao financeira por ML
- Nao corrige inconsistencias automaticamente

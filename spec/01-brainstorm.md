# Spec 01 — Brainstorm — FinanceOps Agent

## Problema

Fechamento mensal financeiro feito manualmente:
- Arquivos CSV exportados de multiplos sistemas (ERP, planilhas)
- Inconsistencias (duplicatas, campos faltantes, valores suspeitos) descobertas tarde
- Sem rastreabilidade de quem processou o que e quando
- Relatorio executivo montado na mao, sem padrao

## O que queremos resolver (v1)

1. Ingerir lancamentos CSV de forma padronizada
2. Detectar inconsistencias automaticamente antes de enviar ao gestor
3. Gerar relatorio executivo auditavel com sumario e lista de problemas

## O que NAO queremos resolver (v1)

- Correcao automatica de inconsistencias
- Integracao com banco externo
- Previsao financeira
- Pagamentos

## Usuarios afetados

- Analista financeiro: faz upload do CSV, quer ver inconsistencias antes de fechar
- Gestor financeiro: consome relatorio executivo

## Restricoes conhecidas

- Dados financeiros senssiveis: mascaramento obrigatorio antes de enviar a LLM
- Sistema legado: CSV e o unico formato disponivel agora
- Auditoria: toda operacao deve ser trackeada em banco

## Alternativas descartadas

- Processar tudo com regras fixas sem LLM: detectaria duplicatas mas perderia inconsistencias semanticas
- Enviar dados brutos a LLM: violaria politica de dados sensiveis
- Framework de agentes (CrewAI): adiciona complexidade antes de validar o fluxo basico — defer para depois do treinamento dia 3/4

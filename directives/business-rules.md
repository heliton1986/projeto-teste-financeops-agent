# Diretivas de Regras de Negocio — FinanceOps Agent

## Regras de ingestao

### R01 — Campos obrigatorios
Todo lancamento deve ter: data, descricao, valor, categoria, centro_custo, origem.
Lancamento com campo ausente = inconsistencia tipo `campo_ausente`.

### R02 — Formato de data
Aceitar apenas YYYY-MM-DD. Outros formatos = inconsistencia tipo `formato_invalido`.

### R03 — Valor nao nulo
`valor` nao pode ser zero, nulo, ou string nao numerica.
`valor` negativo e permitido (estorno/devolucao).

### R04 — Origem valida
Campo `origem` aceita apenas: `csv`, `erp`.

## Regras de deteccao de inconsistencias

### R05 — Duplicata
Dois lancamentos com mesma (data, descricao, valor, centro_custo) = duplicata suspeita.
Regra: ambos sao marcados como `duplicata_suspeita`, nenhum e removido.

### R06 — Valor suspeito
Valor absoluto > 100.000 = `valor_alto_suspeito`. Requer revisao humana.
Valor absoluto < 0.01 = `valor_irrisorio_suspeito`.

### R07 — Descricao generica
Descricoes como "teste", "xxx", "n/a", ".", ou com menos de 3 caracteres = `descricao_suspeita`.

### R08 — Centro de custo desconhecido
`centro_custo` nao presente na lista de centros validos do periodo = `centro_custo_desconhecido`.
Lista de centros validos: fornecida por parametro em runtime ou via `directives/centros_custo.csv` se existir.
Se lista ausente: omitir esta verificacao (nao gerar falso positivo).

## Regras de auditoria

### R09 — audit_log imutavel
Toda operacao do sistema (ingestao, deteccao, relatorio) gera entrada em `audit_log`.
audit_log: apenas INSERT. Nunca UPDATE ou DELETE.

### R10 — Mascaramento antes do LLM
Antes de enviar qualquer lancamento ao DetectorAgent (LLM):
- `valor` substituido por faixa: "< 1k", "1k-10k", "10k-100k", "> 100k"
- `descricao` mantida (necessaria para analise semantica)
- CPF/CNPJ em qualquer campo: mascarar com `***`

### R11 — Somente leitura
Nenhum agente altera, remove, ou reescreve lancamentos na fonte CSV/ERP.

## Regras de relatorio

### R12 — Sumario obrigatorio
Relatorio executivo deve conter: total de lancamentos, total inconsistencias, valor total consolidado (sem mascaramento no relatorio — mascaramento e so para o LLM).

### R13 — Classificacao de severidade
Inconsistencias classificadas em:
- `critica`: duplicata confirmada, campo ausente
- `alta`: valor_alto_suspeito, centro_custo_desconhecido
- `media`: descricao_suspeita, valor_irrisorio_suspeito
- `baixa`: formato_invalido corrigivel

### R14 — Periodo do relatorio
Relatorio cobre exatamente o periodo dos lancamentos ingeridos. Nao extrapolar.

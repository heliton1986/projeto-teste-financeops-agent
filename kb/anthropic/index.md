# Anthropic SDK — FinanceOps Agent

## Como este projeto usa Anthropic

Apenas o `DetectorAgent` usa LLM. Todos os outros agentes sao determinisitcos.

## Configuracao

- **Modelo:** `claude-sonnet-4-6`
- **Temperatura:** `0` (determinismo maximo)
- **max_tokens:** `1024`
- **API Key:** variavel `ANTHROPIC_API_KEY`

## Regra critica

Mascaramento obrigatorio antes de enviar qualquer lancamento ao LLM (R10):
- `valor` → faixa: `< 1k`, `1k-10k`, `10k-100k`, `> 100k`
- CPF/CNPJ → `***`
- `descricao` mantida (necessaria para analise semantica)

## Arquivo relevante

- `src/agents/detector_agent.py` — unico ponto de chamada LLM no projeto

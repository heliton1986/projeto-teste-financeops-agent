# KB — FinanceOps Agent

Contexto denso para novas sessoes. Ler antes de qualquer acao no projeto.

## Quando ler cada arquivo

| Arquivo | Ler quando |
|---------|-----------|
| `domain.md` | Inicio de sessao — contexto do sistema, agentes, stack, escopo |
| `rules.md` | Antes de implementar/modificar qualquer agente ou regra de negocio |

## Estado do projeto

- **Versao:** v1 completa
- **Data:** 2026-04-28
- **Gates:** todos aprovados (Fases 1-4)
- **Testes:** 18/18 passando offline

## Proximos passos

1. CI/coverage antes de CrewAI (`.github/workflows/tests.yml`, cobertura minima 80%)
2. CrewAI + Chainlit + LangFuse (pos-treinamento dia 3/4)
3. Fase 5: FastAPI — POST /processar com upload CSV
4. Fase 6: Streamlit UI

## Fontes de verdade

- Regras de negocio: `directives/business-rules.md`
- Contratos de saida: `directives/output-contracts.md`
- Roteamento de modelos: `model_routing.yaml`
- Estado atual: `progress/PROGRESS.md`

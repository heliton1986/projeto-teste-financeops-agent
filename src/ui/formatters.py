from decimal import Decimal
from contracts.relatorio_contract import RelatorioExecutivo
from contracts.inconsistencia_contract import Inconsistencia


SEVERIDADE_COR = {
    "critica": "🔴",
    "alta": "🟠",
    "media": "🟡",
    "baixa": "🟢",
}

STATUS_LABEL = {
    "pronto": "✅ Pronto para fechamento",
    "requer_revisao": "⚠️ Requer revisão",
    "bloqueado": "🚫 Bloqueado",
}


def formatar_status(status: str) -> str:
    return STATUS_LABEL.get(status, status)


def formatar_valor(valor: Decimal) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_inconsistencias(inconsistencias: list[Inconsistencia]) -> list[dict]:
    return [
        {
            "Severidade": f"{SEVERIDADE_COR.get(i.severidade, '')} {i.severidade}",
            "Tipo": i.tipo,
            "Descricao": i.descricao,
            "Valor": i.valor_mascarado,
        }
        for i in inconsistencias
    ]


def resumo_severidades(por_severidade: dict[str, int]) -> list[dict]:
    ordem = ["critica", "alta", "media", "baixa"]
    return [
        {
            "Severidade": f"{SEVERIDADE_COR.get(s, '')} {s}",
            "Quantidade": por_severidade[s],
        }
        for s in ordem
        if s in por_severidade
    ]


def relatorio_para_json(relatorio: RelatorioExecutivo) -> str:
    return relatorio.model_dump_json(indent=2)

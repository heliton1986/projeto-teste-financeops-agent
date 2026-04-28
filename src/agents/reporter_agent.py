from decimal import Decimal

from contracts.inconsistencia_contract import InconsistenciasReport
from contracts.lancamento_contract import LancamentosNormalizados
from contracts.relatorio_contract import RelatorioExecutivo


class ReporterAgent:
    def gerar(self, lancamentos: LancamentosNormalizados, inconsistencias: InconsistenciasReport) -> RelatorioExecutivo:
        valor_total = sum(l.valor for l in lancamentos.lancamentos)

        por_severidade: dict[str, int] = {}
        for inc in inconsistencias.inconsistencias:
            por_severidade[inc.severidade] = por_severidade.get(inc.severidade, 0) + 1

        tem_critica = por_severidade.get("critica", 0) > 0
        tem_alta = por_severidade.get("alta", 0) > 0

        if tem_critica:
            status = "requer_revisao"
        elif tem_alta:
            status = "requer_revisao"
        else:
            status = "pronto"

        periodo = f"{lancamentos.periodo_inicio} a {lancamentos.periodo_fim}"

        return RelatorioExecutivo(
            run_id=lancamentos.run_id,
            periodo=periodo,
            total_lancamentos=lancamentos.total_lancamentos,
            valor_total=valor_total,
            total_inconsistencias=inconsistencias.total_inconsistencias,
            inconsistencias_por_severidade=por_severidade,
            inconsistencias=inconsistencias.inconsistencias,
            status_sistema=status,
        )

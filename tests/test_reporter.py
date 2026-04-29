from datetime import date
from decimal import Decimal
from uuid import uuid4

from contracts.inconsistencia_contract import Inconsistencia, InconsistenciasReport
from contracts.lancamento_contract import Lancamento, LancamentosNormalizados
from contracts.relatorio_contract import RelatorioExecutivo
from src.agents.reporter_agent import ReporterAgent


def _lancamento(**kwargs) -> Lancamento:
    defaults = dict(
        data=date(2026, 3, 1),
        descricao="Pagamento fornecedor",
        valor=Decimal("1000.00"),
        categoria="Fornecedores",
        centro_custo="TI",
        origem="csv",
    )
    defaults.update(kwargs)
    return Lancamento(**defaults)


def _resultado(lancamentos: list[Lancamento]) -> LancamentosNormalizados:
    datas = [l.data for l in lancamentos]
    return LancamentosNormalizados(
        run_id=uuid4(),
        total_lancamentos=len(lancamentos),
        periodo_inicio=min(datas),
        periodo_fim=max(datas),
        lancamentos=lancamentos,
    )


def _inconsistencias(inconsistencias: list[Inconsistencia], run_id=None) -> InconsistenciasReport:
    return InconsistenciasReport(
        run_id=run_id or uuid4(),
        total_analisados=10,
        total_inconsistencias=len(inconsistencias),
        inconsistencias=inconsistencias,
    )


def _inconsistencia(tipo="duplicata_suspeita", severidade="critica") -> Inconsistencia:
    return Inconsistencia(
        lancamento_id=uuid4(),
        tipo=tipo,
        severidade=severidade,
        descricao="Inconsistencia teste",
        valor_mascarado="1k-10k",
    )


def test_reporter_gera_relatorio_sem_inconsistencias():
    l = _lancamento()
    lancamentos = _resultado([l])
    inconsistencias = _inconsistencias([])
    reporter = ReporterAgent()
    relatorio = reporter.gerar(lancamentos, inconsistencias)
    assert isinstance(relatorio, RelatorioExecutivo)
    assert relatorio.status_sistema == "pronto"
    assert relatorio.total_inconsistencias == 0


def test_reporter_status_requer_revisao_critica():
    l = _lancamento()
    lancamentos = _resultado([l])
    inc = _inconsistencia(tipo="duplicata_suspeita", severidade="critica")
    inconsistencias = _inconsistencias([inc])
    reporter = ReporterAgent()
    relatorio = reporter.gerar(lancamentos, inconsistencias)
    assert relatorio.status_sistema == "requer_revisao"
    assert relatorio.inconsistencias_por_severidade.get("critica") == 1


def test_reporter_status_requer_revisao_alta():
    l = _lancamento()
    lancamentos = _resultado([l])
    inc = _inconsistencia(tipo="valor_alto_suspeito", severidade="alta")
    inconsistencias = _inconsistencias([inc])
    reporter = ReporterAgent()
    relatorio = reporter.gerar(lancamentos, inconsistencias)
    assert relatorio.status_sistema == "requer_revisao"
    assert relatorio.inconsistencias_por_severidade.get("alta") == 1


def test_reporter_calcula_valor_total():
    l1 = _lancamento(valor=Decimal("1000.00"))
    l2 = _lancamento(valor=Decimal("2000.00"), data=date(2026, 3, 2))
    lancamentos = _resultado([l1, l2])
    inconsistencias = _inconsistencias([])
    reporter = ReporterAgent()
    relatorio = reporter.gerar(lancamentos, inconsistencias)
    assert relatorio.valor_total == Decimal("3000.00")


def test_reporter_periodo_formatado():
    l1 = _lancamento(data=date(2026, 3, 1))
    l2 = _lancamento(data=date(2026, 3, 31))
    lancamentos = _resultado([l1, l2])
    inconsistencias = _inconsistencias([])
    reporter = ReporterAgent()
    relatorio = reporter.gerar(lancamentos, inconsistencias)
    assert "2026-03-01" in relatorio.periodo
    assert "2026-03-31" in relatorio.periodo

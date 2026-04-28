from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from contracts.inconsistencia_contract import Inconsistencia, InconsistenciasReport
from contracts.lancamento_contract import Lancamento, LancamentosNormalizados
from contracts.relatorio_contract import RelatorioExecutivo
from src.agents.validator_agent import ValidatorAgent


def _lancamentos_normalizados() -> LancamentosNormalizados:
    return LancamentosNormalizados(
        run_id=uuid4(),
        total_lancamentos=1,
        periodo_inicio=date(2026, 3, 1),
        periodo_fim=date(2026, 3, 1),
        lancamentos=[Lancamento(
            data=date(2026, 3, 1),
            descricao="Teste",
            valor=Decimal("100.00"),
            categoria="Cat",
            centro_custo="CC",
            origem="csv",
        )],
    )


def _inconsistencias_report(run_id) -> InconsistenciasReport:
    return InconsistenciasReport(
        run_id=run_id,
        total_analisados=1,
        total_inconsistencias=0,
        inconsistencias=[],
    )


def test_valida_lancamentos_normalizados():
    instancia = _lancamentos_normalizados()
    vr = ValidatorAgent().validar_instancia(instancia)
    assert vr.valido is True
    assert vr.contrato_validado == "LancamentosNormalizados"
    assert vr.erros == []


def test_valida_inconsistencias_report():
    instancia = _inconsistencias_report(uuid4())
    vr = ValidatorAgent().validar_instancia(instancia)
    assert vr.valido is True
    assert vr.contrato_validado == "InconsistenciasReport"


def test_valida_relatorio_executivo():
    run_id = uuid4()
    instancia = RelatorioExecutivo(
        run_id=run_id,
        periodo="2026-03-01 a 2026-03-31",
        total_lancamentos=1,
        valor_total=Decimal("100.00"),
        total_inconsistencias=0,
        inconsistencias_por_severidade={},
        inconsistencias=[],
        status_sistema="pronto",
    )
    vr = ValidatorAgent().validar_instancia(instancia)
    assert vr.valido is True
    assert vr.contrato_validado == "RelatorioExecutivo"


def test_validar_lancamentos_via_dict_invalido():
    vr = ValidatorAgent().validar_lancamentos({})
    assert vr.valido is False
    assert len(vr.erros) > 0

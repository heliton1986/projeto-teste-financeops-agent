import os
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

from contracts.inconsistencia_contract import InconsistenciasReport
from contracts.lancamento_contract import Lancamento, LancamentosNormalizados
from contracts.relatorio_contract import RelatorioExecutivo


def _lancamentos_normalizados() -> LancamentosNormalizados:
    l = Lancamento(
        data=date(2026, 3, 1),
        descricao="Pagamento fornecedor",
        valor=Decimal("1000.00"),
        categoria="Fornecedores",
        centro_custo="TI",
        origem="csv",
    )
    return LancamentosNormalizados(
        run_id=uuid4(),
        total_lancamentos=1,
        periodo_inicio=date(2026, 3, 1),
        periodo_fim=date(2026, 3, 1),
        lancamentos=[l],
    )


def _inconsistencias_report(run_id) -> InconsistenciasReport:
    return InconsistenciasReport(
        run_id=run_id,
        total_analisados=1,
        total_inconsistencias=0,
        inconsistencias=[],
    )


def test_orchestrator_executa_fluxo_completo(tmp_path):
    lancamentos = _lancamentos_normalizados()
    inconsistencias = _inconsistencias_report(lancamentos.run_id)
    relatorio = RelatorioExecutivo(
        run_id=lancamentos.run_id,
        periodo="2026-03-01 a 2026-03-01",
        total_lancamentos=1,
        valor_total=Decimal("1000.00"),
        total_inconsistencias=0,
        inconsistencias_por_severidade={},
        inconsistencias=[],
        status_sistema="pronto",
    )

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        with patch("src.agents.orchestrator.IngestionAgent") as mock_ing, \
             patch("src.agents.orchestrator.DetectorAgent") as mock_det, \
             patch("src.agents.orchestrator.ValidatorAgent") as mock_val, \
             patch("src.agents.orchestrator.ReporterAgent") as mock_rep:

            mock_ing.return_value.processar.return_value = lancamentos
            mock_det.return_value.detectar.return_value = inconsistencias
            mock_rep.return_value.gerar.return_value = relatorio

            from src.agents.orchestrator import OrchestratorAgent
            agent = OrchestratorAgent()
            result = agent.executar("fake.csv")

            assert isinstance(result, RelatorioExecutivo)
            assert result.status_sistema == "pronto"
            mock_ing.return_value.processar.assert_called_once_with("fake.csv")
            mock_det.return_value.detectar.assert_called_once_with(lancamentos)
            mock_rep.return_value.gerar.assert_called_once_with(lancamentos, inconsistencias)

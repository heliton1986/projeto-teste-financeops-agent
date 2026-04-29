import os
from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from contracts.inconsistencia_contract import InconsistenciasReport
from contracts.lancamento_contract import Lancamento, LancamentosNormalizados
from contracts.relatorio_contract import RelatorioExecutivo


def _relatorio_mock() -> RelatorioExecutivo:
    run_id = uuid4()
    return RelatorioExecutivo(
        run_id=run_id,
        periodo="2026-03-01 a 2026-03-31",
        total_lancamentos=9,
        valor_total=Decimal("110952.40"),
        total_inconsistencias=2,
        inconsistencias_por_severidade={"critica": 1, "media": 1},
        inconsistencias=[],
        status_sistema="requer_revisao",
    )


CSV_VALIDO = b"""data,descricao,valor,categoria,centro_custo,origem
2026-03-01,Pagamento fornecedor ABC,5000.00,Fornecedores,TI,csv
2026-03-02,Assinatura software,1200.50,Tecnologia,TI,csv
"""


@pytest.fixture
def client():
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        from src.api.main import app
        return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_processar_csv_valido(client):
    relatorio = _relatorio_mock()
    with patch("src.api.main.OrchestratorAgent") as mock_orch:
        mock_orch.return_value.executar.return_value = relatorio
        response = client.post(
            "/processar",
            files={"file": ("lancamentos.csv", CSV_VALIDO, "text/csv")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status_sistema"] == "requer_revisao"
    assert data["total_lancamentos"] == 9


def test_processar_rejeita_nao_csv(client):
    response = client.post(
        "/processar",
        files={"file": ("dados.xlsx", b"conteudo", "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "CSV" in response.json()["detail"]


def test_processar_rejeita_csv_vazio(client):
    response = client.post(
        "/processar",
        files={"file": ("vazio.csv", b"", "text/csv")},
    )
    assert response.status_code == 400


def test_processar_erro_runtime_vira_422(client):
    with patch("src.api.main.OrchestratorAgent") as mock_orch:
        mock_orch.return_value.executar.side_effect = RuntimeError("CSV invalido: nenhum lancamento valido")
        response = client.post(
            "/processar",
            files={"file": ("lancamentos.csv", CSV_VALIDO, "text/csv")},
        )
    assert response.status_code == 422
    assert "CSV invalido" in response.json()["detail"]

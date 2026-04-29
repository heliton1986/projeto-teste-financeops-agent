from decimal import Decimal
from uuid import uuid4

from contracts.inconsistencia_contract import Inconsistencia
from src.ui.formatters import (
    formatar_status,
    formatar_valor,
    formatar_inconsistencias,
    resumo_severidades,
    relatorio_para_json,
)
from contracts.relatorio_contract import RelatorioExecutivo


def _inconsistencia(tipo="duplicata_suspeita", severidade="critica") -> Inconsistencia:
    return Inconsistencia(
        lancamento_id=uuid4(),
        tipo=tipo,
        severidade=severidade,
        descricao="Lancamento duplicado",
        valor_mascarado="1k-10k",
    )


def test_formatar_status_pronto():
    assert "Pronto" in formatar_status("pronto")


def test_formatar_status_requer_revisao():
    assert "revisão" in formatar_status("requer_revisao")


def test_formatar_status_bloqueado():
    assert "Bloqueado" in formatar_status("bloqueado")


def test_formatar_valor():
    resultado = formatar_valor(Decimal("5000.50"))
    assert "5.000,50" in resultado
    assert "R$" in resultado


def test_formatar_inconsistencias_estrutura():
    inc = _inconsistencia()
    rows = formatar_inconsistencias([inc])
    assert len(rows) == 1
    assert "Severidade" in rows[0]
    assert "Tipo" in rows[0]
    assert "critica" in rows[0]["Severidade"]


def test_formatar_inconsistencias_vazia():
    assert formatar_inconsistencias([]) == []


def test_resumo_severidades_ordenado():
    por_sev = {"media": 1, "critica": 2}
    resumo = resumo_severidades(por_sev)
    assert resumo[0]["Severidade"].endswith("critica")
    assert resumo[1]["Severidade"].endswith("media")


def test_relatorio_para_json():
    relatorio = RelatorioExecutivo(
        run_id=uuid4(),
        periodo="2026-03-01 a 2026-03-31",
        total_lancamentos=5,
        valor_total=Decimal("10000.00"),
        total_inconsistencias=1,
        inconsistencias_por_severidade={"critica": 1},
        inconsistencias=[_inconsistencia()],
        status_sistema="requer_revisao",
    )
    json_str = relatorio_para_json(relatorio)
    assert "requer_revisao" in json_str
    assert "run_id" in json_str

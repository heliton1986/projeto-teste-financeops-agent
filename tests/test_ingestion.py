import pytest
from pathlib import Path

from src.agents.ingestion_agent import IngestionAgent

FIXTURE = str(Path(__file__).parent / "fixtures" / "lancamentos_fixture.csv")


def test_ingestao_fixture_basica():
    agent = IngestionAgent()
    resultado = agent.processar(FIXTURE)
    assert resultado.total_lancamentos == 9
    assert len(resultado.inconsistencias_ingestao) == 1


def test_ingestao_periodo_correto():
    from datetime import date
    agent = IngestionAgent()
    resultado = agent.processar(FIXTURE)
    assert resultado.periodo_inicio == date(2026, 3, 1)
    assert resultado.periodo_fim == date(2026, 3, 15)


LINHA_VALIDA = "2026-03-01,Pagamento valido,100.00,Cat,CC,csv"


def test_ingestao_rejeita_descricao_ausente(tmp_path):
    csv = tmp_path / "test.csv"
    csv.write_text(f"data,descricao,valor,categoria,centro_custo,origem\n{LINHA_VALIDA}\n2026-03-01,,200.00,Cat,CC,csv\n")
    agent = IngestionAgent()
    resultado = agent.processar(str(csv))
    assert resultado.total_lancamentos == 1
    assert len(resultado.inconsistencias_ingestao) == 1
    assert "descricao" in resultado.inconsistencias_ingestao[0].motivo


def test_ingestao_rejeita_data_invalida(tmp_path):
    csv = tmp_path / "test.csv"
    csv.write_text(f"data,descricao,valor,categoria,centro_custo,origem\n{LINHA_VALIDA}\n01/03/2026,Teste,100.00,Cat,CC,csv\n")
    agent = IngestionAgent()
    resultado = agent.processar(str(csv))
    assert resultado.total_lancamentos == 1
    assert len(resultado.inconsistencias_ingestao) == 1
    assert "data" in resultado.inconsistencias_ingestao[0].motivo


def test_ingestao_rejeita_origem_invalida(tmp_path):
    csv = tmp_path / "test.csv"
    csv.write_text(f"data,descricao,valor,categoria,centro_custo,origem\n{LINHA_VALIDA}\n2026-03-01,Teste,100.00,Cat,CC,sap\n")
    agent = IngestionAgent()
    resultado = agent.processar(str(csv))
    assert resultado.total_lancamentos == 1
    assert len(resultado.inconsistencias_ingestao) == 1
    assert "origem" in resultado.inconsistencias_ingestao[0].motivo


def test_ingestao_arquivo_inexistente():
    agent = IngestionAgent()
    with pytest.raises(FileNotFoundError):
        agent.processar("/nao/existe.csv")


def test_ingestao_csv_todo_invalido(tmp_path):
    csv = tmp_path / "test.csv"
    csv.write_text("data,descricao,valor,categoria,centro_custo,origem\n,,,,, \n")
    agent = IngestionAgent()
    with pytest.raises(RuntimeError, match="Nenhum lancamento valido"):
        agent.processar(str(csv))

"""
Integration tests — chamam a API real do Anthropic.
Rodam apenas quando ANTHROPIC_API_KEY está disponível.

Executar local:
    pytest tests/test_detector_integration.py -v

O CI pula automaticamente (sem a key no ambiente).
"""
import os
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from contracts.lancamento_contract import Lancamento, LancamentosNormalizados
from src.agents.detector_agent import DetectorAgent
from src.agents.validator_agent import ValidatorAgent

pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY não configurada",
)


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


def test_pipeline_semantico_retorna_contrato_valido():
    """
    LLM entra em _analisar_com_llm com lancamentos que têm
    inconsistência semântica clara (categoria errada).
    Gate: InconsistenciasReport válido via ValidatorAgent.
    Não afirma qual inconsistência a LLM encontrou — isso é não-determinístico.
    """
    lancamentos = [
        _lancamento(
            descricao="Almoço executivo com cliente",
            categoria="Equipamentos de TI",  # inconsistência semântica clara
            centro_custo="TI",
            valor=Decimal("350.00"),
        ),
        _lancamento(
            descricao="Licença Adobe Creative Cloud",
            categoria="Alimentação",  # inconsistência semântica clara
            centro_custo="Marketing",
            valor=Decimal("2400.00"),
        ),
        _lancamento(
            descricao="Pagamento fornecedor ABC Ltda",
            categoria="Fornecedores",
            centro_custo="Compras",
            valor=Decimal("8500.00"),
        ),
    ]

    agent = DetectorAgent()
    resultado = agent.detectar(_resultado(lancamentos))

    # gate determinístico: contrato Pydantic via ValidatorAgent
    vr = ValidatorAgent().validar_instancia(resultado)
    assert vr.valido is True, f"Contrato inválido: {vr.erros}"
    assert resultado.total_analisados == 3
    # inconsistencias pode ser 0 ou mais — a LLM decide, o gate valida o formato
    for inc in resultado.inconsistencias:
        assert inc.lancamento_id in {l.id for l in lancamentos}
        assert inc.tipo is not None
        assert inc.severidade in {"critica", "alta", "media", "baixa"}

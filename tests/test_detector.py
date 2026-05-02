from datetime import date
from decimal import Decimal
from uuid import uuid4

from contracts.lancamento_contract import Lancamento, LancamentosNormalizados
from src.agents.detector_agent import DetectorAgent


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


def test_detecta_duplicata():
    l1 = _lancamento()
    l2 = _lancamento()
    agent = DetectorAgent.__new__(DetectorAgent)
    resultado = agent._detectar_duplicatas([l1, l2])
    assert len(resultado) == 2
    assert all(r.tipo == "duplicata_suspeita" for r in resultado)
    assert all(r.severidade == "critica" for r in resultado)


def test_nao_detecta_duplicata_valores_diferentes():
    l1 = _lancamento(valor=Decimal("1000.00"))
    l2 = _lancamento(valor=Decimal("2000.00"))
    agent = DetectorAgent.__new__(DetectorAgent)
    resultado = agent._detectar_duplicatas([l1, l2])
    assert len(resultado) == 0


def test_detecta_valor_alto():
    l = _lancamento(valor=Decimal("150000.00"))
    agent = DetectorAgent.__new__(DetectorAgent)
    resultado = agent._detectar_valores_suspeitos([l])
    assert len(resultado) == 1
    assert resultado[0].tipo == "valor_alto_suspeito"
    assert resultado[0].severidade == "alta"


def test_nao_detecta_valor_normal():
    l = _lancamento(valor=Decimal("5000.00"))
    agent = DetectorAgent.__new__(DetectorAgent)
    resultado = agent._detectar_valores_suspeitos([l])
    assert len(resultado) == 0


def test_detecta_descricao_suspeita():
    for desc in ["teste", "xxx", "n/a", "."]:
        l = _lancamento(descricao=desc)
        agent = DetectorAgent.__new__(DetectorAgent)
        resultado = agent._detectar_descricoes_suspeitas([l])
        assert len(resultado) == 1, f"esperava detectar '{desc}'"
        assert resultado[0].tipo == "descricao_suspeita"


def test_nao_detecta_descricao_normal():
    l = _lancamento(descricao="Pagamento fornecedor ABC")
    agent = DetectorAgent.__new__(DetectorAgent)
    resultado = agent._detectar_descricoes_suspeitas([l])
    assert len(resultado) == 0


def test_mascaramento_valor():
    from src.agents.detector_agent import _mascarar_valor
    assert _mascarar_valor(Decimal("500")) == "< 1k"
    assert _mascarar_valor(Decimal("5000")) == "1k-10k"
    assert _mascarar_valor(Decimal("50000")) == "10k-100k"
    assert _mascarar_valor(Decimal("150000")) == "> 100k"


def test_mascaramento_cpf_cnpj():
    from src.agents.detector_agent import _mascarar_cpf_cnpj
    assert _mascarar_cpf_cnpj("CPF 123.456.789-09") == "CPF ***"
    assert _mascarar_cpf_cnpj("sem cpf aqui") == "sem cpf aqui"


def test_filtrar_para_llm_exclui_criticos():
    from contracts.inconsistencia_contract import Inconsistencia
    l1 = _lancamento()
    l2 = _lancamento(descricao="Outro lancamento", valor=Decimal("2000.00"))
    inc = Inconsistencia(
        lancamento_id=l1.id,
        tipo="duplicata_suspeita",
        severidade="critica",
        descricao="duplicata",
        valor_mascarado="1k-10k",
    )
    agent = DetectorAgent.__new__(DetectorAgent)
    resultado = agent._filtrar_para_llm([l1, l2], [inc])
    assert l1 not in resultado
    assert l2 in resultado


def test_filtrar_para_llm_limite_20():
    lancamentos = [_lancamento(descricao=f"Lanc {i}", valor=Decimal(str(i * 100 + 1))) for i in range(25)]
    agent = DetectorAgent.__new__(DetectorAgent)
    resultado = agent._filtrar_para_llm(lancamentos, [])
    assert len(resultado) <= 20


def test_parsear_resposta_llm_valida():
    l = _lancamento()
    agent = DetectorAgent.__new__(DetectorAgent)
    texto = f"id:{l.id}|descricao_suspeita|Descricao incompativel com categoria"
    resultado = agent._parsear_resposta_llm(texto, [l])
    assert len(resultado) == 1
    assert resultado[0].tipo == "descricao_suspeita"
    assert resultado[0].lancamento_id == l.id


def test_parsear_resposta_llm_id_invalido():
    l = _lancamento()
    agent = DetectorAgent.__new__(DetectorAgent)
    texto = "id:00000000-0000-0000-0000-000000000000|descricao_suspeita|texto"
    resultado = agent._parsear_resposta_llm(texto, [l])
    assert len(resultado) == 0


def test_parsear_resposta_llm_vazia():
    agent = DetectorAgent.__new__(DetectorAgent)
    resultado = agent._parsear_resposta_llm("", [])
    assert resultado == []


def test_detecta_valor_irrisorio():
    l = _lancamento(valor=Decimal("0.001"))
    agent = DetectorAgent.__new__(DetectorAgent)
    resultado = agent._detectar_valores_suspeitos([l])
    assert len(resultado) == 1
    assert resultado[0].tipo == "valor_irrisorio_suspeito"
    assert resultado[0].severidade == "media"


# --- mock tests: lógica de controle (CI-safe, sem API) ---

from unittest.mock import MagicMock, patch


def _agent_mockado():
    with patch("src.agents.detector_agent.anthropic.Anthropic"), \
         patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        return DetectorAgent()


def test_detector_init_instancia_cliente():
    with patch("src.agents.detector_agent.anthropic.Anthropic") as mock_cls, \
         patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        agent = DetectorAgent()
        mock_cls.assert_called_once()
        assert agent.client is mock_cls.return_value


def test_detectar_chama_llm_quando_ha_candidatos():
    agent = _agent_mockado()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="")]
    agent.client.messages.create.return_value = mock_response

    resultado = agent.detectar(_resultado([_lancamento()]))

    agent.client.messages.create.assert_called_once()
    assert resultado.total_analisados == 1


def test_detectar_nao_chama_llm_quando_todos_criticos():
    agent = _agent_mockado()
    l1 = _lancamento()
    l2 = _lancamento()  # mesmo data/desc/valor/centro_custo → duplicata critica
    agent.detectar(_resultado([l1, l2]))
    agent.client.messages.create.assert_not_called()


def test_analisar_com_llm_retorna_inconsistencia():
    agent = _agent_mockado()
    l = _lancamento()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=f"id:{l.id}|inconsistencia_semantica|Descricao incompativel")]
    agent.client.messages.create.return_value = mock_response

    resultado = agent._analisar_com_llm([l])

    assert len(resultado) == 1
    assert resultado[0].tipo == "inconsistencia_semantica"
    assert resultado[0].lancamento_id == l.id


def test_analisar_com_llm_resposta_sem_inconsistencias():
    agent = _agent_mockado()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Nenhuma inconsistencia encontrada.")]
    agent.client.messages.create.return_value = mock_response

    resultado = agent._analisar_com_llm([_lancamento()])
    assert resultado == []


def test_analisar_com_llm_todas_tentativas_falham():
    agent = _agent_mockado()
    agent.client.messages.create.side_effect = Exception("API error")

    resultado = agent._analisar_com_llm([_lancamento()])

    assert resultado == []
    assert agent.client.messages.create.call_count == 3


def test_analisar_com_llm_sucesso_na_segunda_tentativa():
    agent = _agent_mockado()
    l = _lancamento()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="")]
    agent.client.messages.create.side_effect = [Exception("timeout"), mock_response]

    agent._analisar_com_llm([l])

    assert agent.client.messages.create.call_count == 2

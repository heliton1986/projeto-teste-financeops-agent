import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd

from src.agents.orchestrator import OrchestratorAgent
from src.ui.formatters import (
    formatar_status,
    formatar_valor,
    formatar_inconsistencias,
    resumo_severidades,
    relatorio_para_json,
)

st.set_page_config(
    page_title="FinanceOps Agent",
    page_icon="💼",
    layout="wide",
)

st.title("💼 FinanceOps Agent")
st.caption("Consolidação e auditoria automatizada de lançamentos financeiros")

uploaded = st.file_uploader("Selecione o arquivo CSV de lançamentos", type=["csv"])

if uploaded is not None:
    with st.spinner("Processando lançamentos..."):
        conteudo = uploaded.read()
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp.write(conteudo)
            tmp_path = tmp.name

        try:
            agente = OrchestratorAgent()
            relatorio = agente.executar(tmp_path)
        except RuntimeError as e:
            st.error(f"Erro ao processar CSV: {e}")
            st.stop()
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    st.success(formatar_status(relatorio.status_sistema))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lançamentos", relatorio.total_lancamentos)
    col2.metric("Valor Total", formatar_valor(relatorio.valor_total))
    col3.metric("Inconsistências", relatorio.total_inconsistencias)
    col4.metric("Período", relatorio.periodo)

    if relatorio.total_inconsistencias > 0:
        st.subheader("Inconsistências por Severidade")
        resumo = resumo_severidades(relatorio.inconsistencias_por_severidade)
        st.dataframe(pd.DataFrame(resumo), use_container_width=True, hide_index=True)

        st.subheader("Detalhamento")
        rows = formatar_inconsistencias(relatorio.inconsistencias)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma inconsistência detectada.")

    st.subheader("Baixar Relatório")
    st.download_button(
        label="⬇️ Baixar JSON",
        data=relatorio_para_json(relatorio),
        file_name=f"relatorio_{relatorio.run_id}.json",
        mime="application/json",
    )

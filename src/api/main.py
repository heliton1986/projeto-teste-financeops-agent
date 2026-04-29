import tempfile
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from contracts.relatorio_contract import RelatorioExecutivo
from src.agents.orchestrator import OrchestratorAgent

app = FastAPI(
    title="FinanceOps Agent API",
    description="API para processamento de lancamentos financeiros e deteccao de inconsistencias",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/processar", response_model=RelatorioExecutivo)
async def processar(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV (.csv)")

    conteudo = await file.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="Arquivo CSV vazio")

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp.write(conteudo)
        tmp_path = tmp.name

    try:
        agente = OrchestratorAgent()
        relatorio = agente.executar(tmp_path)
        return relatorio
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)

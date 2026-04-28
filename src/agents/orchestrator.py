from src.agents.detector_agent import DetectorAgent
from src.agents.ingestion_agent import IngestionAgent
from src.agents.reporter_agent import ReporterAgent
from src.agents.validator_agent import ValidatorAgent
from src.db.audit import registrar
from src.db.connection import get_session
from contracts.relatorio_contract import RelatorioExecutivo


class OrchestratorAgent:
    def __init__(self):
        self.ingestion = IngestionAgent()
        self.detector = DetectorAgent()
        self.validator = ValidatorAgent()
        self.reporter = ReporterAgent()

    def executar(self, csv_path: str) -> RelatorioExecutivo:
        with get_session() as session:
            lancamentos = self.ingestion.processar(csv_path)
            registrar(session, lancamentos.run_id, "IngestionAgent", "ingestao_csv", "ok", {
                "total_lancamentos": lancamentos.total_lancamentos,
                "erros_ingestao": len(lancamentos.inconsistencias_ingestao),
                "periodo_inicio": str(lancamentos.periodo_inicio),
                "periodo_fim": str(lancamentos.periodo_fim),
            })

            inconsistencias = self.detector.detectar(lancamentos)
            registrar(session, lancamentos.run_id, "DetectorAgent", "deteccao_inconsistencias", "ok", {
                "total_analisados": inconsistencias.total_analisados,
                "total_inconsistencias": inconsistencias.total_inconsistencias,
                "tipos": [i.tipo for i in inconsistencias.inconsistencias],
            })

            relatorio = self.reporter.gerar(lancamentos, inconsistencias)
            registrar(session, lancamentos.run_id, "ReporterAgent", "geracao_relatorio", "ok", {
                "status_sistema": relatorio.status_sistema,
                "total_lancamentos": relatorio.total_lancamentos,
                "total_inconsistencias": relatorio.total_inconsistencias,
            })

        return relatorio

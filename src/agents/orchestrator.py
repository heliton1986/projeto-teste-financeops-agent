from src.agents.detector_agent import DetectorAgent
from src.agents.ingestion_agent import IngestionAgent
from src.agents.reporter_agent import ReporterAgent
from src.agents.validator_agent import ValidatorAgent
from contracts.relatorio_contract import RelatorioExecutivo


class OrchestratorAgent:
    def __init__(self):
        self.ingestion = IngestionAgent()
        self.detector = DetectorAgent()
        self.validator = ValidatorAgent()
        self.reporter = ReporterAgent()

    def executar(self, csv_path: str) -> RelatorioExecutivo:
        lancamentos = self.ingestion.processar(csv_path)
        inconsistencias = self.detector.detectar(lancamentos)
        relatorio = self.reporter.gerar(lancamentos, inconsistencias)
        return relatorio

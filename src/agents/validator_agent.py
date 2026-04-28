from pydantic import BaseModel, ValidationError

from contracts.inconsistencia_contract import InconsistenciasReport
from contracts.lancamento_contract import LancamentosNormalizados
from contracts.relatorio_contract import RelatorioExecutivo, ValidationResult


class ValidatorAgent:
    def validar_lancamentos(self, dados: dict) -> ValidationResult:
        return self._validar(dados, LancamentosNormalizados, "LancamentosNormalizados")

    def validar_inconsistencias(self, dados: dict) -> ValidationResult:
        return self._validar(dados, InconsistenciasReport, "InconsistenciasReport")

    def validar_relatorio(self, dados: dict) -> ValidationResult:
        return self._validar(dados, RelatorioExecutivo, "RelatorioExecutivo")

    def validar_instancia(self, instancia: BaseModel) -> ValidationResult:
        """Revalida instancia Pydantic ja criada — defesa em profundidade entre fases."""
        nome = type(instancia).__name__
        return self._validar(instancia.model_dump(), type(instancia), nome)

    def _validar(self, dados: dict, modelo, nome: str) -> ValidationResult:
        try:
            modelo(**dados)
            return ValidationResult(valido=True, contrato_validado=nome)
        except ValidationError as e:
            erros = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
            return ValidationResult(valido=False, erros=erros, contrato_validado=nome)

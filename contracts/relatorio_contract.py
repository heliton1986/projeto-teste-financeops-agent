from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from contracts.inconsistencia_contract import Inconsistencia


class RelatorioExecutivo(BaseModel):
    run_id: UUID
    periodo: str
    total_lancamentos: int
    valor_total: Decimal
    total_inconsistencias: int
    inconsistencias_por_severidade: dict[str, int]
    inconsistencias: list[Inconsistencia]
    status_sistema: Literal["pronto", "requer_revisao", "bloqueado"]
    gerado_em: datetime = Field(default_factory=datetime.utcnow)


class ValidationResult(BaseModel):
    valido: bool
    erros: list[str] = Field(default_factory=list)
    avisos: list[str] = Field(default_factory=list)
    contrato_validado: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

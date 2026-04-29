from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

TipoInconsistencia = Literal[
    "duplicata_suspeita",
    "campo_ausente",
    "formato_invalido",
    "valor_alto_suspeito",
    "valor_irrisorio_suspeito",
    "descricao_suspeita",
    "centro_custo_desconhecido",
    "inconsistencia_semantica",
]

Severidade = Literal["critica", "alta", "media", "baixa"]


class Inconsistencia(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    lancamento_id: UUID
    tipo: TipoInconsistencia
    severidade: Severidade
    descricao: str
    valor_mascarado: str


class InconsistenciasReport(BaseModel):
    run_id: UUID
    total_analisados: int
    total_inconsistencias: int
    inconsistencias: list[Inconsistencia]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

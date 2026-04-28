from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Lancamento(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    data: date
    descricao: str
    valor: Decimal
    categoria: str
    centro_custo: str
    origem: Literal["csv", "erp"]


class InconsistenciaIngestao(BaseModel):
    linha: int
    motivo: str
    dados_brutos: dict


class LancamentosNormalizados(BaseModel):
    run_id: UUID = Field(default_factory=uuid4)
    total_lancamentos: int
    periodo_inicio: date
    periodo_fim: date
    lancamentos: list[Lancamento]
    inconsistencias_ingestao: list[InconsistenciaIngestao] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

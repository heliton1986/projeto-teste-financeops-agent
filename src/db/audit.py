import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.db.models import AuditLog


def registrar(
    session: Session,
    run_id: uuid.UUID,
    agente: str,
    acao: str,
    status: str,
    detalhe: dict[str, Any] | None = None,
) -> None:
    entrada = AuditLog(
        run_id=run_id,
        agente=agente,
        acao=acao,
        status=status,
        detalhe=detalhe,
    )
    session.add(entrada)
    session.flush()

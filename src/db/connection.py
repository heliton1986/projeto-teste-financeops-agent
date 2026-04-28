import os
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.db.models import Base

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        url = os.environ.get("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL nao definida")
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
    return _SessionLocal


@contextmanager
def get_session() -> Session:
    factory = get_session_factory()
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def criar_schema():
    Base.metadata.create_all(bind=get_engine())


def verificar_conexao() -> bool:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def verificar_tabelas() -> dict[str, bool]:
    tabelas_esperadas = ["lancamentos", "inconsistencias", "audit_log"]
    resultado = {}
    try:
        engine = get_engine()
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tabelas_existentes = inspector.get_table_names()
        for t in tabelas_esperadas:
            resultado[t] = t in tabelas_existentes
    except Exception:
        for t in tabelas_esperadas:
            resultado[t] = False
    return resultado

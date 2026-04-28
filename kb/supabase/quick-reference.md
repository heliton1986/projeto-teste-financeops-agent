# Supabase — Quick Reference

## Conexao

```python
# connection.py — padrao do projeto
from src.db.connection import get_session, criar_schema

# Criar tabelas (onboarding Gate 4)
criar_schema()

# Sessao no runner — abrir aqui, passar para fases
with get_session() as session:
    fase_2(session)
    fase_3(session)
```

## Persistir lancamento

```python
from src.db.models import LancamentoDB
db_obj = LancamentoDB(data=l.data, descricao=l.descricao, valor=l.valor, ...)
session.add(db_obj)
session.flush()
```

## audit_log

```python
from src.db.audit import registrar
registrar(session, run_id, "NomeAgente", "acao", "ok|falhou", {"detalhe": "..."})
# INSERT only — nunca UPDATE/DELETE
```

## Verificar conexao

```python
from src.db.connection import verificar_conexao, verificar_tabelas
ok = verificar_conexao()          # SELECT 1
tabs = verificar_tabelas()        # dict[str, bool]
```

## Variaveis de ambiente

```
DATABASE_URL=postgresql://user:pass@host:5432/db
```

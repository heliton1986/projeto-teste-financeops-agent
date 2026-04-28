# Pydantic — Quick Reference

## Definir contrato

```python
from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime

class MeuContrato(BaseModel):
    campo_obrigatorio: str
    valor: Decimal
    data: date
    timestamp: datetime = None
```

## Validar instancia (padrao ValidatorAgent)

```python
from src.agents.validator_agent import ValidatorAgent

vr = ValidatorAgent().validar_instancia(instancia)
if not vr.valido:
    raise RuntimeError(f"Contrato invalido: {vr.erros}")
```

## Serializar / deserializar

```python
dados = instancia.model_dump()         # dict
json_str = instancia.model_dump_json() # JSON string
nova = MeuContrato.model_validate(dados)
```

## Erro de validacao

```python
from pydantic import ValidationError
try:
    obj = MeuContrato(**dados)
except ValidationError as e:
    erros = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
```

## Instanciar sem __init__ (testes)

```python
# Para testar agente que exige API key no __init__
agente = MeuAgente.__new__(MeuAgente)
# agente.metodo_interno(dados)  — sem chamar __init__
```

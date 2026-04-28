# Anthropic SDK — Quick Reference

## Chamada padrao (DetectorAgent)

```python
import anthropic

client = anthropic.Anthropic()  # usa ANTHROPIC_API_KEY do ambiente

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    temperature=0,
    messages=[{"role": "user", "content": prompt}]
)
resultado = response.content[0].text
```

## Mascaramento antes de enviar

```python
def _mascarar_valor(valor: Decimal) -> str:
    v = abs(valor)
    if v < 1000:    return "< 1k"
    if v < 10000:   return "1k-10k"
    if v < 100000:  return "10k-100k"
    return "> 100k"
```

## Verificar API key disponivel

```python
import os
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("ANTHROPIC_API_KEY nao definida")
```

## Variaveis de ambiente

```
ANTHROPIC_API_KEY=sk-ant-...
```

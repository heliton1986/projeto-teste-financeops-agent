"""
FinanceOps Agent — Gate 1: Onboarding

Verifica ambiente, dependencias, conexao DB e schema.
Uso: python execution/run_onboarding_flow.py

Exit codes:
  0 — Gate 1 aprovado (pronto para Fase 2)
  1 — Falha critica
  2 — Bloqueio real (requer intervencao humana)
"""
import sys
import time
from datetime import datetime
from pathlib import Path

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

_env_path = _root / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            import os
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

SEPARADOR = "=" * 56


def log(nivel: str, mensagem: str, duracao: float | None = None) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    dur = f"  ({duracao:.1f}s)" if duracao is not None else ""
    print(f"[{ts}] {nivel:<35} {mensagem}{dur}", flush=True)


def cabecalho() -> None:
    print(f"\n{SEPARADOR}", flush=True)
    print("  FinanceOps Agent — Gate 1: Onboarding", flush=True)
    print(f"{SEPARADOR}\n", flush=True)


def rodape(gates_ok: int, gates_total: int) -> None:
    print(f"\n{SEPARADOR}", flush=True)
    print(f"  Gates: {gates_ok}/{gates_total} aprovados", flush=True)
    if gates_ok == gates_total:
        print("  Gate 1: APROVADO — pronto para Fase 2", flush=True)
        print("  Proximo passo: python execution/run_flow.py", flush=True)
    else:
        print("  Gate 1: REPROVADO — corrigir erros acima", flush=True)
    print(f"{SEPARADOR}\n", flush=True)


class BlockingError(Exception):
    pass


def gate_dependencias() -> None:
    label = "[Gate — Dependencias]"
    t0 = time.monotonic()
    log(label, "verificando...")
    erros = []
    try:
        import anthropic  # noqa: F401
    except ImportError:
        erros.append("anthropic nao instalado")
    try:
        import pydantic  # noqa: F401
    except ImportError:
        erros.append("pydantic nao instalado")
    try:
        import sqlalchemy  # noqa: F401
    except ImportError:
        erros.append("sqlalchemy nao instalado")
    if erros:
        raise RuntimeError(f"pip install -r requirements.txt — faltam: {', '.join(erros)}")
    log(label, "APROVADO", time.monotonic() - t0)


def gate_variaveis_ambiente() -> None:
    import os
    label = "[Gate — Variaveis de Ambiente]"
    t0 = time.monotonic()
    log(label, "verificando...")
    ausentes = []
    for var in ["ANTHROPIC_API_KEY", "DATABASE_URL"]:
        if not os.environ.get(var):
            ausentes.append(var)
    if ausentes:
        raise BlockingError(f"variaveis ausentes no .env: {', '.join(ausentes)}")
    log(label, "APROVADO", time.monotonic() - t0)


def gate_conexao_db() -> None:
    label = "[Gate — Conexao DB]"
    t0 = time.monotonic()
    log(label, "verificando...")
    try:
        from src.db.connection import verificar_conexao
        if not verificar_conexao():
            raise RuntimeError("conexao retornou False")
    except BlockingError:
        raise
    except Exception as e:
        raise RuntimeError(f"falha ao conectar: {e}") from e
    log(label, "APROVADO", time.monotonic() - t0)


def gate_schema() -> None:
    label = "[Gate — Schema DB]"
    t0 = time.monotonic()
    log(label, "verificando...")
    try:
        from src.db.connection import criar_schema, verificar_tabelas
        criar_schema()
        tabelas = verificar_tabelas()
        faltando = [t for t, ok in tabelas.items() if not ok]
        if faltando:
            raise RuntimeError(f"tabelas ausentes apos criar_schema: {faltando}")
    except BlockingError:
        raise
    except Exception as e:
        raise RuntimeError(f"erro ao verificar schema: {e}") from e
    log(label, "APROVADO", time.monotonic() - t0)


def gate_anthropic_key() -> None:
    import os
    label = "[Gate — Anthropic API Key]"
    t0 = time.monotonic()
    log(label, "verificando...")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{"role": "user", "content": "ping"}],
        )
    except Exception as e:
        raise RuntimeError(f"API key invalida ou sem acesso: {e}") from e
    log(label, "APROVADO", time.monotonic() - t0)


def main() -> None:
    cabecalho()
    gates_ok = 0
    gates_total = 5

    gates = [
        ("dependencias", gate_dependencias),
        ("variaveis", gate_variaveis_ambiente),
        ("conexao_db", gate_conexao_db),
        ("schema", gate_schema),
        ("anthropic_key", gate_anthropic_key),
    ]

    for nome, fn in gates:
        try:
            fn()
            gates_ok += 1
        except BlockingError as e:
            log(f"[Gate — {nome}]", f"BLOQUEADO — {e}")
            rodape(gates_ok, gates_total)
            sys.exit(2)
        except Exception as e:
            log(f"[Gate — {nome}]", f"FALHOU — {e}")
            rodape(gates_ok, gates_total)
            sys.exit(1)

    rodape(gates_ok, gates_total)
    sys.exit(0)


if __name__ == "__main__":
    main()

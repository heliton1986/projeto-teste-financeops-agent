"""
FinanceOps Agent — Execution Runner

Executa todas as fases com saida narrativa em tempo real.
Uso: python execution/run_flow.py [--fase NUMERO]

Exit codes:
  0 — todas as fases aprovadas
  1 — falha critica
  2 — bloqueio real (requer intervencao humana)
"""
import argparse
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
    print(f"[{ts}] {nivel:<40} {mensagem}{dur}", flush=True)


def cabecalho(titulo: str) -> None:
    print(f"\n{SEPARADOR}", flush=True)
    print(f"  {titulo}", flush=True)
    print(f"{SEPARADOR}\n", flush=True)


def rodape(fases_ok: int, fases_total: int) -> None:
    print(f"\n{SEPARADOR}", flush=True)
    print(f"  Resultado: {fases_ok}/{fases_total} fases aprovadas", flush=True)
    status = "SISTEMA PRONTO" if fases_ok == fases_total else "SISTEMA BLOQUEADO"
    print(f"  {status}", flush=True)
    print(f"{SEPARADOR}\n", flush=True)


class BlockingError(Exception):
    pass


class RunnerNarrativo:
    def __init__(self, nome: str):
        self.nome = nome
        self.fases_ok = 0
        self.fases_total = 0

    def fase(self, numero: int, nome: str):
        return _FaseContext(self, numero, nome)

    def gate(self, nome: str):
        return _GateContext(nome)


class _FaseContext:
    def __init__(self, runner: RunnerNarrativo, numero: int, nome: str):
        self.runner = runner
        self.label = f"[Fase {numero} — {nome}]"
        self._t0 = 0.0

    def __enter__(self):
        self.runner.fases_total += 1
        self._t0 = time.monotonic()
        log(self.label, "iniciando...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        dur = time.monotonic() - self._t0
        if exc_type is None:
            self.runner.fases_ok += 1
            log(self.label, "CONCLUIDA ✓", dur)
        elif exc_type is BlockingError:
            log(self.label, f"BLOQUEADO — {exc_val}")
        else:
            log(self.label, f"FALHOU — {exc_val}", dur)
        return False


class _GateContext:
    def __init__(self, nome: str):
        self.label = f"  [Gate — {nome}]"
        self._t0 = 0.0

    def __enter__(self):
        self._t0 = time.monotonic()
        log(self.label, "verificando...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        dur = time.monotonic() - self._t0
        if exc_type is None:
            log(self.label, "APROVADO ✓", dur)
        else:
            log(self.label, f"FALHOU — {exc_val}", dur)
        return False


# ── Fases ─────────────────────────────────────────────────────────────────────

def fase_1_bootstrap(runner: RunnerNarrativo) -> None:
    with runner.fase(1, "Bootstrap"):
        with _GateContext("Dependencias"):
            import anthropic  # noqa: F401
            import pydantic  # noqa: F401
            import sqlalchemy  # noqa: F401

        with _GateContext("Conexao DB"):
            from src.db.connection import verificar_conexao
            if not verificar_conexao():
                raise RuntimeError("DB inacessivel")

        with _GateContext("Schema"):
            from src.db.connection import verificar_tabelas
            tabelas = verificar_tabelas()
            faltando = [t for t, ok in tabelas.items() if not ok]
            if faltando:
                raise RuntimeError(f"tabelas ausentes: {faltando}")


def _validar_contrato(session, run_id, instancia, nome_agente: str) -> None:
    from src.agents.validator_agent import ValidatorAgent
    from src.db.audit import registrar
    vr = ValidatorAgent().validar_instancia(instancia)
    registrar(session, run_id, "ValidatorAgent", f"validacao_{type(instancia).__name__}",
              "ok" if vr.valido else "falhou", {"erros": vr.erros, "avisos": vr.avisos})
    if not vr.valido:
        raise RuntimeError(f"Contrato {vr.contrato_validado} invalido apos {nome_agente}: {vr.erros}")


def fase_2_ingestao(runner: RunnerNarrativo, csv_path: str, session) -> "LancamentosNormalizados":  # type: ignore
    with runner.fase(2, "Ingestao e Normalizacao"):
        log("  [IngestionAgent]", "lendo CSV...")

        with _GateContext("Lancamentos Normalizados"):
            from src.agents.ingestion_agent import IngestionAgent
            from src.db.audit import registrar
            agent = IngestionAgent()
            resultado = agent.processar(csv_path)
            assert resultado.total_lancamentos > 0, "nenhum lancamento valido"
            registrar(session, resultado.run_id, "IngestionAgent", "ingestao_csv", "ok", {
                "total_lancamentos": resultado.total_lancamentos,
                "erros_ingestao": len(resultado.inconsistencias_ingestao),
                "periodo_inicio": str(resultado.periodo_inicio),
                "periodo_fim": str(resultado.periodo_fim),
            })

        with _GateContext("Validacao Contrato"):
            _validar_contrato(session, resultado.run_id, resultado, "IngestionAgent")

        log("  [IngestionAgent]", f"{resultado.total_lancamentos} lancamentos normalizados")
        return resultado


def fase_3_deteccao(runner: RunnerNarrativo, lancamentos_norm, session) -> "InconsistenciasReport":  # type: ignore
    with runner.fase(3, "Deteccao de Inconsistencias"):
        log("  [DetectorAgent]", "analisando lancamentos com claude-sonnet-4-6...")

        with _GateContext("Inconsistencias Report"):
            from src.agents.detector_agent import DetectorAgent
            from src.db.audit import registrar
            agent = DetectorAgent()
            resultado = agent.detectar(lancamentos_norm)
            assert resultado.total_analisados > 0, "nenhum lancamento analisado"
            registrar(session, lancamentos_norm.run_id, "DetectorAgent", "deteccao_inconsistencias", "ok", {
                "total_analisados": resultado.total_analisados,
                "total_inconsistencias": resultado.total_inconsistencias,
                "tipos": [i.tipo for i in resultado.inconsistencias],
            })

        with _GateContext("Validacao Contrato"):
            _validar_contrato(session, lancamentos_norm.run_id, resultado, "DetectorAgent")

        log("  [DetectorAgent]", f"{resultado.total_inconsistencias} inconsistencias encontradas")
        return resultado


def fase_4_relatorio(runner: RunnerNarrativo, lancamentos_norm, inconsistencias, session) -> "RelatorioExecutivo":  # type: ignore
    with runner.fase(4, "Relatorio Executivo"):
        log("  [ReporterAgent]", "gerando relatorio...")

        with _GateContext("Relatorio Executivo"):
            from src.agents.reporter_agent import ReporterAgent
            from src.db.audit import registrar
            agent = ReporterAgent()
            resultado = agent.gerar(lancamentos_norm, inconsistencias)
            assert resultado.status_sistema != "bloqueado", "relatorio em estado bloqueado"
            registrar(session, lancamentos_norm.run_id, "ReporterAgent", "geracao_relatorio", "ok", {
                "status_sistema": resultado.status_sistema,
                "total_lancamentos": resultado.total_lancamentos,
                "total_inconsistencias": resultado.total_inconsistencias,
            })

        with _GateContext("Validacao Contrato"):
            _validar_contrato(session, lancamentos_norm.run_id, resultado, "ReporterAgent")

        log("  [ReporterAgent]", f"status: {resultado.status_sistema}")
        return resultado


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="FinanceOps Agent — Execution Runner")
    parser.add_argument("--fase", type=int, default=0, help="Executar ate a fase N (0 = todas)")
    parser.add_argument("--csv", type=str, default="tests/fixtures/lancamentos_fixture.csv",
                        help="Caminho do CSV a processar")
    args = parser.parse_args()

    runner = RunnerNarrativo("FinanceOps Agent")
    cabecalho(f"{runner.nome} — Execution Runner")

    fase_max = args.fase or 4

    try:
        fase_1_bootstrap(runner)

        from src.db.connection import get_session
        with get_session() as session:
            lancamentos_norm = None
            inconsistencias = None

            if fase_max >= 2:
                lancamentos_norm = fase_2_ingestao(runner, args.csv, session)

            if fase_max >= 3 and lancamentos_norm:
                inconsistencias = fase_3_deteccao(runner, lancamentos_norm, session)

            if fase_max >= 4 and lancamentos_norm and inconsistencias:
                fase_4_relatorio(runner, lancamentos_norm, inconsistencias, session)

    except BlockingError as e:
        print(f"\n  BLOQUEIO REAL: {e}", flush=True)
        print("  Intervencao humana necessaria antes de continuar.", flush=True)
        rodape(runner.fases_ok, runner.fases_total)
        sys.exit(2)
    except Exception as e:
        print(f"\n  ERRO: {e}", flush=True)
        rodape(runner.fases_ok, runner.fases_total)
        sys.exit(1)

    rodape(runner.fases_ok, runner.fases_total)
    sys.exit(0 if runner.fases_ok == runner.fases_total else 1)


if __name__ == "__main__":
    main()

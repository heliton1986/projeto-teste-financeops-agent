import csv
import uuid
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from contracts.lancamento_contract import InconsistenciaIngestao, Lancamento, LancamentosNormalizados

ORIGENS_VALIDAS = {"csv", "erp"}


class IngestionAgent:
    def processar(self, csv_path: str) -> LancamentosNormalizados:
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV nao encontrado: {csv_path}")

        lancamentos: list[Lancamento] = []
        erros: list[InconsistenciaIngestao] = []
        run_id = uuid.uuid4()

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):
                try:
                    lancamento = self._normalizar(row)
                    lancamentos.append(lancamento)
                except Exception as e:
                    erros.append(InconsistenciaIngestao(
                        linha=i,
                        motivo=str(e),
                        dados_brutos=dict(row),
                    ))

        if not lancamentos:
            raise RuntimeError("Nenhum lancamento valido no CSV")

        datas = [l.data for l in lancamentos]
        return LancamentosNormalizados(
            run_id=run_id,
            total_lancamentos=len(lancamentos),
            periodo_inicio=min(datas),
            periodo_fim=max(datas),
            lancamentos=lancamentos,
            inconsistencias_ingestao=erros,
        )

    def _normalizar(self, row: dict) -> Lancamento:
        campos_obrigatorios = ["data", "descricao", "valor", "categoria", "centro_custo", "origem"]
        ausentes = [c for c in campos_obrigatorios if not row.get(c, "").strip()]
        if ausentes:
            raise ValueError(f"campos ausentes: {', '.join(ausentes)}")

        try:
            data = date.fromisoformat(row["data"].strip())
        except ValueError:
            raise ValueError(f"data invalida: {row['data']}")

        try:
            valor = Decimal(row["valor"].strip())
        except InvalidOperation:
            raise ValueError(f"valor invalido: {row['valor']}")

        origem = row["origem"].strip().lower()
        if origem not in ORIGENS_VALIDAS:
            raise ValueError(f"origem invalida: {origem}")

        return Lancamento(
            data=data,
            descricao=row["descricao"].strip(),
            valor=valor,
            categoria=row["categoria"].strip(),
            centro_custo=row["centro_custo"].strip(),
            origem=origem,
        )

import os
import re
import uuid
from collections import defaultdict
from decimal import Decimal

import anthropic

from contracts.inconsistencia_contract import Inconsistencia, InconsistenciasReport
from contracts.lancamento_contract import Lancamento, LancamentosNormalizados

DESCRICOES_SUSPEITAS = {"teste", "xxx", "n/a", ".", "-", "test"}


def _mascarar_valor(valor: Decimal) -> str:
    abs_val = abs(valor)
    if abs_val < 1000:
        return "< 1k"
    elif abs_val < 10000:
        return "1k-10k"
    elif abs_val < 100000:
        return "10k-100k"
    return "> 100k"


def _mascarar_cpf_cnpj(texto: str) -> str:
    return re.sub(r"\d{3}[.\-]?\d{3}[.\-]?\d{3}[.\-]?\d{2}", "***", texto)


class DetectorAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def detectar(self, resultado: LancamentosNormalizados) -> InconsistenciasReport:
        inconsistencias: list[Inconsistencia] = []

        inconsistencias.extend(self._detectar_duplicatas(resultado.lancamentos))
        inconsistencias.extend(self._detectar_valores_suspeitos(resultado.lancamentos))
        inconsistencias.extend(self._detectar_descricoes_suspeitas(resultado.lancamentos))

        candidatos_semanticos = self._filtrar_para_llm(resultado.lancamentos, inconsistencias)
        if candidatos_semanticos:
            inconsistencias.extend(self._analisar_com_llm(candidatos_semanticos))

        return InconsistenciasReport(
            run_id=resultado.run_id,
            total_analisados=len(resultado.lancamentos),
            total_inconsistencias=len(inconsistencias),
            inconsistencias=inconsistencias,
        )

    def _detectar_duplicatas(self, lancamentos: list[Lancamento]) -> list[Inconsistencia]:
        vistos: defaultdict = defaultdict(list)
        for l in lancamentos:
            chave = (l.data, l.descricao.lower(), l.valor, l.centro_custo)
            vistos[chave].append(l)

        resultado = []
        for grupo in vistos.values():
            if len(grupo) > 1:
                for l in grupo:
                    resultado.append(Inconsistencia(
                        lancamento_id=l.id,
                        tipo="duplicata_suspeita",
                        severidade="critica",
                        descricao=f"Lancamento duplicado: {l.descricao} em {l.data}",
                        valor_mascarado=_mascarar_valor(l.valor),
                    ))
        return resultado

    def _detectar_valores_suspeitos(self, lancamentos: list[Lancamento]) -> list[Inconsistencia]:
        resultado = []
        for l in lancamentos:
            abs_val = abs(l.valor)
            if abs_val > Decimal("100000"):
                resultado.append(Inconsistencia(
                    lancamento_id=l.id,
                    tipo="valor_alto_suspeito",
                    severidade="alta",
                    descricao=f"Valor acima de 100k: {l.descricao}",
                    valor_mascarado=_mascarar_valor(l.valor),
                ))
            elif abs_val < Decimal("0.01") and abs_val > 0:
                resultado.append(Inconsistencia(
                    lancamento_id=l.id,
                    tipo="valor_irrisorio_suspeito",
                    severidade="media",
                    descricao=f"Valor irrisorio: {l.descricao}",
                    valor_mascarado=_mascarar_valor(l.valor),
                ))
        return resultado

    def _detectar_descricoes_suspeitas(self, lancamentos: list[Lancamento]) -> list[Inconsistencia]:
        resultado = []
        for l in lancamentos:
            desc = l.descricao.strip().lower()
            if desc in DESCRICOES_SUSPEITAS or len(desc) < 3:
                resultado.append(Inconsistencia(
                    lancamento_id=l.id,
                    tipo="descricao_suspeita",
                    severidade="media",
                    descricao=f"Descricao generica ou muito curta: '{l.descricao}'",
                    valor_mascarado=_mascarar_valor(l.valor),
                ))
        return resultado

    def _filtrar_para_llm(self, lancamentos: list[Lancamento], ja_detectadas: list[Inconsistencia]) -> list[Lancamento]:
        ids_com_critica = {i.lancamento_id for i in ja_detectadas if i.severidade == "critica"}
        return [l for l in lancamentos if l.id not in ids_com_critica][:20]

    def _analisar_com_llm(self, lancamentos: list[Lancamento]) -> list[Inconsistencia]:
        linhas = []
        for l in lancamentos:
            desc_mascarada = _mascarar_cpf_cnpj(l.descricao)
            linhas.append(
                f"- id:{l.id} | {l.data} | {desc_mascarada} | {_mascarar_valor(l.valor)} | {l.categoria} | {l.centro_custo}"
            )

        prompt = (
            "Analise estes lancamentos financeiros e identifique APENAS inconsistencias semanticas nao obvias "
            "(descricao incompativel com categoria, centro de custo errado, etc). "
            "Responda apenas se tiver confianca alta. Formato: ID|tipo|descricao_curta\n\n"
            + "\n".join(linhas)
        )

        resultado = []
        print(f"[DetectorAgent] LLM chamado com {len(lancamentos)} candidatos", flush=True)
        for tentativa in range(3):
            try:
                response = self.client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=512,
                    temperature=0,
                    messages=[{"role": "user", "content": prompt}],
                )
                texto = response.content[0].text
                print(f"[DetectorAgent] LLM resposta: {texto[:200]!r}", flush=True)
                resultado = self._parsear_resposta_llm(texto, lancamentos)
                break
            except Exception as e:
                print(f"[DetectorAgent] LLM erro tentativa {tentativa+1}: {e}", flush=True)
                if tentativa == 2:
                    pass
        return resultado

    def _parsear_resposta_llm(self, texto: str, lancamentos: list[Lancamento]) -> list[Inconsistencia]:
        ids_map = {str(l.id): l for l in lancamentos}
        resultado = []
        uuid_pattern = re.compile(
            r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\|([^|]+)\|(.+)",
            re.IGNORECASE,
        )
        for linha in texto.strip().splitlines():
            match = uuid_pattern.search(linha)
            if match:
                lid, tipo, descricao = match.group(1), match.group(2).strip(), match.group(3).strip().strip("*`")
                if lid in ids_map:
                    l = ids_map[lid]
                    TIPOS_VALIDOS = {
                        "duplicata_suspeita", "campo_ausente", "formato_invalido",
                        "valor_alto_suspeito", "valor_irrisorio_suspeito",
                        "descricao_suspeita", "centro_custo_desconhecido", "inconsistencia_semantica",
                    }
                    tipo_normalizado = re.sub(r"[^a-zA-Z0-9_]", "_", tipo).strip("_")
                    tipo_limpo = tipo_normalizado if tipo_normalizado in TIPOS_VALIDOS else "inconsistencia_semantica"
                    resultado.append(Inconsistencia(
                        lancamento_id=l.id,
                        tipo=tipo_limpo,
                        severidade="media",
                        descricao=descricao,
                        valor_mascarado=_mascarar_valor(l.valor),
                    ))
        return resultado

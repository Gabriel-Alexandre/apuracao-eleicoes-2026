"""Caminhos e utilitarios de saida dos resultados (CSV, figuras e o resumo em JSON)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RES = Path(os.environ.get("APURACAO_RESULTADOS", RAIZ / "resultados"))
FIG = RES / "figuras"
RESUMO = RES / "RESUMO.json"


def preparar() -> None:
    RES.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)


def csv(df: pd.DataFrame, nome: str, indice: bool = False) -> Path:
    preparar()
    p = RES / nome
    df.to_csv(p, index=indice, float_format="%.4f", encoding="utf-8")
    return p


def _plano(x):
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return None if np.isnan(x) else float(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, (pd.Timestamp,)):
        return x.isoformat()
    if isinstance(x, dict):
        return {str(k): _plano(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plano(v) for v in x]
    if isinstance(x, float) and np.isnan(x):
        return None
    return x


def anotar(chave: str, valor) -> None:
    """Grava um resultado no RESUMO.json. O relatorio so cita numero que esta aqui."""
    preparar()
    dado = json.loads(RESUMO.read_text(encoding="utf-8")) if RESUMO.exists() else {}
    dado[chave] = _plano(valor)
    RESUMO.write_text(json.dumps(dado, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")


def ler(chave: str):
    return json.loads(RESUMO.read_text(encoding="utf-8"))[chave]

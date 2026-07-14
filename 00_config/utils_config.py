"""Cargador de configuracion compartido por todo el pipeline CacaoIA.
Todos los scripts hacen: from utils_config import CFG, ruta_salida
"""
from pathlib import Path
import yaml

_THIS = Path(__file__).resolve()
_CONFIG_PATH = _THIS.parent / "config_cacao.yaml"

with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)


def ruta_salida(*partes) -> Path:
    """Devuelve una ruta dentro de 07_Pipeline_CacaoIA, creando carpetas padre."""
    base = Path(CFG["proyecto"]["salida"])
    p = base.joinpath(*partes)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def nombre_clase(idx: int) -> str:
    return CFG["clases"].get(int(idx), f"clase_{idx}")

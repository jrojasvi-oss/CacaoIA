"""ORQUESTADOR - Corre el pipeline CacaoIA en orden y encadena los handoffs.
Cada paso escribe su resultado como JSON en _handoffs/, de modo que los pasos (y
los agentes) se comunican por archivo y no re-procesan lo ya hecho.

Uso:
  python ejecutar_pipeline.py            # pipeline completo
  python ejecutar_pipeline.py --seg 20   # segmenta solo 20 imgs (prueba rapida)
  python ejecutar_pipeline.py --solo color   # solo paso de color+paletas
"""
import sys, subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
PASOS = [
    ("Segmentacion (YOLO+SAM)",      "01_motor_dinov2/paso1_segmentar.py"),
    ("Embeddings DINOv2",            "01_motor_dinov2/paso2_embeddings_dinov2.py"),
    ("Identificacion (PCA+cluster)", "01_motor_dinov2/paso3_identificar.py"),
    ("Embeddings de color",          "02_color_embeddings/color_embeddings_cacao.py"),
    ("Paletas por objeto (>=30)",    "02_color_embeddings/paleta_por_objeto.py"),
    ("Montajes 1x30",                "02_color_embeddings/montaje_1x30.py"),
    ("Reporte consolidado",          "04_reportes/generar_reporte.py"),
]


def correr(script, extra=None):
    cmd = [sys.executable, str(BASE / script)] + (extra or [])
    print(f"\n{'='*60}\n>>> {script}\n{'='*60}")
    return subprocess.run(cmd).returncode == 0


def main():
    args = sys.argv[1:]
    seg_extra = []
    if "--seg" in args:
        seg_extra = [args[args.index("--seg") + 1]]
    if "--solo" in args:
        clave = args[args.index("--solo") + 1].lower()
        pasos = [(n, s) for n, s in PASOS if clave in n.lower() or clave in s.lower()]
    else:
        pasos = PASOS

    for nombre, script in pasos:
        extra = seg_extra if "paso1_segmentar" in script else None
        if not correr(script, extra):
            print(f"[!] Fallo en: {nombre}. Revisa el error arriba.")
            break
    print("\n[FIN] Pipeline terminado. Revisa 07_Pipeline_CacaoIA/04_reportes/ y _handoffs/")


if __name__ == "__main__":
    main()

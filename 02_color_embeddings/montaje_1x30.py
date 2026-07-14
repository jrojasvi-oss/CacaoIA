"""MONTAJE 1x30 - Una tira horizontal con 30 imagenes
Genera, por clase con >=30 recortes, una figura 1x30 (una sola fila) con las 30
muestras y debajo la franja de color promedio de cada una. Util para inspeccion
visual del gradiente de pigmentacion (antocianina) dentro de un mismo objeto.

Uso:  python montaje_1x30.py [clase]   (sin arg = todas las clases que cumplan)
"""
import sys
from pathlib import Path
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_config"))
from utils_config import CFG, ruta_salida  # noqa: E402

MIN_IMG = CFG["paletas"]["min_imagenes_por_objeto"]


def montaje_clase(clase_dir, out_dir):
    imgs = sorted(clase_dir.glob("*.png"))[:MIN_IMG]
    if len(imgs) < MIN_IMG:
        print(f"   [skip] {clase_dir.name}: solo {len(imgs)}/{MIN_IMG}")
        return False

    fig, axes = plt.subplots(2, 30, figsize=(30, 2.6),
                             gridspec_kw={"height_ratios": [3, 1], "hspace": 0.05, "wspace": 0.05})
    for j, p in enumerate(imgs):
        im = cv2.imread(str(p))
        rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        axes[0, j].imshow(cv2.resize(rgb, (80, 80))); axes[0, j].axis("off")
        m = np.any(rgb > 8, axis=2)
        prom = rgb[m].mean(axis=0)/255 if m.sum() > 0 else np.zeros(3)
        axes[1, j].add_patch(plt.Rectangle((0, 0), 1, 1, color=prom))
        axes[1, j].set_xlim(0, 1); axes[1, j].set_ylim(0, 1); axes[1, j].axis("off")
    plt.suptitle(f"Montaje 1x30 - {clase_dir.name}  (imagen + color promedio)", fontweight="bold", y=1.02)
    out = out_dir / f"{clase_dir.name}_montaje_1x30.png"
    plt.savefig(out, dpi=110, bbox_inches="tight"); plt.close()
    print(f"   [OK] {clase_dir.name} -> {out.name}")
    return True


def main(clase=None):
    recortes_dir = ruta_salida("_derivados", "recortes", "_.tmp").parent
    if not recortes_dir.exists():
        print("[!] No hay recortes. Corre 01_motor_dinov2/paso1_segmentar.py primero."); return
    out_dir = ruta_salida("02_color_embeddings", "montajes_1x30", "_.tmp").parent

    dirs = [recortes_dir / clase] if clase else [d for d in sorted(recortes_dir.iterdir()) if d.is_dir()]
    n = sum(montaje_clase(d, out_dir) for d in dirs if d.exists())
    print(f"[OK] {n} montajes 1x30 generados en {out_dir}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

"""PALETA DE COLOR POR OBJETO (minimo 30 imagenes por objeto/clase)
Para cada clase con >= 30 recortes, extrae los colores dominantes (KMeans sobre
pixeles no-fondo de las imagenes) y genera:
  - <clase>_paleta.png     : barra de N colores dominantes con codigo HEX
  - <clase>_muestras.png    : mosaico de las 30 imagenes usadas
Si una clase tiene menos de 30, se avisa (no cumple el minimo exigido).
"""
import sys, json, datetime, colorsys
from pathlib import Path
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_config"))
from utils_config import CFG, ruta_salida  # noqa: E402

MIN_IMG = CFG["paletas"]["min_imagenes_por_objeto"]
N_COL = CFG["paletas"]["n_colores_dominantes"]


def colores_dominantes(pixeles, k):
    km = KMeans(n_clusters=k, random_state=42, n_init="auto").fit(pixeles)
    centros = km.cluster_centers_.astype(int)
    pesos = np.bincount(km.labels_, minlength=k) / len(km.labels_)
    orden = np.argsort(-pesos)
    return centros[orden], pesos[orden]


def hex_rgb(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def procesar_clase(clase_dir, out_dir):
    imgs = sorted(clase_dir.glob("*.png"))
    if len(imgs) < MIN_IMG:
        return {"clase": clase_dir.name, "n_imagenes": len(imgs), "cumple_min": False}

    usar = imgs[:MIN_IMG]
    pix_all, thumbs = [], []
    for p in usar:
        im = cv2.imread(str(p))
        if im is None:
            continue
        rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        m = np.any(rgb > 8, axis=2)
        px = rgb[m]
        if len(px) > 0:
            idx = np.random.choice(len(px), min(400, len(px)), replace=False)
            pix_all.append(px[idx])
        thumbs.append(cv2.resize(rgb, (96, 96)))

    if not pix_all:
        return {"clase": clase_dir.name, "n_imagenes": len(imgs), "cumple_min": False}
    pix_all = np.vstack(pix_all)
    centros, pesos = colores_dominantes(pix_all, N_COL)

    # --- Paleta ---
    fig, ax = plt.subplots(figsize=(N_COL * 1.6, 2.4))
    x = 0
    for c, w in zip(centros, pesos):
        ax.add_patch(plt.Rectangle((x, 0), w, 1, color=np.array(c)/255))
        ax.text(x + w/2, 0.5, hex_rgb(c), ha="center", va="center",
                fontsize=8, color="white" if np.mean(c) < 128 else "black", fontweight="bold")
        x += w
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title(f"Paleta dominante - {clase_dir.name} (n={MIN_IMG} imgs)", fontweight="bold")
    plt.tight_layout()
    plt.savefig(out_dir / f"{clase_dir.name}_paleta.png", dpi=150, bbox_inches="tight"); plt.close()

    # --- Mosaico de muestras (5 x 6 = 30) ---
    fig, axes = plt.subplots(5, 6, figsize=(12, 10))
    for ax, th in zip(axes.flat, thumbs):
        ax.imshow(th); ax.axis("off")
    for ax in axes.flat[len(thumbs):]:
        ax.axis("off")
    plt.suptitle(f"30 muestras - {clase_dir.name}", fontweight="bold")
    plt.tight_layout()
    plt.savefig(out_dir / f"{clase_dir.name}_muestras.png", dpi=120, bbox_inches="tight"); plt.close()

    return {"clase": clase_dir.name, "n_imagenes": len(imgs), "cumple_min": True,
            "colores_hex": [hex_rgb(c) for c in centros],
            "pesos": [round(float(w), 3) for w in pesos]}


def main():
    recortes_dir = ruta_salida("_derivados", "recortes", "_.tmp").parent
    if not recortes_dir.exists():
        print("[!] No hay recortes. Corre 01_motor_dinov2/paso1_segmentar.py primero."); return
    out_dir = ruta_salida("02_color_embeddings", "paletas", "_.tmp").parent

    resultados = []
    for clase_dir in sorted(recortes_dir.iterdir()):
        if clase_dir.is_dir():
            resultados.append(procesar_clase(clase_dir, out_dir))

    with open(ruta_salida("_handoffs", "paletas.json"), "w", encoding="utf-8") as f:
        json.dump({"generado": datetime.datetime.now().isoformat(timespec="seconds"),
                   "min_exigido": MIN_IMG, "resultados": resultados}, f, indent=2, ensure_ascii=False)
    ok = [r for r in resultados if r.get("cumple_min")]
    print(f"[OK] Paletas generadas para {len(ok)}/{len(resultados)} clases (>= {MIN_IMG} imgs).")
    for r in resultados:
        estado = "OK" if r.get("cumple_min") else f"FALTAN ({r['n_imagenes']}/{MIN_IMG})"
        print(f"   - {r['clase']}: {estado}")


if __name__ == "__main__":
    main()

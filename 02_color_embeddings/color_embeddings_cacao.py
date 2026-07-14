"""LOGICA DE COLOR - Identificar hoja de cacao por cambios en el embedding de color
La pigmentacion antocianica del brote (verde -> rojizo -> violaceo) es un descriptor
varietal altamente heredable (UPOV C1). Este modulo construye un "embedding de color"
por objeto segmentado y mide como cambia entre clases/variedades.

Embedding de color por objeto (vector interpretable, no caja negra):
  - Histograma HSV (H:16 + S:8 + V:8 bins)  -> distribucion de matiz/saturacion
  - Estadisticos Lab (media a*, b*)          -> eje rojo-verde / azul-amarillo
  - NGRDI = (G-R)/(G+R)                        -> indice de verdor
  - RGBVI = (G^2 - R*B)/(G^2 + R*B)            -> vigor foliar
  - Ratio antocianina = R/(R+G)                -> proxy de pigmentacion roja [0,1]

Salida: catalogo_color.csv (una fila por objeto) + color_embeddings.npy
"""
import sys, json, datetime
from pathlib import Path
import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_config"))
from utils_config import ruta_salida  # noqa: E402


def embedding_color(img_bgr):
    """Devuelve un vector de color interpretable a partir de pixeles NO negros
    (los recortes segmentados tienen fondo negro por SAM)."""
    mask = np.any(img_bgr > 8, axis=2)
    if mask.sum() < 30:
        return None
    b, g, r = [img_bgr[:, :, i][mask].astype(np.float32) for i in range(3)]
    eps = 1e-6

    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h_hist = cv2.calcHist([hsv], [0], mask.astype(np.uint8), [16], [0, 180]).flatten()
    s_hist = cv2.calcHist([hsv], [1], mask.astype(np.uint8), [8], [0, 256]).flatten()
    v_hist = cv2.calcHist([hsv], [2], mask.astype(np.uint8), [8], [0, 256]).flatten()
    h_hist /= (h_hist.sum() + eps); s_hist /= (s_hist.sum() + eps); v_hist /= (v_hist.sum() + eps)

    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    a_mean = float(lab[:, :, 1][mask].mean())
    bb_mean = float(lab[:, :, 2][mask].mean())

    ngrdi = float(np.mean((g - r) / (g + r + eps)))
    rgbvi = float(np.mean((g**2 - r*b) / (g**2 + r*b + eps)))
    # Proxy de pigmentacion roja acotado a [0,1]: R / (R+G). Estable aunque G~0.
    antocianina = float(np.mean(r / (r + g + eps)))

    return np.concatenate([h_hist, s_hist, v_hist,
                           [a_mean/255, bb_mean/255, ngrdi, rgbvi, antocianina]]).astype(np.float32)


def main():
    recortes_dir = ruta_salida("_derivados", "recortes", "_.tmp").parent
    if not recortes_dir.exists():
        print("[!] No hay recortes. Corre 01_motor_dinov2/paso1_segmentar.py primero."); return

    filas, vecs = [], []
    for clase_dir in sorted(recortes_dir.iterdir()):
        if not clase_dir.is_dir():
            continue
        for p in sorted(clase_dir.glob("*.png")):
            img = cv2.imread(str(p))
            if img is None:
                continue
            v = embedding_color(img)
            if v is None:
                continue
            vecs.append(v)
            filas.append({"clase": clase_dir.name, "archivo": p.name,
                          "ngrdi": round(float(v[-3]), 4), "rgbvi": round(float(v[-2]), 4),
                          "antocianina": round(float(v[-1]), 4)})

    if not vecs:
        print("[!] Sin objetos validos."); return
    vecs = np.array(vecs)
    np.save(ruta_salida("02_color_embeddings", "salidas", "color_embeddings.npy"), vecs)

    import csv
    with open(ruta_salida("02_color_embeddings", "salidas", "catalogo_color.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["clase", "archivo", "ngrdi", "rgbvi", "antocianina"])
        w.writeheader(); w.writerows(filas)

    # Resumen por clase (promedios de indices de color)
    import pandas as pd
    df = pd.DataFrame(filas)
    resumen = df.groupby("clase")[["ngrdi", "rgbvi", "antocianina"]].mean().round(4)
    with open(ruta_salida("_handoffs", "color.json"), "w", encoding="utf-8") as f:
        json.dump({"generado": datetime.datetime.now().isoformat(timespec="seconds"),
                   "n_objetos": len(filas), "dim_embedding": int(vecs.shape[1]),
                   "promedios_por_clase": resumen.to_dict("index")}, f, indent=2, ensure_ascii=False)
    print(f"[OK] {len(filas)} embeddings de color (dim={vecs.shape[1]}).")
    print(resumen)


if __name__ == "__main__":
    main()

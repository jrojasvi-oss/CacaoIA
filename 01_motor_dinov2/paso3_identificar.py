"""PASO 3 - IDENTIFICACION (PCA + clustering sobre embeddings DINOv2)
Reduce los embeddings, los agrupa (KMeans) y evalua que tan bien se separan las
clases/variedades de hoja. Produce la grafica PCA y un JSON con metricas
(silueta, varianza explicada, matriz clase-vs-cluster).

Este es el nucleo de la logica de "identificar" del proyecto: mide si la
huella DINOv2 discrimina las hojas de cacao.
"""
import sys, json, datetime
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_config"))
from utils_config import ruta_salida  # noqa: E402

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def main():
    tensores_dir = ruta_salida("_derivados", "embeddings", "_.tmp").parent
    cat_path = tensores_dir / "catalogo_embeddings.csv"
    if not cat_path.exists():
        print("[!] Falta catalogo. Corre paso2_embeddings_dinov2.py primero.")
        return

    df = pd.read_csv(cat_path)
    X, y = [], []
    for _, r in df.iterrows():
        p = tensores_dir / r["embedding"]
        if p.exists():
            X.append(np.load(p)); y.append(r["clase"])
    if len(X) < 3:
        print("[!] Muy pocos embeddings para identificar."); return
    X = np.array(X); y = np.array(y)

    pca = PCA(n_components=min(10, X.shape[0], X.shape[1]))
    Xp = pca.fit_transform(X)
    var = pca.explained_variance_ratio_

    n_clusters = max(2, min(len(np.unique(y)), len(X) - 1))
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    clusters = km.fit_predict(X)
    sil = float(silhouette_score(X, clusters)) if len(X) > n_clusters else 0.0
    ct = pd.crosstab(y, clusters)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 6))
    for cl in np.unique(y):
        m = y == cl
        a1.scatter(Xp[m, 0], Xp[m, 1], s=60, alpha=0.8, edgecolors="black", label=cl)
    a1.set_title("PCA embeddings DINOv2 por clase (identificacion)", fontweight="bold")
    a1.set_xlabel(f"PC1 ({var[0]*100:.1f}%)"); a1.set_ylabel(f"PC2 ({var[1]*100:.1f}%)")
    a1.legend(fontsize=8)
    a2.scatter(Xp[:, 0], Xp[:, 1], c=clusters, cmap="plasma", s=60, alpha=0.85, edgecolors="black")
    a2.set_title(f"Clustering KMeans (silueta={sil:.3f})", fontweight="bold")
    a2.set_xlabel(f"PC1 ({var[0]*100:.1f}%)"); a2.set_ylabel(f"PC2 ({var[1]*100:.1f}%)")
    plt.suptitle("CacaoIA - Identificacion por representacion DINOv2", fontweight="bold")
    plt.tight_layout()
    fig_path = ruta_salida("04_reportes", "identificacion_pca_dinov2.png")
    plt.savefig(fig_path, dpi=160, bbox_inches="tight"); plt.close()

    motor = {
        "generado": datetime.datetime.now().isoformat(timespec="seconds"),
        "n_muestras": int(len(X)), "dim": int(X.shape[1]),
        "var_explicada_2d": float(sum(var[:2])), "silueta_kmeans": sil,
        "n_clusters": int(n_clusters), "clases": list(map(str, np.unique(y))),
        "matriz_clase_cluster": ct.to_dict(), "grafica": str(fig_path),
    }
    with open(ruta_salida("_handoffs", "motor.json"), "w", encoding="utf-8") as f:
        json.dump(motor, f, indent=2, ensure_ascii=False)
    print(f"[OK] Identificacion lista. Silueta={sil:.3f}  Var2D={sum(var[:2])*100:.1f}%")
    print(f"     Grafica -> {fig_path}")


if __name__ == "__main__":
    main()

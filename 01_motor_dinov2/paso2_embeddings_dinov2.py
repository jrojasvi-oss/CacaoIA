"""PASO 2 - EMBEDDINGS DINOv2 (representacion / identificacion)
Toma los recortes del paso1 y extrae el vector de representacion DINOv2 de cada
objeto. Estos embeddings son la "huella" para identificar hojas/variedades sin
necesidad de re-entrenar. Guarda un catalogo + tensores .npy.

Motor: Meta DINOv2 (torch.hub). Modelo por defecto vits14 (384-dim, corre en CPU).
"""
import sys, json, datetime
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_config"))
from utils_config import CFG, ruta_salida  # noqa: E402

import torch
from PIL import Image
import torchvision.transforms as T

_TF = T.Compose([
    T.Resize(256), T.CenterCrop(224), T.ToTensor(),
    T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
])


def cargar_dinov2():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = torch.hub.load("facebookresearch/dinov2", CFG["modelos"]["dinov2"])
    model.eval().to(device)
    return model, device


def main():
    recortes_dir = ruta_salida("_derivados", "recortes").parent / "recortes"
    if not recortes_dir.exists():
        print("[!] No hay recortes. Corre paso1_segmentar.py primero.")
        return

    model, device = cargar_dinov2()
    tensores_dir = ruta_salida("_derivados", "embeddings", "_.tmp").parent
    catalogo = []

    for clase_dir in sorted(recortes_dir.iterdir()):
        if not clase_dir.is_dir():
            continue
        for img_path in sorted(clase_dir.glob("*.png")):
            try:
                img = Image.open(img_path).convert("RGB")
                x = _TF(img).unsqueeze(0).to(device)
                with torch.no_grad():
                    emb = model(x).squeeze(0).cpu().numpy().astype(np.float32)
            except Exception as e:
                print(f"  [skip] {img_path.name}: {e}")
                continue
            npy = tensores_dir / clase_dir.name / f"{img_path.stem}.npy"
            npy.parent.mkdir(parents=True, exist_ok=True)
            np.save(npy, emb)
            catalogo.append({"clase": clase_dir.name, "archivo": img_path.name,
                             "embedding": str(npy.relative_to(tensores_dir)), "dim": int(emb.shape[0])})

    import csv
    cat_path = tensores_dir / "catalogo_embeddings.csv"
    with open(cat_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["clase", "archivo", "embedding", "dim"])
        w.writeheader(); w.writerows(catalogo)

    with open(ruta_salida("_handoffs", "embeddings.json"), "w", encoding="utf-8") as f:
        json.dump({"generado": datetime.datetime.now().isoformat(timespec="seconds"),
                   "modelo": CFG["modelos"]["dinov2"], "n_embeddings": len(catalogo),
                   "catalogo": str(cat_path)}, f, indent=2, ensure_ascii=False)
    print(f"[OK] {len(catalogo)} embeddings DINOv2 -> {cat_path}")


if __name__ == "__main__":
    main()

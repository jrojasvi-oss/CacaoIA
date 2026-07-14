"""PASO 1 - SEGMENTACION
YOLO (best.pt) detecta objetos de cacao -> SAM refina la mascara -> se recortan
los objetos y se guardan agrupados por clase. Alimenta a paso2 (embeddings) y a
las paletas de color.

Entrada:  dataset de imagenes (config_cacao.yaml)
Salida:   07_Pipeline_CacaoIA/_derivados/recortes/<clase>/<img>_<n>.png
          07_Pipeline_CacaoIA/_handoffs/segmentacion.json
"""
import sys, os, json, datetime
from pathlib import Path
import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_config"))
from utils_config import CFG, ruta_salida, nombre_clase  # noqa: E402

from ultralytics import YOLO
try:
    from ultralytics import SAM
    _HAY_SAM = True
except Exception:
    _HAY_SAM = False


def boxes_desde_etiqueta(img_path, w, h):
    """Fallback: si YOLO no detecta, lee el .txt YOLO (polígono o bbox) y devuelve
    (boxes[x1,y1,x2,y2], clases). Soporta segmentacion (clase + pares x y)."""
    label_dir = Path(CFG["dataset"]["labels"])
    lab = label_dir / (Path(img_path).stem + ".txt")
    if not lab.exists():
        return None, None
    boxes, clases = [], []
    for line in lab.read_text().splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        cls = int(float(parts[0]))
        vals = list(map(float, parts[1:]))
        if len(vals) == 4:  # bbox cx,cy,bw,bh normalizado
            cx, cy, bw, bh = vals
            x1, y1 = (cx - bw/2) * w, (cy - bh/2) * h
            x2, y2 = (cx + bw/2) * w, (cy + bh/2) * h
        else:               # poligono: pares x y
            xs, ys = vals[0::2], vals[1::2]
            x1, x2 = min(xs) * w, max(xs) * w
            y1, y2 = min(ys) * h, max(ys) * h
        if (x2 - x1) > 10 and (y2 - y1) > 10:
            boxes.append([int(x1), int(y1), int(x2), int(y2)])
            clases.append(cls)
    if not boxes:
        return None, None
    return np.array(boxes), np.array(clases)


def main(limite=None):
    modelo = YOLO(CFG["modelos"]["yolo_best"])
    sam = SAM(CFG["modelos"]["sam"]) if _HAY_SAM else None
    conf = CFG["modelos"]["yolo_conf"]

    img_dir = Path(CFG["dataset"]["imagenes"])
    imagenes = sorted([p for p in img_dir.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")])
    if limite:
        imagenes = imagenes[:limite]

    conteo = {}
    total = 0
    for img_path in imagenes:
        img_bgr = cv2.imread(str(img_path))
        if img_bgr is None:
            continue
        h, w = img_bgr.shape[:2]
        res = modelo.predict(img_bgr, conf=conf, verbose=False)[0]
        if res.boxes is not None and len(res.boxes) > 0:
            boxes = res.boxes.xyxy.cpu().numpy().astype(int)
            clases = res.boxes.cls.cpu().numpy().astype(int)
        else:
            # Fallback a etiquetas ground-truth (YOLO no detecto)
            boxes, clases = boxes_desde_etiqueta(img_path, w, h)
            if boxes is None:
                continue

        for i, (box, cls) in enumerate(zip(boxes, clases)):
            x1, y1, x2, y2 = box
            x1, y1 = max(0, x1), max(0, y1)
            recorte = img_bgr[y1:y2, x1:x2]
            if recorte.size == 0 or recorte.shape[0] < 12 or recorte.shape[1] < 12:
                continue

            # Refinar con SAM usando el bbox como prompt (mascara -> fondo negro)
            if sam is not None:
                try:
                    m = sam.predict(img_bgr, bboxes=[[x1, y1, x2, y2]], verbose=False)[0]
                    mask = m.masks.data[0].cpu().numpy().astype(np.uint8)[y1:y2, x1:x2]
                    if mask.shape[:2] == recorte.shape[:2]:
                        recorte = cv2.bitwise_and(recorte, recorte, mask=mask)
                except Exception:
                    pass  # si SAM falla, se usa el recorte rectangular

            clase = nombre_clase(cls)
            destino = ruta_salida("_derivados", "recortes", clase, f"{img_path.stem}_{i}.png")
            cv2.imwrite(str(destino), recorte)
            conteo[clase] = conteo.get(clase, 0) + 1
            total += 1

    handoff = {
        "generado": datetime.datetime.now().isoformat(timespec="seconds"),
        "sam_activo": _HAY_SAM,
        "total_recortes": total,
        "por_clase": conteo,
    }
    with open(ruta_salida("_handoffs", "segmentacion.json"), "w", encoding="utf-8") as f:
        json.dump(handoff, f, indent=2, ensure_ascii=False)
    print(f"[OK] {total} recortes segmentados. SAM={'si' if _HAY_SAM else 'no'}")
    print(json.dumps(conteo, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(lim)

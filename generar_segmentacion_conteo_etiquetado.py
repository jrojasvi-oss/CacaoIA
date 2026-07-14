"""Genera las GRAFICAS DE SALIDA del pipeline (YOLO -> SAM):
  - Segmentacion hoja por hoja (mascara SAM por objeto, cada una de un color)
  - Conteo de hojas (total + por clase, sobre la imagen)
  - Etiquetado (caja + nombre de la clase en cada hoja)

Un panel 1x3 por imagen + las tres versiones sueltas, en JPG dentro de
Graficas_CacaoIA/04_Segmentacion_Conteo_Etiquetado/
"""
import sys
from pathlib import Path
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ultralytics import YOLO, SAM

PROY = Path("C:/Users/juanv/Desktop/PROYECTO_CACAO_IA")
SAM_MODEL = PROY / "07_Pipeline_CacaoIA/sam_b.pt"
GRAF = Path("C:/Users/juanv/Desktop/Graficas_CacaoIA")

# Casos disponibles: (modelo YOLO, carpeta de imagenes, subcarpeta destino, conf)
CASOS = {
    "frutos_enfermos": (
        PROY / "05_Datasets_Consolidados/Dataset_3_Clases_Enfermedades/runs/detect/train_robusto/weights/best.pt",
        PROY / "05_Datasets_Consolidados/Dataset_3_Clases_Enfermedades/test/images",
        "04_Frutos_Enfermos_Seg_Etiquetado", 0.25),
    "hojas": (
        PROY / "02_Motor_Entrenamiento/runs_entrenamiento/cacao_9clases_v1/weights/best.pt",
        PROY / "05_Datasets_Consolidados/Dataset_9_Clases/test/images",
        "05_Hojas_Seg_Etiquetado", 0.10),
}

PALETA = [(230, 60, 60), (60, 200, 60), (60, 120, 240), (240, 180, 40),
          (200, 60, 200), (40, 200, 200), (240, 120, 40), (140, 100, 220)]


def main(caso="frutos_enfermos", n=6):
    det_path, imgs_dir, subdest, conf = CASOS[caso]
    if not Path(det_path).exists():
        # fallback al modelo de prueba de 9 clases si el completo no existe
        alt = PROY / "02_Motor_Entrenamiento/runs_entrenamiento/cacao_9clases_TEST/weights/best.pt"
        if caso == "hojas" and alt.exists():
            det_path = alt
            print(f"[i] Modelo 9clases_v1 no existe; uso el de PRUEBA: {alt.name}")
        else:
            print(f"[!] No existe el modelo {det_path}"); return
    DEST = GRAF / subdest
    DEST.mkdir(parents=True, exist_ok=True)
    det = YOLO(str(det_path))
    sam = SAM(str(SAM_MODEL))
    names = det.names

    imgs = [p for p in Path(imgs_dir).glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")][:n]
    for p in imgs:
        img = cv2.imread(str(p))
        if img is None:
            continue
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        r = det.predict(img, conf=conf, verbose=False)[0]
        if r.boxes is None or len(r.boxes) == 0:
            continue
        boxes = r.boxes.xyxy.cpu().numpy()
        clases = [int(c) for c in r.boxes.cls.cpu().numpy()]
        confs = r.boxes.conf.cpu().numpy()

        # --- SAM: mascara por caja ---
        seg = rgb.copy()
        try:
            sres = sam.predict(img, bboxes=boxes.tolist(), verbose=False)[0]
            masks = sres.masks.data.cpu().numpy() if sres.masks is not None else []
        except Exception:
            masks = []
        for i, m in enumerate(masks):
            color = PALETA[i % len(PALETA)]
            mm = cv2.resize(m.astype(np.uint8), (seg.shape[1], seg.shape[0])) > 0
            seg[mm] = (0.5 * seg[mm] + 0.5 * np.array(color)).astype(np.uint8)
            # contorno grueso para que cada hoja se vea nitida
            cnts, _ = cv2.findContours(mm.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(seg, cnts, -1, color, 4)
            cv2.drawContours(seg, cnts, -1, (255, 255, 255), 1)

        # --- Etiquetado: caja + nombre ---
        etq = rgb.copy()
        conteo = {}
        for i, (b, c, cf) in enumerate(zip(boxes, clases, confs)):
            x1, y1, x2, y2 = map(int, b)
            color = PALETA[i % len(PALETA)]
            cv2.rectangle(etq, (x1, y1), (x2, y2), color, 3)
            txt = f"{names[c]} {cf:.0%}"
            (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(etq, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
            cv2.putText(etq, txt, (x1 + 2, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            conteo[names[c]] = conteo.get(names[c], 0) + 1

        # --- Conteo: overlay resumen ---
        cont = rgb.copy()
        y = 34
        cv2.rectangle(cont, (0, 0), (cont.shape[1], 44 + 26 * len(conteo)), (0, 0, 0), -1)
        cv2.putText(cont, f"Total detectado: {len(boxes)}", (12, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        for cl, num in conteo.items():
            y += 26
            cv2.putText(cont, f"  {cl}: {num}", (12, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (120, 240, 120), 2)

        # guardar sueltas
        for arr, tag in [(seg, "segmentacion"), (etq, "etiquetado"), (cont, "conteo")]:
            cv2.imwrite(str(DEST / f"{tag}__{p.stem[:26]}.jpg"),
                        cv2.cvtColor(arr, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])

        # panel 1x3
        fig, ax = plt.subplots(1, 3, figsize=(15, 5.2))
        for a in ax: a.axis("off")
        ax[0].imshow(seg);  ax[0].set_title(f"Segmentacion SAM ({len(masks)} hojas)", fontsize=11)
        ax[1].imshow(etq);  ax[1].set_title("Etiquetado (clase + confianza)", fontsize=11)
        ax[2].imshow(cont); ax[2].set_title(f"Conteo ({len(boxes)} objetos)", fontsize=11)
        plt.suptitle(f"Pipeline YOLO->SAM: {p.name}", fontweight="bold")
        plt.tight_layout()
        plt.savefig(DEST / f"panel__{p.stem[:26]}.jpg", dpi=120)
        plt.close()
        print(f"  [OK] {p.name}: {len(boxes)} obj, {len(masks)} mascaras")

    print(f"[FIN] Graficas en {DEST}")


if __name__ == "__main__":
    # uso: python ...py [caso] [n]   caso = frutos_enfermos | hojas | todos
    caso = sys.argv[1] if len(sys.argv) > 1 else "todos"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    casos = ["frutos_enfermos", "hojas"] if caso == "todos" else [caso]
    for c in casos:
        print(f"\n=== CASO: {c} ===")
        main(c, n)

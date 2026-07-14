"""PASO 4 - ETIQUETADO AUTOMATICO
Corre YOLO (best.pt) sobre una carpeta de imagenes y genera etiquetas en formato
YOLO (.txt normalizado) + una previsualizacion con cajas. Sirve para pre-etiquetar
fotos nuevas de campo antes de la correccion manual en el panel.

Uso:  python paso4_etiquetar.py <carpeta_imagenes> [conf]
"""
import sys, json, datetime
from pathlib import Path
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_config"))
from utils_config import CFG, ruta_salida, nombre_clase  # noqa: E402
from ultralytics import YOLO


def main(carpeta, conf=None):
    conf = float(conf) if conf else CFG["modelos"]["yolo_conf"]
    modelo = YOLO(CFG["modelos"]["yolo_best"])
    img_dir = Path(carpeta)
    imgs = [p for p in img_dir.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")]

    out_lab = ruta_salida("_derivados", "etiquetas_auto", "labels", "_.tmp").parent
    out_prev = ruta_salida("_derivados", "etiquetas_auto", "preview", "_.tmp").parent
    resumen = {"imagenes": 0, "detecciones": 0, "por_clase": {}}

    for p in imgs:
        img = cv2.imread(str(p))
        if img is None:
            continue
        h, w = img.shape[:2]
        res = modelo.predict(img, conf=conf, verbose=False)[0]
        lineas, vis = [], img.copy()
        if res.boxes is not None:
            for box, cls, cf in zip(res.boxes.xyxy.cpu().numpy(),
                                    res.boxes.cls.cpu().numpy().astype(int),
                                    res.boxes.conf.cpu().numpy()):
                x1, y1, x2, y2 = box
                cx, cy, bw, bh = ((x1+x2)/2/w, (y1+y2)/2/h, (x2-x1)/w, (y2-y1)/h)
                lineas.append(f"{cls} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
                cv2.rectangle(vis, (int(x1), int(y1)), (int(x2), int(y2)), (0, 200, 0), 2)
                cv2.putText(vis, f"{nombre_clase(cls)} {cf:.2f}", (int(x1), int(y1)-6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 2)
                c = nombre_clase(cls)
                resumen["por_clase"][c] = resumen["por_clase"].get(c, 0) + 1
                resumen["detecciones"] += 1
        (out_lab / f"{p.stem}.txt").write_text("\n".join(lineas), encoding="utf-8")
        cv2.imwrite(str(out_prev / f"{p.stem}_prev.jpg"), vis)
        resumen["imagenes"] += 1

    resumen["generado"] = datetime.datetime.now().isoformat(timespec="seconds")
    with open(ruta_salida("_handoffs", "etiquetado.json"), "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)
    print(f"[OK] Etiquetadas {resumen['imagenes']} imgs, {resumen['detecciones']} objetos.")
    print(f"     Labels -> {out_lab}\n     Preview -> {out_prev}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python paso4_etiquetar.py <carpeta_imagenes> [conf]"); sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)

"""DESPLIEGUE MOVIL - Exporta best.pt a formatos para telefono
Convierte el modelo YOLO a formatos optimizados para inferencia en movil:
  - ONNX    : universal, sirve para ONNX Runtime Mobile
  - TFLite  : Android (Samsung S25) via TensorFlow Lite
  - NCNN    : ultra-ligero, ideal para tiempo real en CPU de movil

Los archivos se dejan en 07_Pipeline_CacaoIA/03_despliegue/modelos_movil/ y se
copian tambien a 03_App_S25/models si esa carpeta existe.

Uso:  python exportar_movil.py [imgsz]     (imgsz por defecto 640; usa 320 para movil rapido)
"""
import sys, shutil, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_config"))
from utils_config import CFG, ruta_salida  # noqa: E402
from ultralytics import YOLO


def main(imgsz=640):
    modelo = YOLO(CFG["modelos"]["yolo_best"])
    out = ruta_salida("03_despliegue", "modelos_movil", "_.tmp").parent
    exportados = {}

    for fmt in ("onnx", "tflite", "ncnn"):
        try:
            ruta = modelo.export(format=fmt, imgsz=imgsz, half=False)
            destino = out / Path(str(ruta)).name
            if Path(str(ruta)).exists():
                if Path(str(ruta)).is_dir():
                    shutil.copytree(ruta, destino, dirs_exist_ok=True)
                else:
                    shutil.copy(ruta, destino)
            exportados[fmt] = str(destino)
            print(f"[OK] {fmt.upper()} -> {destino}")
        except Exception as e:
            exportados[fmt] = f"ERROR: {e}"
            print(f"[!] {fmt.upper()} fallo: {e}")

    # Copiar a la app del Samsung S25 si existe
    s25 = Path(CFG["proyecto"]["raiz"]) / "03_App_S25" / "models"
    if s25.exists():
        for f in out.glob("*.onnx"):
            shutil.copy(f, s25 / f.name)
        print(f"[OK] Modelos ONNX copiados a {s25}")

    with open(ruta_salida("_handoffs", "export_movil.json"), "w", encoding="utf-8") as fp:
        json.dump({"generado": datetime.datetime.now().isoformat(timespec="seconds"),
                   "imgsz": imgsz, "exportados": exportados}, fp, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 640)

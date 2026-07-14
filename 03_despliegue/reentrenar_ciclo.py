"""REENTRENAMIENTO POR CICLOS (circuito de aprendizaje)
Hace fine-tuning DESDE best.pt (no desde cero) sumando las fotos de campo que la
app fue guardando en dataset_campo/. Usa early stopping (patience) para no
sobreajustar. Respalda el best.pt anterior antes de reemplazarlo.

Uso:
  python reentrenar_ciclo.py            # ciclo estandar (60 epocas, patience 12)
  python reentrenar_ciclo.py 10 5       # epocas=10 patience=5 (ciclo de validacion)
"""
import sys, shutil, datetime, random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_config"))
from utils_config import CFG  # noqa: E402
from ultralytics import YOLO

BASE = Path(__file__).resolve().parent
CAMPO_IMG = BASE / "dataset_campo" / "images"
BASE_IMG = Path(CFG["dataset"]["imagenes"])          # CacaoIAV.yolo26/train/images
SALIDA = BASE / "reentrenamiento"
SALIDA.mkdir(exist_ok=True)


def recolectar():
    imgs = []
    for d in (BASE_IMG, CAMPO_IMG):
        if d.exists():
            imgs += [p for p in d.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")
                     and (d.parent / "labels" / (p.stem + ".txt")).exists()]
    return imgs


def main(epocas=60, patience=12):
    imgs = recolectar()
    n_campo = len([1 for p in imgs if CAMPO_IMG in p.parents])
    if len(imgs) < 10:
        print(f"[!] Solo {len(imgs)} imagenes con etiqueta. Sube mas fotos en la app primero."); return
    random.seed(42); random.shuffle(imgs)
    corte = max(1, int(len(imgs) * 0.15))
    val, train = imgs[:corte], imgs[corte:]

    (SALIDA / "train.txt").write_text("\n".join(str(p) for p in train), encoding="utf-8")
    (SALIDA / "val.txt").write_text("\n".join(str(p) for p in val), encoding="utf-8")

    nombres = [CFG["clases"][i] for i in sorted(CFG["clases"])]
    yaml_txt = (f"train: {SALIDA / 'train.txt'}\nval: {SALIDA / 'val.txt'}\n"
                f"nc: {len(nombres)}\nnames: {nombres}\n")
    data_yaml = SALIDA / "data_ciclo.yaml"
    data_yaml.write_text(yaml_txt.replace("\\", "/"), encoding="utf-8")

    print(f"[*] Fine-tuning desde best.pt | train={len(train)} val={len(val)} "
          f"(fotos de campo nuevas: {n_campo}) | epocas={epocas} patience={patience}")
    model = YOLO(CFG["modelos"]["yolo_best"])
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    model.train(data=str(data_yaml), epochs=epocas, patience=patience, imgsz=640,
                batch=8, project=str(SALIDA), name=f"ciclo_{ts}", exist_ok=True)

    nuevo = SALIDA / f"ciclo_{ts}" / "weights" / "best.pt"
    if nuevo.exists():
        best = Path(CFG["modelos"]["yolo_best"])
        backup = best.with_name(f"best_backup_{ts}.pt")
        shutil.copy(best, backup)
        shutil.copy(nuevo, best)
        print(f"[OK] best.pt actualizado. Respaldo del anterior en {backup.name}")
    else:
        print("[!] No se genero best.pt (revisa el log de entrenamiento).")


if __name__ == "__main__":
    ep = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    pat = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    main(ep, pat)

"""APP CACAOIA - Despliegue local unificado (tiempo real + circuito de aprendizaje)
Sobre best.pt (12 clases). Corre 100% local:  http://localhost:5001

Qué hace al subir una foto (o en cámara en vivo):
  1. Detecta y LOCALIZA los objetos (hojas, nervaduras, frutos...) con YOLO.
  2. CUENTA cuántos hay por clase.
  3. Sobre las hojas, hace un OVERLAY verde/rojo por pixel (indice antocianina
     R/(R+G)) y reporta el % de pixel rojo -> proxy de pigmentacion/variedad.
  4. GUARDA la foto y su pre-etiqueta YOLO en dataset_campo/ (circuito de
     aprendizaje activo: cada foto alimenta el reentrenamiento).

Funciones puras (detectar, anotar, overlay_color) son importables y testeables.
"""
import sys, io, time, datetime, csv, base64
from pathlib import Path
import cv2
import numpy as np
from flask import Flask, request, Response, jsonify, render_template

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_config"))
from utils_config import CFG  # noqa: E402
from ultralytics import YOLO

# ---------------- configuracion ----------------
# Usa el modelo de despliegue que SI detecta (yolo_deploy); cae a yolo_best si no.
MODEL_PATH = CFG["modelos"].get("yolo_deploy") or CFG["modelos"]["yolo_best"]
MODEL_HOJAS = CFG["modelos"].get("yolo_hojas")   # 2do modelo: tipos de hoja (9 clases)
MODEL_COCO = str(Path(CFG["proyecto"]["raiz"]) / "02_Motor_Entrenamiento" / "yolov8n.pt")  # COCO: detecta 'persona'
CONF = CFG["modelos"]["yolo_conf"]

BASE = Path(__file__).resolve().parent
CAMPO_IMG = BASE / "dataset_campo" / "images"
CAMPO_LAB = BASE / "dataset_campo" / "labels"
CAMPO_IMG.mkdir(parents=True, exist_ok=True)
CAMPO_LAB.mkdir(parents=True, exist_ok=True)
REGISTRO = BASE / "dataset_campo" / "registro.csv"

_model = None      # modelo enfermedad
_model2 = None     # modelo hojas (9 clases)
_model_coco = None # COCO: personas
_NAMES = {}
_NAMES2 = {}
_COLORS = np.random.RandomState(42).randint(60, 255, size=(64, 3)).tolist()


def _color_de(nombre):
    """Color estable por nombre de clase (evita choques entre los 2 modelos)."""
    return _COLORS[hash(nombre) % len(_COLORS)]

# Corrige nombres de clase mal escritos en el modelo, para mostrarlos bien
REMAP = {
    "Fitoftora": "Phytophthora", "fitoftora": "Phytophthora", "Phytoftora": "Phytophthora",
    "Monilia": "Moniliophthora", "monilia": "Moniliophthora", "Moniliphthora": "Moniliophthora",
}


def modelo():
    """Carga los modelos: enfermedad + hojas (9 clases) + COCO (personas)."""
    global _model, _model2, _model_coco, _NAMES, _NAMES2
    if _model is None:
        _model = YOLO(MODEL_PATH)
        _NAMES = dict(_model.names)
    if _model2 is None and MODEL_HOJAS and Path(MODEL_HOJAS).exists():
        _model2 = YOLO(MODEL_HOJAS)
        _NAMES2 = dict(_model2.names)
    if _model_coco is None and Path(MODEL_COCO).exists():
        _model_coco = YOLO(MODEL_COCO)
    return _model


def _dentro(cx, cy, cajas):
    return any(px1 <= cx <= px2 and py1 <= cy <= py2 for (px1, py1, px2, py2) in cajas)


# ---------------- funciones puras ----------------
def detectar(img_bgr, conf=CONF):
    """Personas (COCO) + cacao (enfermedad + hojas). Descarta cacao que cae sobre un humano."""
    modelo()
    dets = []
    # 1) Personas -> para no confundir humanos con cacao
    personas = []
    if _model_coco is not None:
        rc = _model_coco.predict(img_bgr, conf=0.35, classes=[0], verbose=False)[0]  # 0 = person
        if rc.boxes is not None:
            for box in rc.boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = map(int, box)
                personas.append((x1, y1, x2, y2))
                dets.append({"cls": -1, "nombre": "persona", "conf": 1.0, "bbox": [x1, y1, x2, y2]})
    # 2) Cacao (2 modelos), filtrando lo que cae dentro de una persona
    for mdl, names in [(_model, _NAMES), (_model2, _NAMES2)]:
        if mdl is None:
            continue
        res = mdl.predict(img_bgr, conf=conf, verbose=False)[0]
        if res.boxes is None:
            continue
        for box, cls, cf in zip(res.boxes.xyxy.cpu().numpy(),
                                res.boxes.cls.cpu().numpy().astype(int),
                                res.boxes.conf.cpu().numpy()):
            x1, y1, x2, y2 = map(int, box)
            if _dentro((x1 + x2) // 2, (y1 + y2) // 2, personas):
                continue  # cae sobre un humano -> no es cacao
            raw = names.get(int(cls), str(int(cls)))
            dets.append({"cls": int(cls), "nombre": REMAP.get(raw, raw),
                         "conf": float(cf), "bbox": [x1, y1, x2, y2]})
    return dets


def anotar(img_bgr, dets):
    """Dibuja cajas + etiquetas. Devuelve (imagen, conteo_por_clase)."""
    vis = img_bgr.copy()
    conteo = {}
    for d in dets:
        x1, y1, x2, y2 = d["bbox"]
        color = _color_de(d["nombre"])
        cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
        etq = f'{d["nombre"]} {d["conf"]:.0%}'
        (tw, th), _ = cv2.getTextSize(etq, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        cv2.rectangle(vis, (x1, y1 - th - 6), (x1 + tw, y1), color, -1)
        cv2.putText(vis, etq, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        conteo[d["nombre"]] = conteo.get(d["nombre"], 0) + 1
    return vis, conteo


def overlay_color_hojas(img_bgr, dets, umbral_rojo=0.52):
    """Sobre cada hoja: colorea verde (sano) vs rojo (antocianina) por pixel.
    antocianina = R/(R+G). Devuelve (overlay, stats_por_hoja)."""
    over = img_bgr.copy()
    stats = []
    for d in dets:
        if d["nombre"] == "persona":
            continue
        x1, y1, x2, y2 = d["bbox"]
        roi = img_bgr[y1:y2, x1:x2].astype(np.float32)
        if roi.size == 0:
            continue
        b, g, r = roi[:, :, 0], roi[:, :, 1], roi[:, :, 2]
        fondo = (r + g + b) < 30            # descartar pixel negros/fondo
        ratio = r / (r + g + 1e-6)
        es_rojo = (ratio >= umbral_rojo) & (~fondo)
        es_verde = (~es_rojo) & (~fondo)
        pintado = over[y1:y2, x1:x2]
        pintado[es_rojo] = (0.35 * pintado[es_rojo] + 0.65 * np.array([40, 40, 220])).astype(np.uint8)
        pintado[es_verde] = (0.55 * pintado[es_verde] + 0.45 * np.array([40, 200, 40])).astype(np.uint8)
        validos = (~fondo).sum()
        pct_rojo = float(es_rojo.sum() / validos * 100) if validos > 0 else 0.0
        stats.append({"hoja": d["nombre"], "pct_rojo": round(pct_rojo, 1),
                      "pigmentacion": "alta" if pct_rojo > 25 else ("media" if pct_rojo > 8 else "baja")})
    return over, stats


# ---------------- circuito de aprendizaje ----------------
def guardar_para_aprendizaje(img_bgr, dets, nombre_orig):
    """Guarda foto + pre-etiqueta YOLO (.txt) con marca de tiempo. Nunca sobrescribe."""
    h, w = img_bgr.shape[:2]
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    stem = f"{ts}_{Path(nombre_orig).stem}"
    cv2.imwrite(str(CAMPO_IMG / f"{stem}.jpg"), img_bgr)
    lineas = []
    for d in dets:
        x1, y1, x2, y2 = d["bbox"]
        cx, cy, bw, bh = ((x1+x2)/2/w, (y1+y2)/2/h, (x2-x1)/w, (y2-y1)/h)
        lineas.append(f"{d['cls']} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
    (CAMPO_LAB / f"{stem}.txt").write_text("\n".join(lineas), encoding="utf-8")
    nuevo = not REGISTRO.exists()
    with open(REGISTRO, "a", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        if nuevo:
            wr.writerow(["archivo", "fecha", "n_detecciones"])
        wr.writerow([f"{stem}.jpg", ts, len(dets)])
    return stem


def b64(img_bgr):
    _, buf = cv2.imencode(".jpg", img_bgr)
    return "data:image/jpeg;base64," + base64.b64encode(buf).decode()


# ---------------- app ----------------
app = Flask(__name__)


@app.after_request
def no_cache(resp):
    """Evita que el navegador use una version vieja cacheada de la pagina."""
    resp.headers["Cache-Control"] = "no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    return resp


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/detect", methods=["POST"])
def api_detect():
    f = request.files.get("foto")
    if not f:
        return jsonify({"error": "sin foto"}), 400
    conf = float(request.form.get("conf", CONF))
    img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
    dets = detectar(img, conf)
    vis, conteo = anotar(img, dets)
    over, color_stats = overlay_color_hojas(img, dets)
    stem = guardar_para_aprendizaje(img, dets, f.filename or "foto")
    return jsonify({
        "n_total": len(dets),
        "conteo": conteo,
        "color_hojas": color_stats,
        "anotada": b64(vis),
        "color": b64(over),
        "guardada_como": stem,
        "total_campo": len(list(CAMPO_IMG.glob('*.jpg'))),
    })


@app.route("/api/detect_frame", methods=["POST"])
def api_detect_frame():
    """Detección LIGERA para la cámara en vivo: solo anota (sin guardar ni color)."""
    f = request.files.get("foto")
    if not f:
        return jsonify({"error": "sin foto"}), 400
    img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
    dets = detectar(img)
    conteo = {}
    for d in dets:
        conteo[d["nombre"]] = conteo.get(d["nombre"], 0) + 1
    # solo coordenadas -> el navegador dibuja las cajas sobre el video fluido
    salida = [{"nombre": d["nombre"], "conf": d["conf"], "bbox": d["bbox"]} for d in dets]
    return jsonify({"dets": salida, "conteo": conteo, "n_total": len(dets)})


def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.05); continue
        dets = detectar(frame)
        vis, _ = anotar(frame, dets)
        _, buf = cv2.imencode(".jpg", vis)
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n")


@app.route("/stream")
def stream():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/estado")
def estado():
    return jsonify({"fotos_campo": len(list(CAMPO_IMG.glob('*.jpg'))),
                    "modelo": Path(MODEL_PATH).name})


if __name__ == "__main__":
    print("CacaoIA app -> http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, threaded=True)

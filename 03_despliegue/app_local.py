"""DESPLIEGUE LOCAL - App Flask para inferencia CacaoIA
Dos modos en una sola app:
  1. Subir foto  (POST /detectar)         -> devuelve imagen anotada + JSON de detecciones
  2. Camara en tiempo real (GET /stream)   -> MJPEG con etiquetas robustas superpuestas

Etiquetas "robustas": se dibuja clase + confianza y se filtra por conf minima del
config. Corre 100% local (no requiere nube). Ideal para el portatil de campo.

Uso:  python app_local.py    ->  http://localhost:5001
"""
import sys, io, time
from pathlib import Path
import cv2
import numpy as np
from flask import Flask, request, Response, jsonify, render_template_string

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_config"))
from utils_config import CFG, nombre_clase  # noqa: E402
from ultralytics import YOLO

app = Flask(__name__)
MODELO = YOLO(CFG["modelos"]["yolo_best"])
CONF = CFG["modelos"]["yolo_conf"]
_COLORS = np.random.RandomState(42).randint(0, 255, size=(len(CFG["clases"]), 3)).tolist()

HTML = """
<!doctype html><html lang=es><head><meta charset=utf-8><title>CacaoIA Local</title>
<style>body{font-family:system-ui;background:#0f1b0f;color:#e8f5e9;text-align:center;margin:0;padding:20px}
h1{color:#8bc34a}.card{background:#1b2e1b;border-radius:12px;padding:20px;margin:16px auto;max-width:820px}
img{max-width:100%;border-radius:8px}button,input{padding:10px 16px;border-radius:8px;border:0;font-size:15px}
button{background:#4caf50;color:#fff;cursor:pointer}</style></head><body>
<h1>CacaoIA - Inferencia local</h1>
<div class=card><h3>Camara en tiempo real</h3><img src="/stream"></div>
<div class=card><h3>Subir foto</h3>
<form action="/detectar" method=post enctype=multipart/form-data>
<input type=file name=foto accept="image/*"><button>Detectar</button></form></div>
</body></html>"""


def anotar(img):
    res = MODELO.predict(img, conf=CONF, verbose=False)[0]
    dets = []
    if res.boxes is not None:
        for box, cls, cf in zip(res.boxes.xyxy.cpu().numpy(),
                                res.boxes.cls.cpu().numpy().astype(int),
                                res.boxes.conf.cpu().numpy()):
            x1, y1, x2, y2 = map(int, box)
            color = _COLORS[cls % len(_COLORS)]
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            etq = f"{nombre_clase(cls)} {cf:.2f}"
            (tw, th), _ = cv2.getTextSize(etq, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(img, (x1, y1 - th - 8), (x1 + tw, y1), color, -1)
            cv2.putText(img, etq, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            dets.append({"clase": nombre_clase(cls), "conf": round(float(cf), 3),
                         "bbox": [x1, y1, x2, y2]})
    return img, dets


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/detectar", methods=["POST"])
def detectar():
    f = request.files.get("foto")
    if not f:
        return jsonify({"error": "sin foto"}), 400
    img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
    img, dets = anotar(img)
    _, buf = cv2.imencode(".jpg", img)
    return Response(buf.tobytes(), mimetype="image/jpeg",
                    headers={"X-Detecciones": str(len(dets))})


def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.05); continue
        frame, _ = anotar(frame)
        _, buf = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n")


@app.route("/stream")
def stream():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    print("CacaoIA local -> http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, threaded=True)

"""🌱 CacaoIA — App de reconocimiento (Streamlit)
Sube una foto o usa la cámara -> detecta y cuenta (enfermedad / hojas) + color.
Robusto y sin dependencias frágiles. Hosting gratis en Streamlit Community Cloud.
"""
import streamlit as st
import numpy as np
import cv2
from PIL import Image

REMAP = {"Fitoftora": "Phytophthora", "Monilia": "Moniliophthora"}
MODELOS = {
    "Enfermedad (mazorca/fruto)": "best.pt",
    "Tipos de hoja (9 clases)": "best_9clases.pt",
}

st.set_page_config(page_title="CacaoIA", page_icon="🌱", layout="wide")


PALETA = [(230, 60, 60), (60, 200, 60), (60, 120, 240), (240, 180, 40),
          (200, 60, 200), (40, 200, 200), (240, 120, 40), (140, 100, 220)]


@st.cache_resource(show_spinner="Cargando modelo…")
def cargar(nombre_archivo):
    from ultralytics import YOLO
    from huggingface_hub import hf_hub_download
    ruta = hf_hub_download("juanvilla/cacao-modelo", nombre_archivo)
    return YOLO(ruta)


def analizar(img_rgb, modelo, conf):
    bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    r = modelo.predict(bgr, conf=conf, verbose=False)[0]
    anot = img_rgb.copy()
    over = img_rgb.copy()
    conteo = {}
    if r.boxes is not None:
        for i, (b, c, cf) in enumerate(zip(r.boxes.xyxy.cpu().numpy(),
                                           r.boxes.cls.cpu().numpy().astype(int),
                                           r.boxes.conf.cpu().numpy())):
            nom = REMAP.get(modelo.names[c], modelo.names[c])  # corrige la etiqueta al mostrar
            conteo[nom] = conteo.get(nom, 0) + 1
            x1, y1, x2, y2 = map(int, b)
            color = PALETA[i % len(PALETA)]
            cv2.rectangle(anot, (x1, y1), (x2, y2), color, 3)
            cv2.putText(anot, f"{nom} {cf:.0%}", (x1, max(20, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            roi = img_rgb[y1:y2, x1:x2].astype(np.float32)
            if roi.size:
                rr, gg = roi[:, :, 0], roi[:, :, 1]
                rojo = (rr / (rr + gg + 1e-6)) >= 0.52
                p = over[y1:y2, x1:x2]
                p[rojo] = (0.4 * p[rojo] + 0.6 * np.array([220, 40, 40])).astype(np.uint8)
    return anot, over, conteo


# ---------- UI ----------
st.title("🌱 CacaoIA — Reconocimiento de cacao")
st.caption("Detecta enfermedad y tipos de hoja. Sube una foto o usa tu cámara.")

col = st.sidebar
col.header("Ajustes")
modelo_sel = col.selectbox("¿Qué reconocer?", list(MODELOS.keys()))
conf = col.slider("Confianza mínima", 0.05, 0.9, 0.25, 0.05)
fuente = col.radio("Entrada", ["Subir foto", "Cámara"])

img_rgb = None
if fuente == "Subir foto":
    f = st.file_uploader("Elige una imagen", type=["jpg", "jpeg", "png"])
    if f:
        img_rgb = np.array(Image.open(f).convert("RGB"))
else:
    c = st.camera_input("Toma una foto")
    if c:
        img_rgb = np.array(Image.open(c).convert("RGB"))

if img_rgb is not None:
    modelo = cargar(MODELOS[modelo_sel])
    with st.spinner("Analizando…"):
        anot, over, conteo = analizar(img_rgb, modelo, conf)
    c1, c2 = st.columns(2)
    c1.image(anot, caption="Detección + etiquetas", use_container_width=True)
    c2.image(over, caption="Pigmentación (rojo = antocianina)", use_container_width=True)
    if conteo:
        st.success("Detectado: " + " · ".join(f"**{v}** {k}" for k, v in conteo.items()))
    else:
        st.warning("No se detectaron objetos. Baja la confianza o acércate más.")
else:
    st.info("👈 Sube una foto o activa la cámara para empezar.")

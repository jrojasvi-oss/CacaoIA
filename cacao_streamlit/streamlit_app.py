"""🌱 CacaoIA — App de reconocimiento (Streamlit, SIN OpenCV)
Sube una foto o usa la cámara -> detecta y cuenta (enfermedad / hojas) + pigmentación.
Sin cv2 -> despliega sin problemas en Streamlit Community Cloud (gratis y permanente).
"""
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw

REMAP = {"Fitoftora": "Phytophthora", "Monilia": "Moniliophthora"}
MODELOS = {
    "Enfermedad (mazorca/fruto)": "best.pt",
    "Tipos de hoja (9 clases)": "best_9clases.pt",
}
PALETA = [(230, 60, 60), (60, 200, 60), (60, 120, 240), (240, 180, 40),
          (200, 60, 200), (40, 200, 200), (240, 120, 40), (140, 100, 220)]

st.set_page_config(page_title="CacaoIA", page_icon="🌱", layout="wide")


@st.cache_resource(show_spinner="Cargando modelo…")
def cargar(nombre_archivo):
    from ultralytics import YOLO
    from huggingface_hub import hf_hub_download
    return YOLO(hf_hub_download("juanvilla/cacao-modelo", nombre_archivo))


def analizar(pil_img, modelo, conf):
    r = modelo.predict(pil_img, conf=conf, verbose=False)[0]   # PIL RGB -> ultralytics lo maneja bien
    arr = np.array(pil_img)
    anot = pil_img.copy()
    draw = ImageDraw.Draw(anot)
    over = arr.copy()
    conteo = {}
    if r.boxes is not None:
        for i, (b, c, cf) in enumerate(zip(r.boxes.xyxy.cpu().numpy(),
                                           r.boxes.cls.cpu().numpy().astype(int),
                                           r.boxes.conf.cpu().numpy())):
            nom = REMAP.get(modelo.names[c], modelo.names[c])
            conteo[nom] = conteo.get(nom, 0) + 1
            x1, y1, x2, y2 = map(int, b)
            color = PALETA[i % len(PALETA)]
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            draw.text((x1 + 2, max(0, y1 - 12)), f"{nom} {cf:.0%}", fill=color)
            roi = arr[y1:y2, x1:x2].astype(np.float32)
            if roi.size:
                rr, gg = roi[:, :, 0], roi[:, :, 1]
                rojo = (rr / (rr + gg + 1e-6)) >= 0.52
                p = over[y1:y2, x1:x2]
                p[rojo] = (0.4 * p[rojo] + 0.6 * np.array([220, 40, 40])).astype(np.uint8)
    return np.array(anot), over, conteo


# ---------- UI ----------
st.title("🌱 CacaoIA — Reconocimiento de cacao")
st.caption("Detecta enfermedad y tipos de hoja. Sube una foto o usa tu cámara.")

s = st.sidebar
s.header("Ajustes")
modelo_sel = s.selectbox("¿Qué reconocer?", list(MODELOS.keys()))
conf = s.slider("Confianza mínima", 0.05, 0.9, 0.25, 0.05)
fuente = s.radio("Entrada", ["Subir foto", "Cámara"])

pil = None
if fuente == "Subir foto":
    f = st.file_uploader("Elige una imagen", type=["jpg", "jpeg", "png"])
    if f:
        pil = Image.open(f).convert("RGB")
else:
    c = st.camera_input("Toma una foto")
    if c:
        pil = Image.open(c).convert("RGB")

if pil is not None:
    modelo = cargar(MODELOS[modelo_sel])
    with st.spinner("Analizando…"):
        anot, over, conteo = analizar(pil, modelo, conf)
    c1, c2 = st.columns(2)
    c1.image(anot, caption="Detección + etiquetas", use_container_width=True)
    c2.image(over, caption="Pigmentación (rojo = antocianina)", use_container_width=True)
    if conteo:
        st.success("Detectado: " + " · ".join(f"**{v}** {k}" for k, v in conteo.items()))
    else:
        st.warning("No se detectaron objetos. Baja la confianza o acércate más.")
else:
    st.info("👈 Sube una foto o activa la cámara para empezar.")

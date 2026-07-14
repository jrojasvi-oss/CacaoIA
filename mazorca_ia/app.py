"""🌰 MAZORCA IA — Asistente conversacional libre y abierto de cacao
Para estudiantes (usos de la IA) y agricultores del Valle del Cauca.

Combina 3 capacidades:
  1. VISIÓN  : sube una foto -> detecta enfermedad del cacao (YOLO).
  2. WEB     : busca información real y actualizada (DuckDuckGo).
  3. DIÁLOGO : modelo LIBRE y ABIERTO vía HuggingFace Inference (gratis).

100% software libre. En un HF Space el token (HF_TOKEN) está disponible solo;
en local, si no hay token, responde igual con visión + web (sin síntesis LLM).
"""
import os
from pathlib import Path
import numpy as np
import cv2
import gradio as gr

# ---------- configuracion ----------
BASE = Path(__file__).resolve().parent
MODEL_LOCAL = "C:/Users/juanv/Desktop/PROYECTO_CACAO_IA/05_Datasets_Consolidados/Dataset_3_Clases_Enfermedades/runs/detect/train_robusto/weights/best.pt"
MODEL_PATH = str(BASE / "best.pt") if (BASE / "best.pt").exists() else MODEL_LOCAL
LLM_MODEL = os.environ.get("MAZORCA_LLM", "meta-llama/Llama-3.2-3B-Instruct")
HF_TOKEN = os.environ.get("HF_TOKEN")
REMAP = {"Fitoftora": "Phytophthora", "Monilia": "Moniliophthora"}

SISTEMA = (
    "Eres 'Mazorca IA', un asistente experto y cercano sobre el cultivo de cacao "
    "(Theobroma cacao), especializado en el Valle del Cauca, Colombia. Ayudas tanto "
    "a estudiantes que aprenden sobre IA como a agricultores de campo. Explicas en "
    "español claro y práctico, con recomendaciones agronómicas responsables. Si te dan "
    "un diagnóstico de visión por computadora o resultados de búsqueda web, úsalos. "
    "Nunca inventes datos; si no sabes algo, dilo."
)

_yolo = None


def yolo():
    global _yolo
    if _yolo is None:
        from ultralytics import YOLO
        _yolo = YOLO(MODEL_PATH)
    return _yolo


def diagnosticar(img_rgb):
    """Detecta enfermedad en la foto. Devuelve texto de diagnóstico."""
    if img_rgb is None:
        return None
    m = yolo()
    bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    r = m.predict(bgr, conf=0.25, verbose=False)[0]
    if r.boxes is None or len(r.boxes) == 0:
        return "No detecté objetos claros de cacao en la foto (prueba con más luz o más cerca)."
    conteo = {}
    for c, cf in zip(r.boxes.cls.cpu().numpy().astype(int), r.boxes.conf.cpu().numpy()):
        nom = REMAP.get(m.names[c], m.names[c])
        conteo[nom] = max(conteo.get(nom, 0), float(cf))
    partes = [f"{k} (confianza {v:.0%})" for k, v in conteo.items()]
    return "Diagnóstico visual: detecté " + ", ".join(partes) + "."


def buscar_web(consulta, n=3):
    try:
        from ddgs import DDGS
        with DDGS() as d:
            res = list(d.text(f"{consulta} cacao Theobroma", max_results=n))
        if not res:
            return ""
        return "\n".join(f"- {r.get('title','')}: {r.get('body','')[:220]}" for r in res)
    except Exception:
        return ""


def llm(mensajes):
    if not HF_TOKEN:
        return None
    try:
        from huggingface_hub import InferenceClient
        cli = InferenceClient(model=LLM_MODEL, token=HF_TOKEN)
        out = cli.chat_completion(messages=mensajes, max_tokens=500, temperature=0.4)
        return out.choices[0].message.content
    except Exception as e:
        return f"(No pude usar el modelo de lenguaje: {str(e)[:80]}. Te doy lo que sí tengo abajo.)"


def responder(mensaje, imagen, historial):
    diag = diagnosticar(imagen) if imagen is not None else None
    web = buscar_web(mensaje) if mensaje and len(mensaje) > 3 else ""

    contexto = ""
    if diag:
        contexto += f"\n[Visión] {diag}"
    if web:
        contexto += f"\n[Búsqueda web]\n{web}"

    mensajes = [{"role": "system", "content": SISTEMA}]
    for u, a in historial[-4:]:
        mensajes += [{"role": "user", "content": u}, {"role": "assistant", "content": a}]
    mensajes.append({"role": "user", "content": (mensaje or "Analiza la foto.") + contexto})

    r = llm(mensajes)
    if r is None:  # sin LLM (local sin token) -> respuesta compuesta
        piezas = []
        if diag:
            piezas.append(diag)
        if web:
            piezas.append("Información encontrada en la web:\n" + web)
        if not piezas:
            piezas.append("Sube una foto de una hoja o mazorca, o pregúntame sobre el cultivo de cacao. "
                          "(El modelo conversacional se activa al desplegar en HuggingFace con tu token.)")
        return "\n\n".join(piezas)
    return r


# ---------- interfaz ----------
with gr.Blocks(title="Mazorca IA") as demo:
    gr.Markdown("# 🌰 Mazorca IA\nAsistente **libre y abierto** de cacao para el Valle del Cauca. "
                "Sube una foto para diagnóstico, o pregunta lo que quieras. Busca en la web en vivo.")
    chatbot = gr.Chatbot(height=380)
    with gr.Row():
        img = gr.Image(label="Foto (opcional)", type="numpy", height=140)
        with gr.Column(scale=3):
            msg = gr.Textbox(label="Tu mensaje", placeholder="¿Qué le pasa a mi mazorca? ¿Cómo controlo la monilia?")
            enviar = gr.Button("Enviar", variant="primary")

    def on_send(mensaje, imagen, hist):
        resp = responder(mensaje, imagen, hist)
        hist = hist + [[mensaje or "(foto)", resp]]
        return hist, None, None

    enviar.click(on_send, [msg, img, chatbot], [chatbot, msg, img])
    msg.submit(on_send, [msg, img, chatbot], [chatbot, msg, img])

if __name__ == "__main__":
    demo.launch()

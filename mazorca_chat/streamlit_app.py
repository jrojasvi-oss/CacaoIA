"""🌰 Mazorca IA — Chatbot de cacao (Streamlit, modelo LIBRE)
Asistente conversacional para estudiantes y agricultores del Valle del Cauca.
- Modelo de lenguaje LIBRE y abierto (HuggingFace Inference).
- Búsqueda WEB en vivo (DuckDuckGo) para dar datos reales.
Ligero (sin torch/cv2) -> despliega rápido y anda bien en el celular.
"""
import os
import streamlit as st

st.set_page_config(page_title="Mazorca IA", page_icon="🌰")

# HF_TOKEN se pone en los Secretos de Streamlit Cloud (nunca en el código).
def _token():
    try:
        return st.secrets["HF_TOKEN"]          # si hay secrets.toml con el token
    except Exception:
        return os.environ.get("HF_TOKEN")      # fallback a variable de entorno / None
HF_TOKEN = _token()
LLM_MODEL = os.environ.get("MAZORCA_LLM", "meta-llama/Llama-3.2-3B-Instruct")
SISTEMA = (
    "Eres 'Mazorca IA', un asistente experto y cercano sobre el cultivo de cacao "
    "(Theobroma cacao), especializado en el Valle del Cauca, Colombia. Ayudas a "
    "estudiantes que aprenden de IA y a agricultores de campo. Respondes en español "
    "claro y práctico, con recomendaciones agronómicas responsables. Si te dan contexto "
    "de una búsqueda web, úsalo. Nunca inventes datos; si no sabes, dilo."
)


def buscar_web(consulta, n=3):
    try:
        from ddgs import DDGS
        with DDGS() as d:
            res = list(d.text(f"{consulta} cacao Theobroma", max_results=n))
        return "\n".join(f"- {r.get('title','')}: {r.get('body','')[:220]}" for r in res)
    except Exception:
        return ""


def responder(mensaje, historial):
    web = buscar_web(mensaje)
    if not HF_TOKEN:
        base = "🔑 El diálogo se activa al agregar **HF_TOKEN** en los Secretos de Streamlit."
        return base + (f"\n\n**Encontré en la web:**\n{web}" if web else "")
    try:
        from huggingface_hub import InferenceClient
        cli = InferenceClient(model=LLM_MODEL, token=HF_TOKEN)
        msgs = [{"role": "system", "content": SISTEMA}]
        msgs += [{"role": m["role"], "content": m["content"]} for m in historial[-8:]]
        contenido = mensaje + (f"\n\n[Contexto web]\n{web}" if web else "")
        msgs.append({"role": "user", "content": contenido})
        out = cli.chat_completion(messages=msgs, max_tokens=500, temperature=0.4)
        return out.choices[0].message.content
    except Exception as e:
        return f"(No pude usar el modelo: {str(e)[:120]})" + (f"\n\nInfo web:\n{web}" if web else "")


# ---------- UI ----------
st.title("🌰 Mazorca IA")
st.caption("Asistente libre de cacao para el Valle del Cauca. Pregunta lo que quieras sobre variedades, enfermedades o cultivo.")

if "hist" not in st.session_state:
    st.session_state.hist = []

for m in st.session_state.hist:
    st.chat_message(m["role"]).write(m["content"])

if prompt := st.chat_input("¿Cómo controlo la monilia? ¿Qué variedad de cacao me conviene?"):
    st.chat_message("user").write(prompt)
    st.session_state.hist.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Pensando…"):
            resp = responder(prompt, st.session_state.hist)
        st.write(resp)
    st.session_state.hist.append({"role": "assistant", "content": resp})

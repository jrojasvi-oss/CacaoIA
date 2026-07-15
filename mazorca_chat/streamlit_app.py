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
        return st.secrets["HF_TOKEN"]          # 1) secrets.toml (Streamlit Cloud)
    except Exception:
        pass
    if os.environ.get("HF_TOKEN"):
        return os.environ["HF_TOKEN"]          # 2) variable de entorno
    try:
        from huggingface_hub import get_token  # 3) token guardado por 'huggingface-cli login'
        return get_token()
    except Exception:
        return None
HF_TOKEN = _token()
LLM_MODEL = os.environ.get("MAZORCA_LLM", "Qwen/Qwen2.5-7B-Instruct")  # libre, sin licencia gated
SISTEMA = (
    "Eres 'Mazorca IA', una mazorca de cacao con alma de PARCERO del Valle del Cauca. "
    "Hablas como un amigo campesino colombiano: cercano, cálido y con dialecto valluno/paisa "
    "(usa expresiones como 'parcero', 'hágale', '¿bien o qué?', 'de una', 'sumercé' con respeto), "
    "pero siempre claro y práctico. Eres experto en cacao (Theobroma cacao): variedades, "
    "enfermedades como monilia (Moniliophthora roreri) y fitóftora (Phytophthora), cultivo, "
    "poda, cosecha y beneficio. Si es una conversación nueva y aún no sabes de la persona, "
    "salúdala como Mazorca IA y pregúntale con cariño: (1) de dónde es o dónde queda su finca, "
    "y (2) si ya tiene cacao sembrado o apenas va a empezar. Da recomendaciones agronómicas "
    "responsables. Si te dan contexto de una búsqueda web, úsalo. Nunca inventes; si no sabes, "
    "dilo con humildad."
)
BIENVENIDA = ("¡Quiubo, parcero! 🌰 Soy **Mazorca IA**, su compañero cacaotero del Valle. "
              "Pa' ayudarle mejor, cuénteme dos cositas: ¿de dónde es o dónde le queda la finca? "
              "¿Y ya tiene cacao sembrado o apenas va a arrancar? ¡Hágale, que aquí estoy pa' lo que necesite!")


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
    st.session_state.hist = [{"role": "assistant", "content": BIENVENIDA}]

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

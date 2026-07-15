"""🌰 Mazorca IA — Chatbot de cacao (Streamlit, modelo LIBRE)
Parcero cacaotero del Valle: pregunta inicial (nombre, finca, cacao), conversa
dinámico con repreguntas, usa búsqueda web y ubica en Google Maps satélite.
"""
import os
import urllib.parse
import streamlit as st

st.set_page_config(page_title="Mazorca IA", page_icon="🌰")


def _token():
    try:
        return st.secrets["HF_TOKEN"]
    except Exception:
        pass
    if os.environ.get("HF_TOKEN"):
        return os.environ["HF_TOKEN"]
    try:
        from huggingface_hub import get_token
        return get_token()
    except Exception:
        return None
HF_TOKEN = _token()
LLM_MODEL = os.environ.get("MAZORCA_LLM", "Qwen/Qwen2.5-7B-Instruct")

SISTEMA = (
    "Eres 'Mazorca IA', una mazorca de cacao con alma de PARCERO del Valle del Cauca, "
    "creada en la Universidad Nacional de Colombia (Sede Palmira) como aporte a la "
    "investigación, la innovación y la extensión rural. Hablas como un amigo campesino "
    "colombiano: cálido, cercano, con dialecto valluno/paisa ('parcero', 'hágale', "
    "'¿bien o qué?', 'de una', 'sumercé' con respeto), pero claro y práctico. "
    "Conversa de forma DINÁMICA y natural: no sueltes párrafos enormes; responde corto y "
    "HAZ REPREGUNTAS para entender mejor el caso. Por ejemplo, si hablan de monilia o "
    "fitóftora, pregunta: ¿desde dónde empezó el daño, de arriba o de abajo de la mazorca?, "
    "¿de qué color está la mancha?, ¿cómo está el clima/humedad?, ¿qué edad tiene el árbol? "
    "Con esas respuestas das un diagnóstico y recomendaciones responsables. Eres experto en "
    "cacao (variedades, enfermedades, poda, cosecha, beneficio). Usa el contexto web si te lo "
    "dan. Para PRECIOS del cacao, la fuente OFICIAL es la Federación Nacional de Cacaoteros "
    "(Fedecacao, fedecacao.com.co): cita siempre esa fuente y comparte el enlace. NUNCA inventes "
    "un precio exacto; si no tienes el dato del día, dirige a la persona a consultarlo en "
    "fedecacao.com.co (precio por kilo en Puntos Fedecacao y precio internacional de la tonelada). "
    "Nunca inventes; si no sabes, dilo con humildad."
)
FEDECACAO = (
    "[Fuente oficial de PRECIOS del cacao] Federación Nacional de Cacaoteros (Fedecacao). "
    "El precio del día (por kilo en Puntos Fedecacao y la tonelada internacional en USD) se "
    "publica en https://www.fedecacao.com.co/ — dirige ahí para el precio actualizado y cita la fuente."
)


def buscar_web(consulta, n=3):
    try:
        from ddgs import DDGS
        with DDGS() as d:
            res = list(d.text(f"{consulta} cacao Theobroma", max_results=n))
        return "\n".join(f"- {r.get('title','')}: {r.get('body','')[:220]}" for r in res)
    except Exception:
        return ""


def responder(mensaje, historial, perfil):
    # Si preguntan por precio, busca dirigido en Fedecacao y añade la fuente oficial
    es_precio = any(p in mensaje.lower() for p in ["precio", "cuánto vale", "cuanto vale", "cotiz", "cuánto pagan", "cuanto pagan", "mercado"])
    web = buscar_web("precio del cacao Fedecacao Colombia hoy" if es_precio else mensaje)
    if es_precio:
        web = FEDECACAO + ("\n" + web if web else "")
    ctx_perfil = ""
    if perfil:
        ctx_perfil = (f"\n[Perfil del usuario] Nombre: {perfil['nombre']}. "
                      f"Finca/ubicación: {perfil['ubicacion'] or 'no dijo'}. "
                      f"Cacao: {perfil['cacao']}.")
    if not HF_TOKEN:
        return "🔑 El diálogo se activa con HF_TOKEN." + (f"\n\n**En la web:**\n{web}" if web else "")
    try:
        from huggingface_hub import InferenceClient
        cli = InferenceClient(model=LLM_MODEL, token=HF_TOKEN)
        msgs = [{"role": "system", "content": SISTEMA + ctx_perfil}]
        msgs += [{"role": m["role"], "content": m["content"]} for m in historial[-8:]]
        contenido = mensaje + (f"\n\n[Contexto web]\n{web}" if web else "")
        msgs.append({"role": "user", "content": contenido})
        return cli.chat_completion(messages=msgs, max_tokens=450, temperature=0.5).choices[0].message.content
    except Exception as e:
        return f"(No pude usar el modelo: {str(e)[:120]})" + (f"\n\nInfo web:\n{web}" if web else "")


# ---------- UI ----------
st.title("🌰 Mazorca IA")
st.caption("Tu parcero cacaotero del Valle · Universidad Nacional de Colombia — Sede Palmira")

with st.expander("ℹ️ Conoce más — qué es, cómo se hizo, código y créditos"):
    st.markdown(
        "**CacaoIA** combina visión por computadora (**YOLO + SAM + ViT/DINOv2**) y un "
        "**modelo de lenguaje libre** para reconocer y conversar sobre cacao.\n\n"
        "- 🎓 Trabajo de grado, **Universidad Nacional de Colombia — Sede Palmira**.\n"
        "- 💻 Código abierto: [github.com/jrojasvi-oss/CacaoIA](https://github.com/jrojasvi-oss/CacaoIA)\n"
        "- 🌱 Un aporte del **colectivo Siembra** a una ciencia y tecnología **accesible**.\n"
        "- 🆓 Software libre, modelos de IA abiertos.")

st.info("© 2026 **CacaoIA** · Proyecto de **investigación** — Universidad Nacional de Colombia (Sede Palmira) · "
        "Colectivo **Siembra** · Código: [github.com/jrojasvi-oss/CacaoIA](https://github.com/jrojasvi-oss/CacaoIA) · Software libre")

if "perfil" not in st.session_state:
    st.session_state.perfil = None

# --- Formulario inicial (preguntas fijas antes del chat) ---
if st.session_state.perfil is None:
    st.subheader("Antes de empezar, cuéntame de ti 🌱")
    with st.form("form_perfil"):
        nombre = st.text_input("¿Cómo te llamas?")
        ubic = st.text_input("¿Dónde queda tu finca? (municipio y vereda)")
        cacao = st.radio("¿Tienes cacao?",
                         ["Sí, ya tengo cultivo", "Quiero sembrar", "Apenas estoy aprendiendo"])
        ok = st.form_submit_button("¡Hágale, empecemos! 🌰")
    if ok:
        st.session_state.perfil = {"nombre": nombre.strip() or "parcero", "ubicacion": ubic.strip(), "cacao": cacao}
        n = st.session_state.perfil["nombre"]
        st.session_state.hist = [{"role": "assistant",
            "content": f"¡Quiubo, {n}! 🌰 Un gusto. Soy Mazorca IA. Cuénteme, ¿en qué le puedo ayudar hoy con su cacao? "
                       f"Si es por una enfermedad, mándeme cómo se ve y le voy preguntando pa' afinar el diagnóstico."}]
        st.rerun()
    st.stop()

perfil = st.session_state.perfil
if perfil["ubicacion"]:
    url = "https://www.google.com/maps/search/" + urllib.parse.quote(perfil["ubicacion"]) + "/data=!3m1!1e3"
    st.caption(f"📍 [Ver **{perfil['ubicacion']}** en Google Maps satélite]({url})")
st.caption("💰 Precio oficial del cacao: [Fedecacao — fedecacao.com.co](https://www.fedecacao.com.co/)")

if "hist" not in st.session_state:
    st.session_state.hist = []
for m in st.session_state.hist:
    st.chat_message(m["role"]).write(m["content"])

if prompt := st.chat_input("Escríbele a Mazorca IA…"):
    st.chat_message("user").write(prompt)
    st.session_state.hist.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Pensando…"):
            resp = responder(prompt, st.session_state.hist, perfil)
        st.write(resp)
    st.session_state.hist.append({"role": "assistant", "content": resp})

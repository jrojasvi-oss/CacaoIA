---
title: Mazorca IA
emoji: 🌰
colorFrom: yellow
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# 🌰 Mazorca IA

Asistente conversacional **libre y abierto** sobre el cultivo de cacao, para
estudiantes y agricultores del Valle del Cauca. Combina:

- **Visión** — sube una foto y detecta enfermedad (Phytophthora / Moniliophthora / sana).
- **Web en vivo** — busca información real y actualizada (DuckDuckGo).
- **Diálogo** — modelo de lenguaje libre y abierto vía HuggingFace Inference.

Parte del trabajo de grado *Fenotipado digital de Theobroma cacao* (UNAL Palmira).
Código: https://github.com/jrojasvi-oss/CacaoIA

## Configuración
- Requiere `best.pt` (pesos YOLO) junto a `app.py`.
- El diálogo usa `HF_TOKEN` (en un Space se provee solo). Modelo por defecto:
  `meta-llama/Llama-3.2-3B-Instruct` (cambia con la variable `MAZORCA_LLM`).

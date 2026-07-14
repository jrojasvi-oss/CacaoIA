# 🌱 Pipeline CacaoIA — Consolidado

Carpeta **limpia y ordenada** del proyecto, lista para subir a repositorios. Consolida la lógica de **identificar → segmentar → etiquetar** hojas de cacao con el motor **DINOv2 + YOLO + SAM**, más la **lógica de color/antocianina** (paletas por objeto y montajes 1×30) y el **despliegue local y móvil**.

> El proyecto original (raíz `PROYECTO_CACAO_IA/`) **no se toca**. Aquí solo vive lo relevante y funcional.

---

## 🤖 Despliegue de agentes (economía de tokens)

Tres subagentes persistentes en `.claude/agents/` que se **comunican por archivos** (`_handoffs/*.json`) en vez de re-pasar todo el contexto — así cada uno trabaja con su alcance mínimo:

| Agente | Rol | Modelo | Entrada → Salida |
|---|---|---|---|
| `cacao-analista` | Mapea TODO el proyecto (scripts, datasets, modelos) | sonnet | *(raíz)* → `_handoffs/inventario.json` |
| `cacao-consolidador` | Copia solo lo relevante/funcional a esta carpeta | sonnet | `inventario.json` → `07_Pipeline_CacaoIA/` |
| `cacao-reportero` | Redacta reportes de handoff y bitácora | haiku | `*.json` → `04_reportes/`, `PROGRESO.md` |

**Cómo invocarlos** (desde Claude Code, en orden):
```
Usa el subagente cacao-analista para mapear el proyecto.
Luego cacao-consolidador para poblar 07_Pipeline_CacaoIA.
Cierra con cacao-reportero para generar el reporte de handoff.
```

---

## 📂 Estructura

```
07_Pipeline_CacaoIA/
├── 00_config/            config_cacao.yaml (rutas/clases) + utils_config.py
├── 01_motor_dinov2/      paso1_segmentar · paso2_embeddings_dinov2 · paso3_identificar · paso4_etiquetar
├── 02_color_embeddings/  color_embeddings_cacao · paleta_por_objeto (≥30) · montaje_1x30
├── 03_despliegue/        app_local.py (foto + cámara realtime) · exportar_movil.py (ONNX/TFLite/NCNN)
├── 04_reportes/          generar_reporte.py + reportes/paletas generados
├── _handoffs/            JSON de comunicación entre pasos y agentes
├── ejecutar_pipeline.py  ← orquestador (corre todo en orden)
├── requirements.txt · PROGRESO.md · .gitignore
```

---

## 🚀 Uso rápido

```bash
pip install -r requirements.txt

# Pipeline completo (segmenta, embeddings DINOv2, identifica, color, paletas, reporte)
python ejecutar_pipeline.py

# Prueba rápida con 20 imágenes
python ejecutar_pipeline.py --seg 20

# Solo la parte de color/paletas
python ejecutar_pipeline.py --solo color

# Despliegue local (subir foto + cámara en vivo)  -> http://localhost:5001
python 03_despliegue/app_local.py

# Exportar a móvil (Samsung S25)
python 03_despliegue/exportar_movil.py 320
```

---

## 🧠 Lógica del motor

1. **Segmentar** — YOLO `best.pt` (12 clases) detecta objetos; SAM refina la máscara y recorta cada objeto sobre fondo negro.
2. **Embeddings DINOv2** — vector de representación por objeto (huella para identificar sin re-entrenar).
3. **Identificar** — PCA + KMeans + silueta miden si la huella DINOv2 separa las hojas/variedades.
4. **Color / antocianina** — embedding de color interpretable (HSV + Lab + NGRDI + RGBVI + ratio antocianina) para el descriptor varietal UPOV C1.
5. **Paletas** — colores dominantes por objeto (≥30 imágenes) + montaje 1×30 del gradiente de pigmentación.
6. **Etiquetar / desplegar** — pre-etiquetado YOLO `.txt` y apps local/móvil.

## 🔜 Roadmap — nervaduras
La clase `Nervaduras_hojas_cacao` (id 5) es el siguiente foco: esqueletización + grafos (NetworkX) sobre las máscaras de hoja para extraer descriptores topológicos (nodos, aristas, ángulos de venas secundarias) → asignación a grupos genéticos (GP1–GP10). Ver `PROGRESO.md`.

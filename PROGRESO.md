# 📈 Bitácora de progreso — CacaoIA

Registro acumulativo por ciclos. Fuente para los commits en repos posteriores.
El agente `cacao-reportero` y `04_reportes/generar_reporte.py` agregan entradas aquí.

---

## Ciclo 0 — Consolidación inicial (2026-07-08)

**Hecho:**
- Creado el sistema de 3 subagentes persistentes (`analista`, `consolidador`, `reportero`) con handoff por archivos JSON para minimizar tokens.
- Consolidada la lógica del motor **DINOv2 + YOLO + SAM** en `01_motor_dinov2/` (segmentar → embeddings → identificar → etiquetar).
- Implementada la lógica de **color/antocianina**: `color_embeddings_cacao.py`, `paleta_por_objeto.py` (mínimo 30 imgs/objeto) y `montaje_1x30.py`.
- Añadido despliegue **local** (`app_local.py`, foto + cámara en vivo) y **móvil** (`exportar_movil.py` → ONNX/TFLite/NCNN, con copia a `03_App_S25`).
- Orquestador `ejecutar_pipeline.py` + generador de reporte + `.gitignore`/`requirements.txt` para repos.

**Handoff al siguiente ciclo:**
- Correr `python ejecutar_pipeline.py --seg 20` para validar el motor end-to-end y llenar `_handoffs/`.
- Verificar que cada clase de hoja tenga ≥30 recortes para las paletas.

**Pendiente / riesgos:**
- DINOv2 se descarga vía torch.hub en la primera corrida (requiere internet una vez).
- Ajustar `yolo_conf` en `00_config/config_cacao.yaml` según recall en campo.

---

## Próximo — Nervaduras (Ciclo 1)
- Esqueletización de máscaras de hoja + grafos NetworkX → descriptores topológicos.
- Cruce con embeddings DINOv2 + color para asignación a grupos genéticos GP1–GP10.

- **2026-07-08** | pipeline ejecutado | recortes=47 | silueta=0.055
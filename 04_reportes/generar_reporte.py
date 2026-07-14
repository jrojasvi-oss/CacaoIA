"""GENERADOR DE REPORTE CONSOLIDADO
Lee todos los JSON de _handoffs/ y produce un unico reporte Markdown legible +
actualiza PROGRESO.md (bitacora acumulativa para subir a repos).
Equivalente en codigo al trabajo del agente cacao-reportero.
"""
import sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_config"))
from utils_config import ruta_salida  # noqa: E402


def cargar(nombre):
    p = ruta_salida("_handoffs", nombre)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def main():
    fecha = datetime.date.today().isoformat()
    seg = cargar("segmentacion.json")
    emb = cargar("embeddings.json")
    motor = cargar("motor.json")
    color = cargar("color.json")
    pal = cargar("paletas.json")
    mov = cargar("export_movil.json")

    L = [f"# Reporte CacaoIA - {fecha}\n"]
    L.append("## 1. Segmentacion (YOLO+SAM)")
    L.append(f"- Recortes: **{seg['total_recortes']}** | SAM activo: {seg['sam_activo']}" if seg else "- pendiente")
    if seg:
        for c, n in sorted(seg["por_clase"].items(), key=lambda x: -x[1]):
            L.append(f"  - {c}: {n}")

    L.append("\n## 2. Identificacion (DINOv2)")
    if emb:
        L.append(f"- Embeddings: **{emb['n_embeddings']}** (modelo {emb['modelo']})")
    if motor:
        L.append(f"- Silueta KMeans: **{motor['silueta_kmeans']:.3f}** | Var 2D: {motor['var_explicada_2d']*100:.1f}%")
        L.append(f"- Grafica: `{Path(motor['grafica']).name}`")
    if not emb and not motor:
        L.append("- pendiente")

    L.append("\n## 3. Color / antocianina")
    if color:
        L.append(f"- Objetos analizados: **{color['n_objetos']}** (dim embedding {color['dim_embedding']})")
        L.append("- Promedios por clase (NGRDI / RGBVI / antocianina):")
        for c, v in color["promedios_por_clase"].items():
            L.append(f"  - {c}: {v['ngrdi']} / {v['rgbvi']} / {v['antocianina']}")
    else:
        L.append("- pendiente")

    L.append("\n## 4. Paletas (>=30 imgs por objeto)")
    if pal:
        for r in pal["resultados"]:
            estado = "OK" if r.get("cumple_min") else f"faltan ({r['n_imagenes']}/{pal['min_exigido']})"
            L.append(f"- {r['clase']}: {estado}")
    else:
        L.append("- pendiente")

    L.append("\n## 5. Despliegue movil")
    L.append(f"- Formatos: {list(mov['exportados'].keys())}" if mov else "- pendiente")

    reporte = ruta_salida("04_reportes", f"REPORTE_{fecha}.md")
    reporte.write_text("\n".join(L), encoding="utf-8")

    # Append a PROGRESO.md
    prog = ruta_salida("PROGRESO.md")
    linea = f"\n- **{fecha}** | pipeline ejecutado | recortes={seg['total_recortes'] if seg else 0}"
    linea += f" | silueta={motor['silueta_kmeans']:.3f}" if motor else ""
    with open(prog, "a", encoding="utf-8") as f:
        f.write(linea)

    print(f"[OK] Reporte -> {reporte}")


if __name__ == "__main__":
    main()

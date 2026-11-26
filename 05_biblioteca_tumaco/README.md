# Biblioteca digital · Cacao del suroccidente colombiano

Base abierta de la revisión de alcance (PRISMA-ScR) sobre el cacao de Tumaco, el Pacífico nariñense, el Cauca y el Valle del Cauca, con dos líneas temáticas añadidas en la fase 4: inteligencia artificial en cacao y sanidad del cultivo.

**Sitio (GitHub Pages):** https://jrojasvi-oss.github.io/CacaoIA/05_biblioteca_tumaco/ — catálogo con buscador y filtros de los 387 documentos.

## Estado (25 nov 2026)

- **387 documentos colombianos** incluidos de **3.277 registros identificados** en cuatro fases (18 a 24 nov 2026), más un corpus aparte de **246 estudios de IA en cacao** de otros países.
- Fase 1 Tumaco: 394 registros, 109 incluidos (Scopus, Web of Science, EBSCO, AGRIS, SciELO, SIRED, AGROSAVIA, Redalyc y literatura gris).
- Fase 2 Valle del Cauca y ruta: 378 registros, 106 incluidos (Scopus, AGRIS y búsqueda web dirigida).
- Fase 3 OpenAlex: 914 registros, 55 incluidos (vía Publish or Perish).
- Fase 4 IA y sanidad: 1.591 registros, 117 colombianos y 246 de IA mundial (OpenAlex vía Publish or Perish).
- Tamizaje inicial con IA (Claude, Anthropic) y verificación humana pendiente: todas las inclusiones y 20 % de las exclusiones (semilla 2026), y segundo revisor ciego en Rayyan con kappa de Cohen.

## Informes (`informes/`)

| Archivo | Qué es |
|---|---|
| `Informe_avance_revision_cacao_suroccidente.pdf` / `.docx` | Informe de avance: método, 35 ecuaciones de búsqueda, tabla y diagrama PRISMA, resultados, IA y sanidad, mapas de cadmio del CIAT, bibliometrix (versión con ecuaciones de la fase 4 corregidas) |
| `Graficos_bibliometricos_cacao_387.pdf` / `.docx` | Informe corto con 7 gráficos bibliométricos sobre los 387 documentos |
| `Catalogo_graficos_bibliometricos_cacao.pdf` | Catálogo de 38 gráficos numerados para elegir (mapas de calor, palabras, redes, tendencias, sanidad y distribución por departamento) |

## Datos (`data/`)

| Archivo | Qué es |
|---|---|
| `biblioteca_387.csv` | Las 387 fichas: id, año, autores, título, tipo, fuente, región, tema armonizado, diseño, hallazgo, enlace y fase |
| `Revision_cacao_ruta_suroccidental_datos.xlsx` | Libro de datos completo: fichas, bitácora de búsqueda, criterios, tamizajes y muestras de verificación |
| `busquedas.csv` | Bitácora de búsqueda de las fases 1 y 2 |
| `estudios.csv`, `complementarios.csv`, `ampliacion.csv`, `valle.csv` | Fichas por fase (1 y 2) |
| `tamizaje/` | Criterios, decisiones registro por registro, muestras de verificación del 20 %, RIS de cada consulta de OpenAlex (`openalex/`, `fase4/`) y RIS para Zotero |
| `bibliometrix/` | Script de R, datos de entrada (`M.csv` 270 y `M387.csv` 387), tablas y figuras |
| `bibliometrix/graficas_387/` | Gráficos complementarios del informe corto |
| `bibliometrix/catalogo_graficos/` | PNG de los 38 gráficos del catálogo, scripts de Python y clasificación de los documentos de sanidad |
| `figuras_informe/` | Figuras nuevas del informe de avance (PRISMA, años, regiones, IA, sanidad) |
| `fuentes_datos.csv` | Fuentes de datos secundarias |

## Herramientas

Python 3 (csv, json, re, unicodedata, openpyxl, matplotlib, networkx, wordcloud, plotly, adjustText), R 4.3 con bibliometrix 4.3.0, Publish or Perish 8 (OpenAlex), Zotero, Rayyan, servicios ArcGIS del geovisor Clima-LoCa (Alianza Bioversity-CIAT) y Claude Opus 5.5 (Anthropic) para el tamizaje inicial y la redacción, con verificación del autor.

## Autor

Juan David Rojas Villafañe · Ingeniería Agronómica, Universidad Nacional de Colombia, sede Palmira.

## Licencia

Metadatos y código: CC BY 4.0.

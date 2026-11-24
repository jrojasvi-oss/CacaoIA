# Biblioteca digital · Cacao de Tumaco

Base abierta de la revisión de alcance (PRISMA-ScR) sobre el cacao nativo fino y de aroma de Tumaco y el Pacífico nariñense.

**Sitio (GitHub Pages):** https://jrojasvi-oss.github.io/CacaoIA/05_biblioteca_tumaco/

## Contenido

- `index.html`: catálogo con buscador y filtros, modelo de proceso e inventario de fuentes de datos.
- `docs/Cacao_Tumaco_modelos_investigacion.pdf` y `.docx`: documento completo de síntesis y modelos de investigación propuestos.
- `data/Revision_cacao_Tumaco_datos.xlsx`: base de datos completa (estudios, complementarios, actores, búsquedas y conteo PRISMA).
- `data/estudios.csv`: 56 documentos incluidos en el conteo PRISMA (D = bases indexadas, G = literatura gris).
- `data/complementarios.csv`: búsqueda complementaria (C01–C05 entran al conteo; C06 y C07 son contexto).
- `data/ampliacion.csv`: 48 documentos de la ampliación del 23 nov 2026 (AGRIS, SciELO, SIRED, AGROSAVIA).
- `data/valle.csv`: 106 documentos de la fase Valle del Cauca / ruta suroccidental (Scopus, AGRIS y búsquedas dirigidas).
- `data/Revision_cacao_ruta_suroccidental_datos.xlsx` y `docs/Ruta_suroccidental_cacao.pdf|docx`: base completa (215) y documento de la ruta suroccidental.
- `data/busquedas.csv`: bitácora de búsqueda (bases, fecha, cadenas, registros).
- `data/fuentes_datos.csv`: fuentes de datos secundarias.
- `scripts/construir_pagina.py`: genera `index.html` a partir de los CSV.

## Método

**Total actual: 215 documentos** (109 de Tumaco + 106 de la ruta suroccidental). 
Búsqueda del 18 de noviembre de 2026 en Scopus, Web of Science y EBSCO (acceso institucional, Universidad Nacional de Colombia). 78 registros identificados, 23 duplicados, 55 tamizados, 11 excluidos, 44 incluidos desde bases y 12 de literatura gris: 56 documentos. Ampliación (23 nov 2026): AGRIS 210, SciELO 14, SIRED 70 y AGROSAVIA 12 registros; 203 revisados, 48 nuevos incluidos; más 5 complementarios. Fase Valle del Cauca (23 nov 2026): Scopus 115 únicos y AGRIS 67, con 37 y 18 incluidos, más 16 fuentes de búsquedas dirigidas; segunda ronda temática en AGRIS (24 nov): 196 únicos, 35 incluidos. Total fase: 106 nuevos. Criterios, decisiones de tamizaje, muestra de verificación y archivo RIS en `data/tamizaje/`. La extracción, el tamizaje y la codificación se hicieron con apoyo de inteligencia artificial (Claude, Anthropic), con verificación del autor.

## Autor

Juan David Rojas Villafañe · Ingeniería Agronómica, Universidad Nacional de Colombia, Sede Palmira.

## Licencia

Metadatos y código: CC BY 4.0.

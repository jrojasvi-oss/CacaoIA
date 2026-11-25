import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
import textwrap
F=[('Mapas de calor','g01_calor_tema_anio','Tema por año (2005–2026)','Cuántos documentos de cada tema salen cada año; muestra el salto reciente del cadmio y la IA.'),
('Mapas de calor','g02_calor_tema_periodo','Tema por periodo','La misma lectura agrupada en seis periodos; más fácil de leer impresa.'),
('Mapas de calor','g03_calor_tema_region','Tema por región','Qué se ha estudiado en cada región; Tumaco en sistemas, otras regiones en sanidad, el Valle casi vacío.'),
('Mapas de calor','g04_calor_region_periodo','Región por periodo','Cómo creció la producción de cada región en el tiempo; el Valle no despega.'),
('Mapas de calor','g05_calor_coocurrencia','Co-ocurrencia de las 22 palabras más frecuentes','Cuántos títulos comparten cada par de palabras; los bloques oscuros son temas que van juntos.'),
('Mapas de calor','g06_calor_autores_tema','Autores por tema','Los 20 autores con más documentos y en qué temas publican.'),
('Mapas de calor','g07_calor_tipo_periodo','Tipo de documento por periodo','Artículos, tesis, informes y otros a lo largo del tiempo.'),
('Mapas de calor','g08_calor_ia_organo_tarea','IA en cacao: órgano por tarea (246 estudios, mundo)','Qué órgano de la planta se usa para cada tarea; la hoja casi solo se usa para enfermedades.'),
('Mapas de palabras','g17_nube_general','Nube de palabras general','Las 120 palabras más frecuentes en los títulos de los 387 documentos.'),
('Mapas de palabras','g11_nubes_por_tema','Nubes de palabras por tema','Cuatro nubes: sanidad, suelo y cadmio, genética y sistemas; cada tema con su vocabulario.'),
('Mapas de palabras','g18_treemap_bigramas','Mapa de árbol de pares de palabras','Los 25 pares de palabras más frecuentes; el área es proporcional a la frecuencia.'),
('Mapas de palabras','g14_bigramas_top20','Los 20 pares de palabras más frecuentes','La misma información del mapa de árbol en barras, más precisa para comparar.'),
('Redes','g09_red_coocurrencia','Red de co-ocurrencia de palabras','Palabras unidas cuando aparecen juntas en al menos dos títulos; los colores son comunidades temáticas.'),
('Redes','g10_red_coautoria','Red de coautoría','Los 45 autores más productivos y con quién publican; muestra grupos de trabajo aislados.'),
('Tendencias','g19_temas_tendencia','Temas en tendencia','Año en que se usa cada palabra; arriba lo antiguo, abajo lo reciente.'),
('Tendencias','g12_produccion_por_tema','Producción anual por tema (2000–2026)','Diez pequeños gráficos, uno por tema, con la misma escala para comparar.'),
('Tendencias','g13_antes_despues_2020','Antes y después de 2020','Documentos por tema antes de 2020 y desde 2020; muestra qué temas crecieron y cuáles se estancaron.'),
('Tendencias','g16_lotka','Productividad de autores (ley de Lotka)','La mayoría de autores publica un solo documento; la curva es la ley de Lotka.'),
('Estructura','g20_estructura_conceptual','Estructura conceptual (MCA)','Plano donde las palabras que salen juntas quedan cerca; cuatro grupos temáticos.'),
('Estructura','g21_tres_campos','Tres campos: autor, tema y región','Flujos de los 15 autores más productivos hacia sus temas y regiones.'),
('Estructura','g15_sunburst_tema_region','Anillos: tema y región','Círculo interno con los temas y externo con las regiones de cada tema.'),
('Sanidad: plagas y enfermedades','g22_problemas_sanitarios','Problemas sanitarios estudiados en Colombia','Documentos por enfermedad o plaga (109 documentos de sanidad); la moniliasis domina con 80.'),
('Sanidad: plagas y enfermedades','g31_insectos_plaga','Insectos plaga estudiados','Carmenta, Monalonion, Xyleborus y Antiteuchus: las plagas tienen muy pocos trabajos en la biblioteca.'),
('Sanidad: plagas y enfermedades','g25_calor_problema_periodo','Mapa de calor: problema sanitario por periodo','Cuándo se estudió cada enfermedad o plaga; Phytophthora crece desde 2015.'),
('Sanidad: plagas y enfermedades','g27_calor_problema_region','Mapa de calor: problema sanitario por región','Dónde se estudió cada problema; casi nada de sanidad en Tumaco y poco en el Valle.'),
('Sanidad: modos de manejo','g23_modos_manejo','Modos de manejo','Diagnóstico, control biológico, cultural, genético, químico, integrado, extractos e IA.'),
('Sanidad: modos de manejo','g24_calor_problema_manejo','Mapa de calor: problema sanitario por modo de manejo','Qué tipo de manejo se ha probado para cada enfermedad o plaga.'),
('Sanidad: modos de manejo','g26_calor_manejo_periodo','Mapa de calor: modo de manejo por periodo','Cómo cambió el manejo estudiado; lo biológico sube desde 2015 y los extractos desde 2020.'),
('Sanidad: modos de manejo','g28_calor_agente_problema','Mapa de calor: agente de control biológico por problema','Trichoderma, Bacillus, Clonostachys, endófitos y entomopatógenos frente a cada problema en Colombia.'),
('Sanidad: modos de manejo','g29_colombia_vs_mundo_biocontrol','Control biológico: Colombia frente a otros países','Registros que nombran el agente y el patógeno; Bacillus contra Phytophthora tiene 1 en Colombia y 18 afuera.'),
('Sanidad: modos de manejo','g30_sankey_problema_manejo_region','Flujos: problema sanitario, manejo y región','Diagrama de tres columnas que conecta cada problema con su manejo y la región donde se estudió.'),
('Sanidad: modos de manejo','g32_red_palabras_sanidad','Red de palabras de los títulos de sanidad','Palabras de sanidad que aparecen juntas en los títulos, agrupadas por comunidades.')]
with PdfPages('g15/Catalogo_graficos_bibliometricos_cacao.pdf') as pdf:
    fig=plt.figure(figsize=(11,8.5));fig.text(.07,.82,'Catálogo de gráficos bibliométricos',fontsize=24,color='#191919',weight='bold')
    fig.text(.07,.76,'Biblioteca de cacao del suroccidente colombiano · 387 documentos · 25 nov 2026',fontsize=13,color='#666666')
    fig.text(.07,.715,'Elige por número los gráficos que quieres en el informe. Del 22 al 32, sanidad: plagas, enfermedades y modos de manejo.',fontsize=12,color='#191919')
    y=.685;cur=None
    for i,(g,_,t,_) in enumerate(F,1):
        if g!=cur:
            y-=.004;fig.text(.07,y,g,fontsize=10,weight='bold',color='#257de0');y-=.019;cur=g
        fig.text(.09,y,f'{i:>2}.  {t}',fontsize=8.6,color='#191919');y-=.0148
    pdf.savefig(fig);plt.close(fig)
    for i,(g,f,t,d) in enumerate(F,1):
        im=Image.open(f'g15/{f}.png')
        fig=plt.figure(figsize=(11,8.5))
        fig.text(.05,.94,f'{i}',fontsize=26,weight='bold',color='#257de0')
        fig.text(.11,.945,t,fontsize=16,weight='bold',color='#191919');fig.text(.11,.915,g,fontsize=10,color='#666666')
        fig.text(.05,.87,'\n'.join(textwrap.wrap(d,130)),fontsize=11,color='#191919')
        ax=fig.add_axes([.04,.03,.92,.81]);ax.imshow(im);ax.axis('off')
        pdf.savefig(fig,dpi=150);plt.close(fig)
print('ok')

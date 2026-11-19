import csv, json, html
rows=list(csv.DictReader(open('/home/claude/tumaco/estudios.csv',encoding='utf-8')))+list(csv.DictReader(open('/home/claude/tumaco/complementarios.csv',encoding='utf-8')))
data=json.dumps(rows,ensure_ascii=False).replace('</','<\\/')
page=r'''<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Biblioteca digital · Cacao de Tumaco</title>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#faf8f4;--ink:#2a2420;--mute:#6b625a;--line:#e4ddd3;--acc:#7a3e1d;--acc2:#b9783f;--card:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#1b1816;--ink:#ece6df;--mute:#a69d94;--line:#3a332e;--acc:#e0a070;--acc2:#c78a52;--card:#24201d}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 Inter,system-ui,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 60px}
h1{font-family:"Source Serif 4",Georgia,serif;font-size:30px;margin:0 0 4px;color:var(--acc)}
h2{font-family:"Source Serif 4",Georgia,serif;font-size:21px;margin:36px 0 10px}
.sub{color:var(--mute);margin:0 0 18px}
nav a{color:var(--acc);margin-right:16px;text-decoration:none;font-weight:500}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:18px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:24px;color:var(--acc)}.kpi span{color:var(--mute);font-size:13px}
.flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;counter-reset:s}
.step{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--acc2);border-radius:8px;padding:12px;counter-increment:s}
.step h3{margin:0 0 6px;font-size:15px}.step h3:before{content:counter(s) ". ";color:var(--acc)}
.step p{margin:0;font-size:13px;color:var(--mute)}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
input,select,button{font:inherit;padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink)}
input{flex:1;min-width:220px}button{cursor:pointer;background:var(--acc);color:#fff;border:none}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:13.5px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:color-mix(in srgb,var(--acc2) 14%,var(--card));cursor:pointer;white-space:nowrap}
tr.r:hover{background:color-mix(in srgb,var(--acc2) 7%,var(--card))}
.tag{display:inline-block;font-size:11.5px;padding:2px 7px;border-radius:20px;background:color-mix(in srgb,var(--acc2) 18%,transparent);color:var(--ink)}
.det{color:var(--mute);font-size:13px}
.bars div{display:flex;align-items:center;gap:8px;margin:4px 0;font-size:13px}.bars i{display:block;height:12px;background:var(--acc2);border-radius:3px}
pre{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;overflow:auto;font-size:12.5px}
.note{font-size:13px;color:var(--mute)}
</style></head><body><div class="wrap">
<h1>Biblioteca digital · Cacao de Tumaco</h1>
<p class="sub">Base abierta de la revisión de alcance (PRISMA-ScR) sobre cacao en Tumaco y el Pacífico nariñense: 56 documentos del conteo PRISMA más registros de búsqueda complementaria, y un inventario de fuentes de datos secundarias.</p>
<nav><a href="#catalogo">Catálogo</a><a href="#datos">Fuentes de datos</a><a href="#proceso">Modelo de proceso</a><a href="#replicar">Cómo publicarla</a></nav>
<div class="kpis" id="kpis"></div>
<h2 id="catalogo">Catálogo</h2>
<div class="filters">
<input id="q" placeholder="Buscar en título, autor, hallazgo…">
<select id="ftema"><option value="">Todos los temas</option></select>
<select id="ftipo"><option value="">Todos los tipos</option></select>
<select id="fzona"><option value="">Todas las zonas</option></select>
<select id="forig"><option value="">Todos los orígenes</option><option value="P">Conteo PRISMA (D/G)</option><option value="C">Búsqueda complementaria (C)</option></select>
<button id="copy">Copiar CSV filtrado</button>
</div>
<p class="note" id="count"></p>
<div style="overflow:auto"><table><thead><tr><th data-k="id">ID</th><th data-k="anio">Año</th><th data-k="autor">Autores</th><th data-k="titulo">Título y hallazgo</th><th data-k="tema">Tema</th><th data-k="tipo">Tipo</th><th data-k="zona">Zona</th></tr></thead><tbody id="tb"></tbody></table></div>
<h2 id="datos">Fuentes de datos secundarias</h2>
<p>Datos abiertos para cruzar con la literatura y con el ensayo: sirven para ubicar las fincas, describir el contexto y comparar contra la tendencia municipal.</p>
<div style="overflow:auto"><table><thead><tr><th>Fuente</th><th>Qué trae</th><th>Uso en Tumaco</th></tr></thead><tbody>
<tr><td><b>EVA – Evaluaciones Agropecuarias Municipales (UPRA)</b></td><td>Área sembrada, cosechada, producción y rendimiento por municipio y año</td><td>Serie histórica de Tumaco; contexto y tendencia frente al ensayo</td></tr>
<tr><td><b>SIPRA – Zonificación de aptitud para cacao comercial (UPRA, 1:100.000)</b></td><td>Aptitud alta, media, baja y no apta; frontera agrícola</td><td>Estratificar fincas por aptitud; ubicar parcelas</td></tr>
<tr><td><b>Agronet (MADR)</b></td><td>Series nacionales y departamentales de cacao, precios</td><td>Comparar Nariño con el país</td></tr>
<tr><td><b>Censo Nacional Agropecuario 2014 (DANE, microdatos)</b></td><td>Unidades productivas, área, prácticas, asistencia técnica</td><td>Marco muestral y línea base de prácticas</td></tr>
<tr><td><b>SIPSA (DANE) y precios Fedecacao</b></td><td>Precios de insumos y de cacao en grano</td><td>Análisis económico del ensayo</td></tr>
<tr><td><b>IDEAM / boletines agroclimáticos de Nariño</b></td><td>Lluvia, temperatura, pronóstico ENOS</td><td>Covariables climáticas y calendario de labores</td></tr>
<tr><td><b>IGAC – suelos 1:100.000 y SoilGrids</b></td><td>Unidades de suelo, pH, textura, carbono</td><td>Covariables de suelo por finca</td></tr>
<tr><td><b>Sentinel-2 / Global Forest Watch</b></td><td>NDVI, cobertura de dosel, pérdida de bosque</td><td>Sombra y cobertura por finca; cambio de uso</td></tr>
<tr><td><b>Repositorios: SIRED (Udenar), AGROSAVIA, AGRIS, SciELO, Redalyc</b></td><td>Tesis, informes y artículos regionales</td><td>Ampliar la biblioteca (registros C)</td></tr>
</tbody></table></div>
<h2>Distribución por tema</h2><div class="bars" id="bars"></div>
<h2 id="proceso">Modelo de proceso de la biblioteca</h2>
<p>El ciclo completo, desde la búsqueda hasta la publicación y la actualización. Cada etapa deja un archivo versionado, así cualquiera puede auditar o repetir la biblioteca.</p>
<div class="flow">
<div class="step"><h3>Protocolo</h3><p>Pregunta PCC, criterios de inclusión y cadenas de búsqueda. Se registra en OSF antes de tamizar. Salida: protocolo.md + ID OSF.</p></div>
<div class="step"><h3>Captura</h3><p>Exportaciones RIS/CSV de Scopus, WoS y EBSCO (proxy UNAL), más AGRIS, SIRED, AGROSAVIA y Fedecacao. Bitácora con fecha, cadena y conteo.</p></div>
<div class="step"><h3>Depuración</h3><p>Unir fuentes, normalizar DOI y títulos, quitar duplicados con un script (Python/SQL). Salida: registros_unicos.csv.</p></div>
<div class="step"><h3>Tamizaje</h3><p>Título/resumen y luego texto completo, en Rayyan, con dos revisores (kappa) y razón de exclusión. Salida: tamizaje.csv y diagrama PRISMA.</p></div>
<div class="step"><h3>Codificación</h3><p>Ficha común: tema, zona, diseño, variables, hallazgo y enlace. Se pilotea con 5 estudios. Salida: estudios.csv (la fuente de verdad).</p></div>
<div class="step"><h3>Curaduría</h3><p>Validar enlaces y DOI, marcar el acceso (abierto o cerrado), adjuntar PDF solo si la licencia lo permite. Control de calidad por muestreo.</p></div>
<div class="step"><h3>Publicación</h3><p>Un script genera esta página desde estudios.csv; se publica en GitHub Pages y la versión se archiva en Zenodo con DOI.</p></div>
<div class="step"><h3>Actualización</h3><p>Búsqueda de vigilancia cada 6 meses con las mismas cadenas. Lo nuevo entra por el mismo flujo, con fecha de corte visible y changelog.</p></div>
</div>
<p class="note">Roles: <b>curador principal</b> (búsqueda y codificación), <b>segundo revisor</b> (tamizaje y 20 % de la codificación), <b>mantenedor</b> (script y publicación). Gobernanza: licencia CC BY 4.0 para metadatos; se acepta aporte externo por formulario o pull request, con revisión del curador.</p>
<h2 id="replicar">Cómo publicarla en GitHub Pages</h2>
<pre>biblioteca-cacao-tumaco/
├── data/
│   ├── estudios.csv          # 56 registros PRISMA (fuente de verdad)
│   ├── complementarios.csv   # búsqueda complementaria
│   ├── fuentes_datos.csv     # datos secundarios
│   ├── busquedas.csv         # bitácora PRISMA-S
│   └── tamizaje.csv          # decisiones y razones de exclusión
├── protocolo/protocolo.md    # registrado en OSF
├── scripts/
│   ├── depurar.py            # unir + quitar duplicados
│   └── construir_pagina.py   # estudios.csv → index.html
├── index.html                # esta página
├── CHANGELOG.md
└── LICENSE (CC BY 4.0)</pre>
<p class="note">Activas GitHub Pages en la rama main, carpeta raíz. Cada versión publicada se conecta a Zenodo para tener un DOI citable. Los registros D y G salen de la hoja de la revisión; los C, de una búsqueda complementaria en SIRED, SciELO y repositorios, todavía fuera del conteo PRISMA. Fecha de corte: noviembre de 2026.</p>
</div>
<script>
const D=__DATA__;
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function opts(sel,k){[...new Set(D.map(r=>r[k]))].sort().forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;$(sel).appendChild(o)})}
opts('#ftema','tema');opts('#ftipo','tipo');opts('#fzona','zona');
const yrs=D.map(r=>+r.anio).filter(Boolean);
$('#kpis').innerHTML=[[D.filter(r=>r.id[0]!='C').length,'en el conteo PRISMA'],[D.filter(r=>r.id[0]=='C').length,'de búsqueda complementaria'],[D.filter(r=>r.id.startsWith('D')).length,'de bases indexadas'],[D.filter(r=>r.id.startsWith('G')).length,'de literatura gris'],[Math.min(...yrs)+'–'+Math.max(...yrs),'años cubiertos'],[D.filter(r=>/Tesis/.test(r.tipo)).length,'tesis']].map(([b,s])=>`<div class="kpi"><b>${b}</b><span>${s}</span></div>`).join('');
let sk='anio',sd=-1,cur=[];
function render(){const o=$('#forig').value,q=$('#q').value.toLowerCase(),t=$('#ftema').value,ti=$('#ftipo').value,z=$('#fzona').value;
cur=D.filter(r=>(!o||(o=='C'?r.id[0]=='C':r.id[0]!='C'))&&(!t||r.tema==t)&&(!ti||r.tipo==ti)&&(!z||r.zona==z)&&(!q||(r.titulo+' '+r.autor+' '+r.hallazgo+' '+r.diseno).toLowerCase().includes(q)));
cur.sort((a,b)=>{const x=a[sk],y=b[sk];return (isNaN(x)?String(x).localeCompare(y):x-y)*sd});
$('#count').textContent=cur.length+' de '+D.length+' documentos';
$('#tb').innerHTML=cur.map(r=>{const l=/^https?:/.test(r.enlace)?`<a href="${esc(r.enlace)}">${esc(r.enlace.slice(0,60))}</a>`:esc(r.enlace);
return `<tr class="r"><td>${esc(r.id)}</td><td>${esc(r.anio)}</td><td>${esc(r.autor)}</td><td><b>${esc(r.titulo)}</b><div class="det">${esc(r.hallazgo)}</div><div class="det"><i>${esc(r.diseno)}</i> · ${l}</div></td><td><span class="tag">${esc(r.tema)}</span></td><td>${esc(r.tipo)}</td><td>${esc(r.zona)}</td></tr>`}).join('');}
document.querySelectorAll('th').forEach(th=>th.onclick=()=>{const k=th.dataset.k;sd=(sk==k)?-sd:1;sk=k;render()});
['#q','#ftema','#ftipo','#fzona','#forig'].forEach(s=>$(s).addEventListener('input',render));
$('#copy').onclick=async()=>{const ks=Object.keys(D[0]);const csv=[ks.join(',')].concat(cur.map(r=>ks.map(k=>'"'+String(r[k]??'').replace(/"/g,'""')+'"').join(','))).join('\n');
try{await navigator.clipboard.writeText(csv);$('#copy').textContent='Copiado ✓'}catch(e){$('#copy').textContent='No se pudo copiar'}setTimeout(()=>$('#copy').textContent='Copiar CSV filtrado',1800)};
const c={};D.forEach(r=>c[r.tema]=(c[r.tema]||0)+1);const mx=Math.max(...Object.values(c));
$('#bars').innerHTML=Object.entries(c).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`<div><span style="width:260px">${esc(k)}</span><i style="width:${v/mx*300}px"></i><b>${v}</b></div>`).join('');
render();
</script></body></html>'''
open('/home/claude/tumaco/biblioteca_cacao_tumaco.html','w',encoding='utf-8').write(page.replace('__DATA__',data))
print('ok')

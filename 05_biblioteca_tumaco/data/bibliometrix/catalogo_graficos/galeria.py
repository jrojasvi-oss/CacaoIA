import csv,collections,re,itertools,matplotlib,openpyxl
matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np, networkx as nx
from wordcloud import WordCloud
import plotly.graph_objects as go
from adjustText import adjust_text
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
T='#191919';G='#666666';B='#257de0';O='#f47230'
CM='YlGnBu'
R=list(csv.DictReader(open('M387.csv')))
def tc(s): return s[:1].upper()+s[1:].lower()
SHORT={'SANIDAD':'Sanidad','SISTEMAS Y MANEJO':'Sistemas y manejo','SUELO, MICROBIOTA Y CADMIO':'Suelo y cadmio','CADENA Y TERRITORIO':'Cadena y territorio','GENETICA, TAXONOMIA Y CARACTERES':'Genética y caracteres','POSCOSECHA Y CALIDAD':'Poscosecha y calidad','MEJORAMIENTO Y SELECCION':'Mejoramiento','IA Y FENOTIPADO DIGITAL':'IA y fenotipado','PATRONES Y PROPAGACION':'Patrones y propagación','HISTORIA Y RUTA':'Historia y ruta'}
RS={'TUMACO Y PACIFICO NARINENSE':'Tumaco y Pacífico','OTRAS REGIONES DE COLOMBIA':'Otras regiones','COLOMBIA (NACIONAL)':'Nacional','VALLE DEL CAUCA':'Valle del Cauca','REGIONAL (FUERA DE COLOMBIA INCLUIDO)':'Regional','CAUCA Y SUROCCIDENTE':'Cauca','NARINO ANDINO Y DEPARTAMENTAL':'Nariño andino'}
temas=[t for t,_ in collections.Counter(r['DE'] for r in R).most_common()]
regs=[t for t,_ in collections.Counter(r['ID'] for r in R).most_common()]
def yr(r):
    try:return int(float(r['PY']))
    except:return None
SW=set("de del la las el los en y con para por una un al sus su a o e u the of and in on for with to from by an as its at is are using use between under into que se lo le como sobre entre sin desde hacia mediante bajo durante tras ante segun dos tres caso estudio study cacao theobroma cocoa colombia colombian colombiano colombiana municipio departamento evaluacion evaluation analisis analysis efecto effect effects uso spp cif par san pod rot sas new based frente contra luis".split())
def toks(r): return [w.lower() for w in r['TI'].split() if w.lower() not in SW and len(w)>2 and not w.isdigit()]
D={r['UT']:set(toks(r)) for r in R}
def clean(ax,grid='y'):
    for s in ['top','right']: ax.spines[s].set_visible(False)
    ax.grid(axis=grid,color='#eeeeee');ax.set_axisbelow(True);ax.tick_params(colors=G)
def heat(H,rows,cols,fn,xl='',yl='',w=None,h=None,rot=0,fs=9):
    fig,ax=plt.subplots(figsize=(w or 0.9*len(cols)+3.5,h or 0.42*len(rows)+1.4))
    im=ax.imshow(H,cmap=CM,aspect='auto',vmin=0)
    m=H.max()
    for i in range(H.shape[0]):
        for j in range(H.shape[1]):
            v=H[i,j]
            if v: ax.text(j,i,str(v),ha='center',va='center',fontsize=fs,color='white' if v>m*.5 else T)
    ax.set_xticks(range(len(cols)));ax.set_xticklabels(cols,fontsize=8.5,color=G,rotation=rot,ha='right' if rot else 'center')
    ax.set_yticks(range(len(rows)));ax.set_yticklabels(rows,fontsize=9,color=G)
    ax.set_xticks(np.arange(-.5,len(cols)),minor=True);ax.set_yticks(np.arange(-.5,len(rows)),minor=True);ax.grid(which='minor',color='white',lw=1.5);ax.tick_params(which='both',length=0)
    for s in ax.spines.values(): s.set_visible(False)
    cb=plt.colorbar(im,ax=ax,fraction=.03,pad=.02);cb.outline.set_visible(False);cb.ax.tick_params(labelsize=8,colors=G);cb.set_label('Documentos',color=G,fontsize=8.5)
    ax.set_xlabel(xl,color=G);ax.set_ylabel(yl,color=G);plt.tight_layout();plt.savefig(fn,dpi=170);plt.close()
# G01 calor tema x año (2005-2026)
yrs=list(range(2005,2027))
H=np.zeros((len(temas),len(yrs)),int)
for r in R:
    y=yr(r)
    if y and y>=2005: H[temas.index(r['DE']),yrs.index(y)]+=1
heat(H,[SHORT[t] for t in temas],[str(y) for y in yrs],'g15/g01_calor_tema_anio.png',rot=45,w=13,fs=8)
# G02 calor tema x periodo
per=[('<2000',0,1999),('2000–09',2000,2009),('2010–14',2010,2014),('2015–19',2015,2019),('2020–22',2020,2022),('2023–26',2023,2026)]
H=np.zeros((len(temas),len(per)),int)
for r in R:
    y=yr(r)
    if y is None: continue
    for j,(_,a,b) in enumerate(per):
        if a<=y<=b:H[temas.index(r['DE']),j]+=1
heat(H,[SHORT[t] for t in temas],[p[0] for p in per],'g15/g02_calor_tema_periodo.png',xl='Periodo')
# G03 calor tema x region
H=np.zeros((len(temas),len(regs)),int)
for r in R: H[temas.index(r['DE']),regs.index(r['ID'])]+=1
heat(H,[SHORT[t] for t in temas],[RS[x] for x in regs],'g15/g03_calor_tema_region.png',rot=30)
# G04 calor region x periodo
H=np.zeros((len(regs),len(per)),int)
for r in R:
    y=yr(r)
    if y is None: continue
    for j,(_,a,b) in enumerate(per):
        if a<=y<=b:H[regs.index(r['ID']),j]+=1
heat(H,[RS[x] for x in regs],[p[0] for p in per],'g15/g04_calor_region_periodo.png',xl='Periodo')
# G05 coocurrencia terminos
tf=collections.Counter(w for s in D.values() for w in s)
top=[w for w,_ in tf.most_common(22)]
C=np.zeros((len(top),len(top)),int)
for s in D.values():
    for a,b in itertools.combinations([w for w in top if w in s],2):
        i,j=top.index(a),top.index(b);C[i,j]+=1;C[j,i]+=1
heat(C,top,top,'g15/g05_calor_coocurrencia.png',rot=60,w=11,h=9.5,fs=7.5)
# G06 autores x tema
ac=collections.Counter(a for r in R for a in r['AU'].split(';') if a and a not in ('AGROSAVIA','CORPOICA','ANONIMO'))
ta=[a for a,_ in ac.most_common(20)]
H=np.zeros((len(ta),len(temas)),int)
for r in R:
    for a in set(r['AU'].split(';')):
        if a in ta: H[ta.index(a),temas.index(r['DE'])]+=1
heat(H,[a.title() for a in ta],[SHORT[t] for t in temas],'g15/g06_calor_autores_tema.png',rot=35,w=10,h=8)
# G07 tipo x periodo
import unicodedata
def tnorm(t):
    t=unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode().upper()
    if 'ARTIC' in t or 'ARTICLE' in t or 'PREPRINT' in t or 'REVISION' in t or 'DATA-PAPER' in t: return 'Artículo'
    if 'TESIS' in t or 'GRADO' in t or 'MONOGRAF' in t: return 'Tesis o trabajo de grado'
    if 'INFORME' in t or 'MANUAL' in t or 'CARTILLA' in t or 'FICHA' in t or 'HERRAMIENTA' in t: return 'Informe, cartilla o manual'
    if 'LIBRO' in t or 'CAPITULO' in t or 'BOOK' in t: return 'Libro o capítulo'
    if 'PONENCIA' in t or 'CONFERENCE' in t or 'MEMORIA' in t: return 'Ponencia o memoria'
    return 'Otros'
for r in R: r['DT2']=tnorm(r['DT'])
tipos=[t for t,_ in collections.Counter(r['DT2'] for r in R).most_common()]
H=np.zeros((len(tipos),len(per)),int)
for r in R:
    y=yr(r)
    if y is None: continue
    for j,(_,a,b) in enumerate(per):
        if a<=y<=b:H[tipos.index(r['DT2']),j]+=1
heat(H,tipos,[p[0] for p in per],'g15/g07_calor_tipo_periodo.png',xl='Periodo')
# G08 IA organo x tarea
wb=openpyxl.load_workbook('/home/claude/tumaco/v3/Revision_cacao_ruta_suroccidental_datos.xlsx',read_only=True,data_only=True)
ia=list(wb['IA en cacao (mundial)'].iter_rows(values_only=True))[1:]
org=[t for t,_ in collections.Counter(r[5] for r in ia).most_common()];tar=[t for t,_ in collections.Counter(r[6] for r in ia).most_common()]
H=np.zeros((len(org),len(tar)),int)
for r in ia: H[org.index(r[5]),tar.index(r[6])]+=1
heat(H,org,tar,'g15/g08_calor_ia_organo_tarea.png',rot=30,w=10)
# G09 red coocurrencia terminos
top40=[w for w,_ in tf.most_common(40)]
Gx=nx.Graph()
for s in D.values():
    for a,b in itertools.combinations(sorted(w for w in top40 if w in s),2):
        Gx.add_edge(a,b,weight=Gx[a][b]['weight']+1 if Gx.has_edge(a,b) else 1)
Gx.remove_edges_from([(a,b) for a,b,d in Gx.edges(data=True) if d['weight']<2])
Gx.remove_nodes_from(list(nx.isolates(Gx)))
comm=nx.community.louvain_communities(Gx,weight='weight',seed=3)
PAL=[B,O,'#00b894','#6a4ce2','#f2a600','#ee7fac','#008a17']
col={n:PAL[i%7] for i,c in enumerate(comm) for n in c}
pos=nx.spring_layout(Gx,weight='weight',seed=4,k=.9)
fig,ax=plt.subplots(figsize=(11,8.5))
nx.draw_networkx_edges(Gx,pos,width=[.4+d['weight']*.25 for *_,d in Gx.edges(data=True)],edge_color='#cccccc',ax=ax)
nx.draw_networkx_nodes(Gx,pos,node_size=[tf[n]*14 for n in Gx],node_color=[col[n] for n in Gx],edgecolors='white',ax=ax)
txt=[ax.text(*pos[n],n,fontsize=9,color=T) for n in Gx];adjust_text(txt,ax=ax)
ax.axis('off');plt.tight_layout();plt.savefig('g15/g09_red_coocurrencia.png',dpi=170);plt.close()
# G10 red coautoria
GA=nx.Graph()
for r in R:
    aus=sorted(set(a for a in r['AU'].split(';') if a and a not in ('AGROSAVIA','CORPOICA','ANONIMO')))
    for a in aus: GA.add_node(a)
    for a,b in itertools.combinations(aus,2): GA.add_edge(a,b,weight=GA[a][b]['weight']+1 if GA.has_edge(a,b) else 1)
deg=dict(GA.degree(weight='weight'));keep=sorted(deg,key=lambda n:-ac.get(n,0)*10-deg[n])[:45]
H2=GA.subgraph(keep).copy();H2.remove_nodes_from(list(nx.isolates(H2)))
comm=nx.community.louvain_communities(H2,seed=3);col={n:PAL[i%7] for i,c in enumerate(comm) for n in c}
pos=nx.spring_layout(H2,seed=5,k=.6)
fig,ax=plt.subplots(figsize=(11,8.5))
nx.draw_networkx_edges(H2,pos,edge_color='#cccccc',width=[.5+d['weight']*.4 for *_,d in H2.edges(data=True)],ax=ax)
nx.draw_networkx_nodes(H2,pos,node_size=[40+ac.get(n,1)*30 for n in H2],node_color=[col[n] for n in H2],edgecolors='white',ax=ax)
txt=[ax.text(*pos[n],n.title(),fontsize=8,color=T) for n in H2];adjust_text(txt,ax=ax)
ax.axis('off');plt.tight_layout();plt.savefig('g15/g10_red_coautoria.png',dpi=170);plt.close()
# G11 nubes por tema
fig,axs=plt.subplots(2,2,figsize=(12,7.5))
cmaps={'SANIDAD':['#0f4a96','#257de0'],'SUELO, MICROBIOTA Y CADMIO':['#a3470f','#f47230'],'GENETICA, TAXONOMIA Y CARACTERES':['#006e57','#00b894'],'SISTEMAS Y MANEJO':['#3f2a9c','#6a4ce2']}
for ax,t in zip(axs.flat,cmaps):
    f=collections.Counter(w for r in R if r['DE']==t for w in set(toks(r)))
    cc=cmaps[t]
    wc=WordCloud(width=900,height=520,background_color='white',max_words=60,color_func=lambda *a,**k:np.random.choice(cc),random_state=2,font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf').generate_from_frequencies(f)
    ax.imshow(wc);ax.axis('off');ax.set_title(f"{SHORT[t]} ({sum(1 for r in R if r['DE']==t)} documentos)",loc='left',fontsize=11,color=T)
plt.tight_layout();plt.savefig('g15/g11_nubes_por_tema.png',dpi=160);plt.close()
# G12 pequeños multiplos produccion por tema
fig,axs=plt.subplots(2,5,figsize=(14,5.2),sharex=True)
ys=list(range(2000,2027))
for ax,t in zip(axs.flat,temas):
    c=collections.Counter(yr(r) for r in R if r['DE']==t)
    v=[c.get(y,0) for y in ys];ax.fill_between(ys,v,color=B,alpha=.25);ax.plot(ys,v,color=B,lw=1.8)
    ax.set_title(SHORT[t],fontsize=9.5,loc='left',color=T);clean(ax);ax.set_ylim(0,max(12,max(v)+1))
    ax.tick_params(labelsize=7.5)
plt.tight_layout();plt.savefig('g15/g12_produccion_por_tema.png',dpi=170);plt.close()
# G13 dumbbell antes vs desde 2020
fig,ax=plt.subplots(figsize=(9,5.2))
rows=[]
for t in temas:
    a=sum(1 for r in R if r['DE']==t and yr(r) and yr(r)<2020);b=sum(1 for r in R if r['DE']==t and yr(r) and yr(r)>=2020);rows.append((t,a,b))
rows.sort(key=lambda x:x[2]-x[1])
for i,(t,a,b) in enumerate(rows):
    ax.plot([a,b],[i,i],color='#cccccc',lw=2.5,zorder=1);ax.scatter(a,i,color='#9dc8f7',s=70,zorder=2,edgecolor='white');ax.scatter(b,i,color=B,s=70,zorder=3,edgecolor='white')
    ax.text(max(a,b)+1,i,f'{a} → {b}',va='center',fontsize=8.5,color=G)
ax.set_yticks(range(len(rows)));ax.set_yticklabels([SHORT[t] for t,_,_ in rows],color=G)
ax.scatter([],[],color='#9dc8f7',label='Antes de 2020');ax.scatter([],[],color=B,label='2020–2026');ax.legend(frameon=False,loc='upper center',bbox_to_anchor=(.5,-.12),ncol=2,fontsize=9);ax.set_xlim(0,62)
ax.set_xlabel('Documentos',color=G);clean(ax,'x');plt.tight_layout();plt.savefig('g15/g13_antes_despues_2020.png',dpi=170);plt.close()
# G14 lollipop bigramas
f2=[(r['termino'].lower(),int(r['n'])) for r in csv.DictReader(open('g387/terminos_2.csv')) if not any(w in r['termino'].lower() for w in ('cacao','theobroma','cif','colombia'))][:20][::-1]
fig,ax=plt.subplots(figsize=(9,6.5))
for i,(t,n) in enumerate(f2):
    ax.plot([0,n],[i,i],color='#9dc8f7',lw=2);ax.scatter(n,i,color=B,s=60,zorder=3);ax.text(n+.8,i,str(n),va='center',fontsize=8.5,color=T)
ax.set_yticks(range(len(f2)));ax.set_yticklabels([t for t,_ in f2],color=G);ax.set_xlabel('Apariciones en títulos',color=G);clean(ax,'x')
plt.tight_layout();plt.savefig('g15/g14_bigramas_top20.png',dpi=170);plt.close()
# G15 sunburst tema-region
lab=['387 documentos'];par=[''];val=[len(R)];ids=['root'];colors=['white']
TC=dict(zip(temas,['#257de0','#f47230','#00b894','#6a4ce2','#f2a600','#ee7fac','#008a17','#ec4647','#1757ac','#a3470f']))
for t in temas:
    n=sum(1 for r in R if r['DE']==t);ids.append(t);lab.append(SHORT[t]);par.append('root');val.append(n);colors.append(TC[t])
    for g in regs:
        m=sum(1 for r in R if r['DE']==t and r['ID']==g)
        if m: ids.append(t+'|'+g);lab.append(RS[g]);par.append(t);val.append(m);colors.append(TC[t])
fig=go.Figure(go.Sunburst(ids=ids,labels=lab,parents=par,values=val,branchvalues='total',marker=dict(colors=colors,line=dict(color='white',width=1.5)),insidetextorientation='radial',textfont=dict(size=11)))
fig.update_layout(width=900,height=900,margin=dict(l=5,r=5,t=5,b=5),font=dict(family='DejaVu Sans'))
fig.write_image('g15/g15_sunburst_tema_region.png',scale=2)
# G16 lotka
ap=collections.Counter(ac.values());xs=sorted(ap)
fig,ax=plt.subplots(figsize=(8,4.8));tot=sum(ap.values())
ax.bar(xs,[ap[x]/tot*100 for x in xs],color=B,width=.6)
xx=np.linspace(1,max(xs),50);ax.plot(xx,(ap[1]/tot*100)/xx**2.39,color=O,lw=2,label='Ley de Lotka (β = 2,39)')
for x in xs: ax.text(x,ap[x]/tot*100+1,str(ap[x]),ha='center',fontsize=8,color=T)
ax.set_xlabel('Documentos por autor',color=G);ax.set_ylabel('% de autores',color=G);ax.legend(frameon=False);clean(ax)
plt.tight_layout();plt.savefig('g15/g16_lotka.png',dpi=170);plt.close()
print('ok')

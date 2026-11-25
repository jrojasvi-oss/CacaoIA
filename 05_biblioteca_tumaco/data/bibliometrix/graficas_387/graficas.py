import csv,collections,re,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np, squarify
from wordcloud import WordCloud
import plotly.graph_objects as go
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
T='#191919';G='#666666'
R=list(csv.DictReader(open('M387.csv')))
def tc(s): return s.capitalize()
# 1 nube
f1={r['termino'].lower():int(r['n']) for r in csv.DictReader(open('g387/terminos_1.csv'))}
BAD={'spp','cif','par','san','pod','rot','sas','luis','frente','contra','based','new','crop','crops','beans','pods','potencial','production','learning'}
f1={k:v for k,v in f1.items() if len(k)>2 and k not in BAD}
def col(*a,**k):
    import random;return random.choice(['#0f4a96','#1757ac','#2370cd','#257de0','#519ced'])
wc=WordCloud(width=1800,height=1000,background_color='white',max_words=120,color_func=col,prefer_horizontal=.9,random_state=7,font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf').generate_from_frequencies(f1)
wc.to_file('g387/nube.png')
# 2 treemap bigramas
f2=[(r['termino'].lower(),int(r['n'])) for r in csv.DictReader(open('g387/terminos_2.csv')) if not any(w in r['termino'].lower() for w in ('cacao','theobroma','cif','colombia'))][:25]
fig,ax=plt.subplots(figsize=(11,6.2))
cols=plt.cm.Blues(np.linspace(.85,.35,len(f2)))
squarify.plot(sizes=[n for _,n in f2],label=[f'{t}\n{n}' for t,n in f2],color=cols,pad=False,ax=ax,text_kwargs={'fontsize':7.8,'color':'white'},ec='white',linewidth=2)
for t in ax.texts[13:]: t.set_color(T)
ax.axis('off');plt.tight_layout();plt.savefig('g387/treemap.png',dpi=180)
# 3 heatmap tema x periodo
per=[('<2000',0,1999),('2000–09',2000,2009),('2010–14',2010,2014),('2015–19',2015,2019),('2020–22',2020,2022),('2023–26',2023,2026)]
temas=[t for t,_ in collections.Counter(r['DE'] for r in R).most_common()]
H=np.zeros((len(temas),len(per)),int)
for r in R:
    try:y=int(float(r['PY']))
    except:continue
    for j,(_,a,b) in enumerate(per):
        if a<=y<=b: H[temas.index(r['DE']),j]+=1
def heat(H,rows,cols_,fn,xl):
    fig,ax=plt.subplots(figsize=(1.25*len(cols_)+3.2,0.42*len(rows)+1.2))
    ax.imshow(H,cmap='Blues',aspect='auto',vmin=0)
    m=H.max()
    for i in range(H.shape[0]):
        for j in range(H.shape[1]):
            v=H[i,j];ax.text(j,i,str(v) if v else '·',ha='center',va='center',fontsize=9,color='white' if v>m*.55 else T)
    ax.set_xticks(range(len(cols_)));ax.set_xticklabels(cols_,fontsize=8.5,color=G);ax.set_yticks(range(len(rows)));ax.set_yticklabels([tc(x) for x in rows],fontsize=9,color=G)
    ax.set_xticks(np.arange(-.5,len(cols_)),minor=True);ax.set_yticks(np.arange(-.5,len(rows)),minor=True);ax.grid(which='minor',color='white',lw=2);ax.tick_params(which='both',length=0)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_xlabel(xl,color=G);plt.tight_layout();plt.savefig(fn,dpi=180)
heat(H,temas,[p[0] for p in per],'g387/calor_tema_periodo.png','Periodo de publicación')
regs=[t for t,_ in collections.Counter(r['ID'] for r in R).most_common()]
short={'TUMACO Y PACIFICO NARINENSE':'Tumaco y Pacífico','OTRAS REGIONES DE COLOMBIA':'Otras regiones','COLOMBIA (NACIONAL)':'Nacional','VALLE DEL CAUCA':'Valle','REGIONAL (FUERA DE COLOMBIA INCLUIDO)':'Regional','CAUCA Y SUROCCIDENTE':'Cauca','NARINO ANDINO Y DEPARTAMENTAL':'Nariño andino'}
H2=np.zeros((len(temas),len(regs)),int)
for r in R: H2[temas.index(r['DE']),regs.index(r['ID'])]+=1
heat(H2,temas,[short.get(x,x) for x in regs],'g387/calor_tema_region.png','Región de estudio')
# 4 trend topics
tt=[r for r in csv.DictReader(open('g387/trend_topics.csv')) if int(r['freq'])>=5 and len(r['item'])>2 and r['item'].lower() not in BAD|{'desarrollo','san','arboles','incidencia','productores','sistema','sistemas','control','consejo','comunitario','cultivo','ecuador','manejo','produccion','frosty','valle','cacaoteros'}]
by=collections.defaultdict(list)
for r in tt: by[int(float(r['year_med']))].append(r)
sel=[]
for y in sorted(by):
    if y<2005: continue
    sel+=sorted(by[y],key=lambda r:-int(r['freq']))[:3]
fig,ax=plt.subplots(figsize=(9,0.33*len(sel)+1.2))
for i,r in enumerate(sel):
    ax.plot([float(r['year_q1']),float(r['year_q3'])],[i,i],color='#9dc8f7',lw=2.5,solid_capstyle='round',zorder=1)
    ax.scatter(float(r['year_med']),i,s=12+int(r['freq'])*4,color='#257de0',zorder=2,edgecolor='white',lw=1)
ax.set_yticks(range(len(sel)));ax.set_yticklabels([f"{tc(r['item'])} ({r['freq']})" for r in sel],fontsize=8.5,color=G)
ax.invert_yaxis();ax.grid(axis='x',color='#eeeeee');ax.set_axisbelow(True)
for s in ['top','right','left']: ax.spines[s].set_visible(False)
ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%d'));ax.set_xlabel('Año (punto = mediana; barra = cuartiles 1 a 3; tamaño = frecuencia)',color=G,fontsize=9);plt.tight_layout();plt.savefig('g387/temas_tendencia.png',dpi=180)
# 5 evolucion tematica: mapa tematico por periodo
import matplotlib.ticker
fig,axs=plt.subplots(1,3,figsize=(15,5.4))
GEN={'theobroma cacao','cacao theobroma','cacao colombia','cultivo cacao'}
for ax,(fn,tl) in zip(axs,[('1950_2009','1957–2009'),('2010_2019','2010–2019'),('2020_2026','2020–2026')]):
    C=[c for c in csv.DictReader(open(f'g387/clusters_{fn}.csv')) if c['name'] not in GEN]
    x=np.array([float(c['centrality']) for c in C]);y=np.array([float(c['density']) for c in C]);f=np.array([float(c['freq']) for c in C])
    mx,my=np.median(x),np.median(y)
    ax.axvline(mx,color='#bbbbbb',ls='--',lw=1);ax.axhline(my,color='#bbbbbb',ls='--',lw=1)
    ax.scatter(x,y,s=30+f*6,color='#257de0',alpha=.55,edgecolor='white',lw=1.5)
    order=np.argsort(-f)
    for k,i in enumerate(order[:9]):
        ax.annotate(C[i]['name'],(x[i],y[i]),xytext=(5,5),textcoords='offset points',fontsize=8,color=T)
    ax.set_title(tl,loc='left',fontsize=11,color=T)
    ax.text(.99,.99,'Motores',transform=ax.transAxes,ha='right',va='top',fontsize=8,color=G);ax.text(.01,.99,'Nicho',transform=ax.transAxes,va='top',fontsize=8,color=G)
    ax.text(.01,.01,'Emergentes o en declive',transform=ax.transAxes,fontsize=8,color=G);ax.text(.99,.01,'Básicos',transform=ax.transAxes,ha='right',fontsize=8,color=G)
    ax.set_xlabel('Centralidad',color=G);ax.set_ylabel('Densidad',color=G)
    for sp in ['top','right']: ax.spines[sp].set_visible(False)
    ax.tick_params(colors=G,labelsize=8)
plt.tight_layout();plt.savefig('g387/evolucion_tematica.png',dpi=170)
# 5b MCA
D=list(csv.DictReader(open('g387/mca_terminos.csv')))
cl={c:i for i,c in enumerate(sorted({d['color'] for d in D}))}
CP=['#257de0','#f47230','#00b894','#6a4ce2','#f2a600','#ee7fac']
fig,ax=plt.subplots(figsize=(10,7))
ax.axvline(0,color='#dddddd',lw=1);ax.axhline(0,color='#dddddd',lw=1)
TX=[]
for d in D:
    c=CP[cl[d['color']]%len(CP)];x,y=float(d['Dim1']),float(d['Dim2'])
    ax.scatter(x,y,s=28,color=c,edgecolor='white',lw=1);TX.append(ax.text(x,y,d['label'],fontsize=9,color=T))
from adjustText import adjust_text
adjust_text(TX,ax=ax,arrowprops=dict(arrowstyle='-',color='#bbbbbb',lw=.5))
ax.set_xlabel('Dimensión 1',color=G);ax.set_ylabel('Dimensión 2',color=G)
for sp in ['top','right']: ax.spines[sp].set_visible(False)
ax.tick_params(colors=G);plt.tight_layout();plt.savefig('g387/estructura_conceptual.png',dpi=170)
# 6 tres campos autor-tema-region
ac=collections.Counter(a for r in R for a in r['AU'].split(';') if a and a not in ('AGROSAVIA','CORPOICA','ANONIMO'))
top=[a for a,_ in ac.most_common(15)]
lab=[a.title() for a in top]+[tc(t) for t in temas]+[short.get(x,x) for x in regs]
L1=collections.Counter();L2=collections.Counter()
for r in R:
    aus=[a for a in r['AU'].split(';') if a in top]
    for a in aus: L1[(top.index(a),len(top)+temas.index(r['DE']))]+=1
    if aus: L2[(len(top)+temas.index(r['DE']),len(top)+len(temas)+regs.index(r['ID']))]+=1
links=list(L1.items())+list(L2.items())
ncol=['#1757ac']*len(top)+['#257de0']*len(temas)+['#84b9f3']*len(regs)
fig=go.Figure(go.Sankey(arrangement='snap',node=dict(label=lab,color=ncol,pad=10,thickness=14,line=dict(width=0)),link=dict(source=[s for (s,t),v in links],target=[t for (s,t),v in links],value=[v for _,v in links],color='rgba(37,125,224,0.18)')))
for x,t in [(0.0,'Autores (15 más productivos)'),(0.5,'Tema'),(1.0,'Región')]:
    fig.add_annotation(x=x,y=1.07,xref='paper',yref='paper',text=f'<b>{t}</b>',showarrow=False,font=dict(size=13,color=T))
fig.update_layout(font=dict(size=11,color=T,family='DejaVu Sans'),width=1100,height=700,margin=dict(l=10,r=10,t=50,b=10),paper_bgcolor='white')
fig.write_image('g387/tres_campos.png',scale=2)
print('ok',len(sel),top[:5])

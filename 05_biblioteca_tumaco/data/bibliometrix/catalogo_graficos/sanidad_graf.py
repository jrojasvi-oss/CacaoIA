import json,collections,re,unicodedata,openpyxl,matplotlib
import matplotlib.ticker
matplotlib.use('Agg')
import matplotlib.pyplot as plt,numpy as np,networkx as nx,itertools
import plotly.graph_objects as go
from adjustText import adjust_text
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
T='#191919';G='#666666';B='#257de0';O='#f47230';CM='YlGnBu'
D=json.load(open('g25/sanidad_docs.json'))
def na(s): return unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower()
PR=[p for p,_ in collections.Counter(p for d in D for p in d['prob']).most_common()]
MN=[m for m,_ in collections.Counter(m for d in D for m in d['man']).most_common()]
REG=[r for r,_ in collections.Counter(d['reg'] for d in D).most_common()]
per=[('<2000',0,1999),('2000–09',2000,2009),('2010–14',2010,2014),('2015–19',2015,2019),('2020–22',2020,2022),('2023–26',2023,2026)]
def pidx(y):
    for j,(_,a,b) in enumerate(per):
        if y is not None and a<=y<=b: return j
IT={'Phytophthora':r'$\it{Phytophthora}$','Ceratocystis':r'$\it{Ceratocystis}$','Rosellinia':r'$\it{Rosellinia}$','Carmenta':r'$\it{Carmenta}$','Monalonion':r'$\it{Monalonion}$','Xyleborus':r'$\it{Xyleborus}$','Antiteuchus':r'$\it{Antiteuchus}$','Trichoderma':r'$\it{Trichoderma}$','Bacillus':r'$\it{Bacillus}$','Clonostachys':r'$\it{Clonostachys}$','Pseudomonas':r'$\it{Pseudomonas}$'}
def DL(x):
    for k,v in IT.items(): x=x.replace(k,v)
    return x
def clean(ax,g='x'):
    for s in ['top','right']: ax.spines[s].set_visible(False)
    ax.grid(axis=g,color='#eeeeee');ax.set_axisbelow(True);ax.tick_params(colors=G)
def heat(H,rows,cols,fn,xl='',w=None,h=None,rot=0):
    fig,ax=plt.subplots(figsize=(w or 1.0*len(cols)+3.8,h or .48*len(rows)+1.5))
    im=ax.imshow(H,cmap=CM,aspect='auto',vmin=0);m=H.max()
    for i in range(H.shape[0]):
        for j in range(H.shape[1]):
            if H[i,j]: ax.text(j,i,str(H[i,j]),ha='center',va='center',fontsize=9,color='white' if H[i,j]>m*.5 else T)
    ax.set_xticks(range(len(cols)));ax.set_xticklabels([DL(c) for c in cols],fontsize=8.5,color=G,rotation=rot,ha='right' if rot else 'center')
    ax.set_yticks(range(len(rows)));ax.set_yticklabels([DL(r) for r in rows],fontsize=9,color=G)
    ax.set_xticks(np.arange(-.5,len(cols)),minor=True);ax.set_yticks(np.arange(-.5,len(rows)),minor=True);ax.grid(which='minor',color='white',lw=1.5);ax.tick_params(which='both',length=0)
    for s in ax.spines.values(): s.set_visible(False)
    cb=plt.colorbar(im,ax=ax,fraction=.03,pad=.02);cb.outline.set_visible(False);cb.ax.tick_params(labelsize=8,colors=G);cb.set_label('Documentos',color=G,fontsize=8.5)
    ax.set_xlabel(xl,color=G);plt.tight_layout();plt.savefig(fn,dpi=170);plt.close()
def bars(items,fn,xl='Documentos',col=B,h=None,italic=()):
    items=items[::-1];fig,ax=plt.subplots(figsize=(9,h or .45*len(items)+1.2))
    ax.barh(range(len(items)),[n for _,n in items],color=col,height=.6)
    mx=max(n for _,n in items)
    for i,(_,n) in enumerate(items): ax.text(n+mx*.012,i,str(n),va='center',fontsize=9,color=T)
    ax.set_yticks(range(len(items)));ax.set_yticklabels([DL(k) for k,_ in items],color=G)
    for lab in ax.get_yticklabels():
        if lab.get_text() in italic: lab.set_style('italic')
    ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True));ax.set_xlabel(xl,color=G);clean(ax);plt.tight_layout();plt.savefig(fn,dpi=170);plt.close()
# 22 problemas
bars(collections.Counter(p for d in D for p in d['prob']).most_common(),'g25/g22_problemas_sanitarios.png')
# 23 manejo
bars(collections.Counter(m for d in D for m in d['man']).most_common(),'g25/g23_modos_manejo.png',col='#00a888')
# 24 problema x manejo
H=np.zeros((len(PR),len(MN)),int)
for d in D:
    for p in d['prob']:
        for m in d['man']: H[PR.index(p),MN.index(m)]+=1
heat(H,PR,MN,'g25/g24_calor_problema_manejo.png',rot=30,w=12,h=5.5)
# 25 problema x periodo
H=np.zeros((len(PR),len(per)),int)
for d in D:
    j=pidx(d['y'])
    if j is None: continue
    for p in d['prob']: H[PR.index(p),j]+=1
heat(H,PR,[p[0] for p in per],'g25/g25_calor_problema_periodo.png',xl='Periodo')
# 26 manejo x periodo
H=np.zeros((len(MN),len(per)),int)
for d in D:
    j=pidx(d['y'])
    if j is None: continue
    for m in d['man']: H[MN.index(m),j]+=1
heat(H,MN,[p[0] for p in per],'g25/g26_calor_manejo_periodo.png',xl='Periodo')
# 27 problema x region
H=np.zeros((len(PR),len(REG)),int)
for d in D:
    for p in d['prob']: H[PR.index(p),REG.index(d['reg'])]+=1
heat(H,PR,REG,'g25/g27_calor_problema_region.png',rot=30)
# 28 agente biologico x problema (Colombia)
AG={'Trichoderma':r'trichoderma','Bacillus':r'bacillus','Clonostachys':r'clonostachys','Pseudomonas':r'pseudomonas','Hongos endófitos':r'endofit|endophyt','Hongos entomopatógenos':r'beauveria|metarhizium|paecilomyces|lecanicillium|entomopat','Otros antagonistas nativos':r'antagon|microorganismos? nativ|bioinsumo'}
AGL=list(AG);PR2=[p for p in PR if p not in ('Enfermedades en general',)]
H=np.zeros((len(AGL),len(PR2)),int)
for d in D:
    for a,p_ in AG.items():
        if re.search(p_,d['txt']):
            for p in d['prob']:
                if p in PR2: H[AGL.index(a),PR2.index(p)]+=1
keep=[i for i in range(len(AGL)) if H[i].sum()>0];H=H[keep];AGL=[AGL[i] for i in keep]
heat(H,AGL,PR2,'g25/g28_calor_agente_problema.png',rot=25,w=11)
# 29 Colombia vs otros: agente x patogeno (busquedas de sanidad de la fase 4)
U=json.load(open('/home/claude/tumaco/fase4/u4_final.json'))
combos=[('Trichoderma','monilia'),('Trichoderma','phyto'),('Bacillus','monilia'),('Bacillus','phyto'),('Otros antagonistas','monilia'),('Otros antagonistas','phyto')]
pat={'Trichoderma':r'trichoderma','Bacillus':r'bacillus','Otros antagonistas':r'pseudomonas|clonostachys|endophyt|endofit|streptomyces|actinomyc','monilia':r'monili|roreri|frosty','phyto':r'phytophthora|black pod|mazorca negra|palmivora'}
cc=collections.Counter()
for x in U:
    t=na(x['titulo']+' '+(x.get('ab') or ''))
    if not re.search(r'cacao|cocoa|theobroma',t): continue
    rz=str(x.get('razon',''))
    zona='Colombia' if (x.get('dec')=='I' and rz.startswith('Colombia')) else ('Otros países' if rz.startswith('E1') else None)
    if not zona: continue
    for a,p in combos:
        if re.search(pat[a],t) and re.search(pat[p],t): cc[(a,p,zona)]+=1
lab=[DL(f"{a}\ncontra {'moniliasis' if p=='monilia' else 'Phytophthora'}") for a,p in combos]
fig,ax=plt.subplots(figsize=(10,5));x=np.arange(len(combos))
c1=[cc[(a,p,'Colombia')] for a,p in combos];c2=[cc[(a,p,'Otros países')] for a,p in combos]
ax.bar(x-.19,c1,.36,color=B,label='Colombia');ax.bar(x+.19,c2,.36,color=O,label='Otros países')
for i in range(len(x)): ax.text(x[i]-.19,c1[i]+.3,str(c1[i]),ha='center',fontsize=9,color=T);ax.text(x[i]+.19,c2[i]+.3,str(c2[i]),ha='center',fontsize=9,color=T)
ax.set_xticks(x);ax.set_xticklabels(lab,fontsize=8.5,color=G);ax.set_ylabel('Registros',color=G);ax.legend(frameon=False);clean(ax,'y')
plt.tight_layout();plt.savefig('g25/g29_colombia_vs_mundo_biocontrol.png',dpi=170);plt.close()
print('cc',dict(cc))
# 30 sankey problema -> manejo -> region
P2=[p for p in PR];M2=[m for m in MN]
lab=P2+M2+REG;L=collections.Counter()
for d in D:
    for p in d['prob']:
        for m in d['man']: L[(P2.index(p),len(P2)+M2.index(m))]+=1
    for m in d['man']: L[(len(P2)+M2.index(m),len(P2)+len(M2)+REG.index(d['reg']))]+=1
ncol=['#0f4a96']*len(P2)+['#00a888']*len(M2)+['#84b9f3']*len(REG)
fig=go.Figure(go.Sankey(node=dict(label=lab,color=ncol,pad=10,thickness=14,line=dict(width=0)),link=dict(source=[s for (s,t) in L],target=[t for (s,t) in L],value=list(L.values()),color='rgba(37,125,224,0.16)')))
for x_,t in [(0,'Problema sanitario'),(.5,'Modo de manejo'),(1,'Región')]: fig.add_annotation(x=x_,y=1.07,xref='paper',yref='paper',text=f'<b>{t}</b>',showarrow=False,font=dict(size=13))
fig.update_layout(width=1150,height=700,margin=dict(l=10,r=10,t=50,b=10),font=dict(size=11,family='DejaVu Sans',color=T))
fig.write_image('g25/g30_sankey_problema_manejo_region.png',scale=2)
# 31 insectos plaga
INS={'Monalonion (chinche)':r'monalonion','Antiteuchus (chinche)':r'antiteuchus','Carmenta (perforador de mazorca)':r'carmenta|perforador','Xyleborus y taladradores':r'xyleborus|taladrador|barrenador','Steirastoma':r'steirastoma','Hormigas':r'hormiga|atta ','Trips':r'thrips|trips\b'}
ic=[(k,sum(1 for d in D if re.search(p,d['txt']))) for k,p in INS.items()]
ic=[x for x in sorted(ic,key=lambda x:-x[1]) if x[1]>0]
bars(ic,'g25/g31_insectos_plaga.png',col=O,h=3.6)
print(ic)
# 32 red de palabras en sanidad
SW=set("de del la las el los en y con para por una un al sus su a o e the of and in on for with to from by an as its at is are using use que se como sobre entre sin desde mediante bajo cacao theobroma cocoa colombia colombian evaluacion evaluation analisis analysis efecto effect uso spp cif par san pod rot sas new frente contra".split())
docs=[set(w for w in re.sub(r'[^a-z ]',' ',na(d['ti'])).split() if w not in SW and len(w)>3) for d in D]
tf=collections.Counter(w for s in docs for w in s);top=[w for w,_ in tf.most_common(35)]
Gx=nx.Graph()
for s in docs:
    for a,b in itertools.combinations(sorted(w for w in top if w in s),2): Gx.add_edge(a,b,weight=Gx[a][b]['weight']+1 if Gx.has_edge(a,b) else 1)
Gx.remove_nodes_from(list(nx.isolates(Gx)))
comm=nx.community.louvain_communities(Gx,weight='weight',seed=3);PAL=[B,O,'#00b894','#6a4ce2','#f2a600','#ee7fac']
col={n:PAL[i%6] for i,c in enumerate(comm) for n in c};pos=nx.spring_layout(Gx,weight='weight',seed=2,k=.9)
fig,ax=plt.subplots(figsize=(11,8))
nx.draw_networkx_edges(Gx,pos,edge_color='#d5d5d5',width=[.4+d['weight']*.35 for *_,d in Gx.edges(data=True)],ax=ax)
nx.draw_networkx_nodes(Gx,pos,node_size=[tf[n]*22 for n in Gx],node_color=[col[n] for n in Gx],edgecolors='white',ax=ax)
tx=[ax.text(*pos[n],n,fontsize=9,color=T) for n in Gx];adjust_text(tx,ax=ax);ax.axis('off');plt.tight_layout();plt.savefig('g25/g32_red_palabras_sanidad.png',dpi=170);plt.close()
print('ok')

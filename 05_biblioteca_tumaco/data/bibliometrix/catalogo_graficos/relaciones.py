import json,collections,itertools,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt,numpy as np,networkx as nx
from matplotlib.path import Path
from matplotlib.patches import PathPatch,Wedge,Circle
import plotly.graph_objects as go
from adjustText import adjust_text
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
T='#191919';G='#666666';CM='YlGnBu'
D=json.load(open('g25/sanidad_docs2.json'))
SPc=collections.Counter(s for d in D for s in d['sp'])
SP=[s for s,n in SPc.most_common() if n>=2]
DEPc=collections.Counter(x for d in D for x in d['dep']);DEP=[x for x,_ in DEPc.most_common()]
ENF=[e for e,_ in collections.Counter(e for d in D for e in d['enf']).most_common()]
PAL=['#257de0','#f47230','#00b894','#6a4ce2','#f2a600','#ee7fac','#008a17','#ec4647','#1757ac','#a3470f','#5a5a5a']
SPC={s:PAL[i%len(PAL)] for i,s in enumerate(SP)}
def it(s):
    w=s.split(' ')
    if s in('Phytophthora spp.',): return r'$\it{Phytophthora}$ spp.'
    if w[0] in ('Moniliophthora','Phytophthora','Carmenta') and len(w)==2: return r'$\it{'+w[0]+r'}$ $\it{'+w[1]+'}$'
    return r'$\it{'+s+'}$'
def heat(H,rows,cols,fn,w,h,rot=35,rl=None):
    fig,ax=plt.subplots(figsize=(w,h));im=ax.imshow(H,cmap=CM,aspect='auto',vmin=0);m=H.max()
    for i in range(H.shape[0]):
        for j in range(H.shape[1]):
            if H[i,j]: ax.text(j,i,str(H[i,j]),ha='center',va='center',fontsize=9,color='white' if H[i,j]>m*.5 else T)
    ax.set_xticks(range(len(cols)));ax.set_xticklabels(cols,rotation=rot,ha='right',fontsize=8.5,color=G)
    ax.set_yticks(range(len(rows)));ax.set_yticklabels(rl or rows,fontsize=9,color=G)
    ax.set_xticks(np.arange(-.5,len(cols)),minor=True);ax.set_yticks(np.arange(-.5,len(rows)),minor=True);ax.grid(which='minor',color='white',lw=1.5);ax.tick_params(which='both',length=0)
    for s in ax.spines.values(): s.set_visible(False)
    cb=plt.colorbar(im,ax=ax,fraction=.03,pad=.02);cb.outline.set_visible(False);cb.ax.tick_params(labelsize=8,colors=G);cb.set_label('Documentos',color=G,fontsize=8.5)
    plt.tight_layout();plt.savefig(fn,dpi=170);plt.close()
# 33 calor especie x departamento
H=np.zeros((len(SP),len(DEP)),int)
for d in D:
    for s in d['sp']:
        if s in SP:
            for x in d['dep']: H[SP.index(s),DEP.index(x)]+=1
keep=[i for i in range(len(SP)) if H[i].sum()];Hd=H[keep];SPd=[SP[i] for i in keep]
heat(Hd,SPd,DEP,'g25/g33_calor_especie_departamento.png',13,.55*len(SPd)+2,rl=[it(s) for s in SPd])
# 34 calor especie x enfoque
H2=np.zeros((len(SP),len(ENF)),int)
for d in D:
    for s in d['sp']:
        if s in SP:
            for e in d['enf']: H2[SP.index(s),ENF.index(e)]+=1
heat(H2,SP,ENF,'g25/g34_calor_especie_enfoque.png',11,.5*len(SP)+2.2,rot=25,rl=[it(s) for s in SP])
# 35 diagrama de cuerdas especie <-> departamento
Sx=SPd;Dx=[x for x in DEP if Hd[:,DEP.index(x)].sum()>0]
M=Hd[:,[DEP.index(x) for x in Dx]]
tot=M.sum();gap=np.deg2rad(2.2)
nodes=[(s,M[i].sum(),'sp') for i,s in enumerate(Sx)]+[(x,M[:,j].sum(),'dep') for j,x in enumerate(Dx)]
avail=2*np.pi-gap*len(nodes);scale=avail/(2*tot)
ang={};a=np.pi/2
for n,v,k in nodes:
    ang[n]=(a,a-v*scale);a-=v*scale+gap
fig,ax=plt.subplots(figsize=(10,10));ax.set_xlim(-1.45,1.45);ax.set_ylim(-1.45,1.45);ax.axis('off');ax.set_aspect('equal')
DC='#9aa5b1'
for n,v,k in nodes:
    a0,a1=ang[n];c=SPC.get(n,DC)
    ax.add_patch(Wedge((0,0),1.06,np.rad2deg(a1),np.rad2deg(a0),width=.07,color=c))
    am=(a0+a1)/2;x,y=1.12*np.cos(am),1.12*np.sin(am);rot=np.rad2deg(am)
    if np.cos(am)<0: rot+=180
    ax.text(x,y,(it(n) if k=='sp' else n)+f' ({int(v)})',rotation=rot,rotation_mode='anchor',ha='left' if np.cos(am)>=0 else 'right',va='center',fontsize=9,color=T)
pos_sp={n:ang[n][0] for n,_,k in nodes if k=='sp'};pos_dep={n:ang[n][0] for n,_,k in nodes if k=='dep'}
for i,s in enumerate(Sx):
    for j,x in enumerate(Dx):
        v=M[i,j]
        if not v: continue
        w=v*scale;s0=pos_sp[s];s1=s0-w;pos_sp[s]=s1;d0=pos_dep[x];d1=d0-w;pos_dep[x]=d1
        P=lambda t:(0.99*np.cos(t),0.99*np.sin(t))
        verts=[P(s0),(0,0),P(d1),P(d1),P(d0),P(d0),(0,0),P(s1),P(s1),P(s0)]
        # arcs approximated by straight segments between close points
        codes=[Path.MOVETO,Path.CURVE3,Path.CURVE3,Path.LINETO,Path.LINETO,Path.CURVE3,Path.CURVE3,Path.LINETO,Path.LINETO,Path.CLOSEPOLY]
        verts=[P(s0),(0,0),P(d1),P(d0),(0,0),P(s1),P(s0)];codes=[Path.MOVETO,Path.CURVE3,Path.CURVE3,Path.LINETO,Path.CURVE3,Path.CURVE3,Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts,codes),fc=SPC[s],alpha=.55,ec='white',lw=.4))
plt.tight_layout();plt.savefig('g25/g35_cuerdas_especie_departamento.png',dpi=170);plt.close()
# 36 red tipo molecular
Gx=nx.Graph()
for d in D:
    items=[('sp',s) for s in d['sp'] if s in SP]+[('dep',x) for x in d['dep']]+[('enf',e) for e in d['enf']]
    for a_,b_ in itertools.combinations(items,2):
        if a_[0]==b_[0]: continue
        Gx.add_edge(a_,b_,weight=Gx[a_][b_]['weight']+1 if Gx.has_edge(a_,b_) else 1)
Gx.remove_edges_from([(u,v) for u,v,dd in Gx.edges(data=True) if dd['weight']<2])
Gx.remove_nodes_from(list(nx.isolates(Gx)))
cnt={('sp',s):SPc[s] for s in SP};cnt.update({('dep',x):DEPc[x] for x in DEP});cnt.update({('enf',e):sum(1 for d in D if e in d['enf']) for e in ENF})
pos=nx.kamada_kawai_layout(Gx)
fig,ax=plt.subplots(figsize=(12,10));ax.set_facecolor('white')
for u,v,dd in Gx.edges(data=True):
    (x1,y1),(x2,y2)=pos[u],pos[v];ax.plot([x1,x2],[y1,y2],color='#b9c2cc',lw=.6+dd['weight']*.35,zorder=1,solid_capstyle='round')
txt=[]
for n in Gx:
    k,name=n;x,y=pos[n];r=.025+np.sqrt(cnt[n])*.008
    c=SPC.get(name) if k=='sp' else ('#9aa5b1' if k=='dep' else '#3d3d3d')
    ax.add_patch(Circle((x,y),r,color=c,zorder=2));ax.add_patch(Circle((x-r*.35,y+r*.35),r*.35,color='white',alpha=.45,zorder=3))
    txt.append(ax.text(x+r,y+r,(it(name) if k=='sp' else name),fontsize=8.5 if k!='enf' else 8,color=T,weight='bold' if k=='enf' else 'normal',zorder=4))
adjust_text(txt,ax=ax)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([],[],marker='o',ls='',color='#257de0',ms=11,label='Patógeno o plaga (color por especie)'),Line2D([],[],marker='o',ls='',color='#9aa5b1',ms=9,label='Departamento'),Line2D([],[],marker='o',ls='',color='#3d3d3d',ms=9,label='Enfoque de investigación')],frameon=False,loc='lower left',fontsize=9)
ax.set_aspect('equal');ax.axis('off');plt.tight_layout();plt.savefig('g25/g36_red_molecular_especie_depto_enfoque.png',dpi=170);plt.close()
# 37 sunburst especie -> departamento
ids=['root'];lab=['Sanidad'];par=[''];val=[0];col=['white']
for i,s in enumerate(SPd):
    v=int(Hd[i].sum());ids.append(s);lab.append('<i>'+s.replace(' spp.','</i> spp.<i>')+'</i>');par.append('root');val.append(v);col.append(SPC[s])
    for j,x in enumerate(DEP):
        if Hd[i,j]: ids.append(s+'|'+x);lab.append(x);par.append(s);val.append(int(Hd[i,j]));col.append(SPC[s])
val[0]=sum(val[1:1+len(SPd)]) if False else sum(int(Hd[i].sum()) for i in range(len(SPd)))
fig=go.Figure(go.Sunburst(ids=ids,labels=lab,parents=par,values=val,branchvalues='total',marker=dict(colors=col,line=dict(color='white',width=1.5)),insidetextorientation='radial',textfont=dict(size=11)))
fig.update_layout(width=900,height=900,margin=dict(l=5,r=5,t=5,b=5),font=dict(family='DejaVu Sans'))
fig.write_image('g25/g37_anillos_especie_departamento.png',scale=2)
# 38 barras circulares departamento apiladas por especie
Dn=[x for x in DEP if Hd[:,DEP.index(x)].sum()>0];n=len(Dn)
fig=plt.figure(figsize=(12,9));ax=fig.add_axes([0,0,.72,1],projection='polar')
th=np.linspace(0,2*np.pi,n,endpoint=False);w=2*np.pi/n*.8;base=6;bottom=np.zeros(n)
for i,s_ in enumerate(SPd):
    v=np.array([Hd[i,DEP.index(x)] for x in Dn]);ax.bar(th,v,width=w,bottom=bottom+base,color=SPC[s_],edgecolor='white',lw=1);bottom+=v
for t,x,b in zip(th,Dn,bottom):
    rot=np.rad2deg(t);al='left'
    if 90<rot<270: rot+=180;al='right'
    ax.text(t,b+base+.6,f'{x} ({int(b)})',rotation=rot,rotation_mode='anchor',ha=al,va='center',fontsize=9.5,color=T)
ax.set_ylim(0,bottom.max()+base+9);ax.axis('off')
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color=SPC[s_],label=it(s_)) for s_ in SPd],loc='center left',bbox_to_anchor=(.72,.5),fontsize=9.5,frameon=False,title='Patógeno o plaga',title_fontsize=10)
plt.savefig('g25/g38_barras_circulares_departamento.png',dpi=170);plt.close()
print('ok')

import openpyxl,collections,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.edgecolor':'#bbbbbb','axes.labelcolor':'#666666','xtick.color':'#666666','ytick.color':'#666666'})
B='#257de0';O='#f47230';T='#191919';G='#666666'
wb=openpyxl.load_workbook('/home/claude/tumaco/v3/Revision_cacao_ruta_suroccidental_datos.xlsx',data_only=True)
rows=[r for r in list(wb['Todos (387 + contexto)'].iter_rows(values_only=True))[1:] if r[14] and 'ontexto' not in str(r[14]) and 'ontexto' not in str(r[13])]
print(len(rows),collections.Counter(r[14] for r in rows))
def clean(ax):
    for s in ['top','right']: ax.spines[s].set_visible(False)
    ax.grid(axis='x' if ax.get_ylabel()=='' else 'y',color='#eeeeee',lw=.8); ax.set_axisbelow(True)
# 1 year
yrs=collections.Counter()
for r in rows:
    try: y=int(str(r[1])[:4])
    except: continue
    yrs[y]+=1
bins=['<1990','1990–99','2000–09','2010–14','2015–19','2020','2021','2022','2023','2024','2025','2026']
def b(y):
    if y<1990:return bins[0]
    if y<2000:return bins[1]
    if y<2010:return bins[2]
    if y<2015:return bins[3]
    if y<2020:return bins[4]
    return str(y)
c=collections.Counter();[c.update({b(y):n}) for y,n in yrs.items()]
print(c, sum(c.values()))
fig,ax=plt.subplots(figsize=(8,3.6));v=[c[k] for k in bins]
ax.bar(bins,v,color=B,width=.7)
for i,x in enumerate(v): ax.text(i,x+.8,str(x),ha='center',fontsize=9,color=T)
ax.set_ylabel('Documentos');clean(ax);plt.xticks(rotation=0,fontsize=8.5);plt.tight_layout();plt.savefig('f_anios.png',dpi=200)
# 2 region
reg=collections.Counter(r[13] for r in rows);print(reg)
it=sorted(reg.items(),key=lambda x:x[1])
fig,ax=plt.subplots(figsize=(8,3.4));ax.barh([k for k,_ in it],[n for _,n in it],color=B,height=.6)
for i,(_,n) in enumerate(it): ax.text(n+1,i,str(n),va='center',fontsize=9,color=T)
ax.set_xlabel('Documentos');ax.set_ylabel('');clean(ax);plt.tight_layout();plt.savefig('f_region.png',dpi=200)
# 3 IA
ia=list(wb['IA en cacao (mundial)'].iter_rows(values_only=True))[1:]
org=collections.Counter(r[5] for r in ia);tar=collections.Counter(r[6] for r in ia);print(org,tar)
fig,axs=plt.subplots(1,2,figsize=(9,3.6))
for ax,cc,tt in [(axs[0],org,'Órgano o escala de la imagen'),(axs[1],tar,'Tarea')]:
    it=sorted(cc.items(),key=lambda x:x[1]);ax.barh([k for k,_ in it],[n for _,n in it],color=B,height=.6)
    for i,(k,n) in enumerate(it): ax.text(n+1,i,str(n),va='center',fontsize=9,color=T)
    ax.set_title(tt,fontsize=10,color=T,loc='left');ax.set_ylabel('');clean(ax);ax.set_xlim(0,max(cc.values())*1.18)
plt.tight_layout();plt.savefig('f_ia.png',dpi=200)
# 4 sanidad
fig,axs=plt.subplots(1,2,figsize=(9,3.4))
d=[('Escoba de bruja',13),('$\\it{Phytophthora}$ (mazorca negra)',16),('Moniliasis',69)]
ax=axs[0];ax.barh([k for k,_ in d],[n for _,n in d],color=B,height=.55)
for i,(k,n) in enumerate(d): ax.text(n+1,i,str(n),va='center',fontsize=9,color=T)
ax.set_title('Enfermedad estudiada (Colombia, 83 documentos)',fontsize=9.5,color=T,loc='left');clean(ax);ax.set_xlim(0,80)
ax=axs[1];cats=['$\\it{Trichoderma}$\n(Colombia)','$\\it{Bacillus}$\n(Colombia)','$\\it{Bacillus}$ contra\n$\\it{Phytophthora}$']
col=[17,10,0];oth=[0,0,17]
x=range(3);ax.bar([i-.18 for i in x],col,width=.34,color=B,label='Colombia')
ax.bar([i+.18 for i in x[2:]],oth[2:],width=.34,color=O,label='Otros países')
for i,n in enumerate(col): ax.text(i-.18,n+.4,str(n),ha='center',fontsize=9,color=T)
ax.text(2.18,17.4,'17',ha='center',fontsize=9,color=T)
ax.set_xticks(list(x));ax.set_xticklabels(cats,fontsize=8.5);ax.set_title('Control biológico',fontsize=9.5,color=T,loc='left')
ax.legend(frameon=False,fontsize=8.5);clean(ax);ax.set_ylabel('Documentos')
plt.tight_layout();plt.savefig('f_sanidad.png',dpi=200)
# 5 PRISMA
fig,ax=plt.subplots(figsize=(9,9.6));ax.set_xlim(0,100);ax.set_ylim(0,108);ax.axis('off')
def box(x,y,w,h,t,fc='#eef5fd',ec='#257de0',fs=8.6):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.3,rounding_size=1.2',fc=fc,ec=ec,lw=1));ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=fs,color=T,wrap=True)
def arr(x1,y1,x2,y2): ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='->',color=G,lw=1))
for y,l in [(88,'Identificación'),(56,'Tamizaje'),(14,'Incluidos')]:
    ax.add_patch(FancyBboxPatch((0,y-(8 if l!='Tamizaje' else 18)),5,(16 if l!='Tamizaje' else 36),boxstyle='round,pad=0.2',fc='#257de0',ec='none'));ax.text(2.5,y,l,rotation=90,ha='center',va='center',color='white',fontsize=9,weight='bold')
box(9,82,44,15,'Registros identificados en bases de datos\n(n = 3.277)\nFase 1 Tumaco: 394 · Fase 2 Valle y ruta: 378\nFase 3 OpenAlex: 914 · Fase 4 IA y sanidad: 1.591')
box(60,84,38,13,'Registros retirados antes del tamizaje\nDuplicados o ya incluidos en una\nfase anterior (n = 840)',fc='#f6f6f6',ec='#999999')
arr(53,90.5,60,90.5);arr(31,82,31,73)
box(9,62,44,11,'Registros tamizados por título y resumen\n(n = 2.437)')
box(60,44,38,36,'Registros excluidos (n = 1.818)\n\nFases 1 y 2 (n = 315): otro país, fuera\nde alcance, boletines, divulgativos\n\nFases 3 y 4 (n = 1.503):\nE1/E2 otro país o fuera de alcance: 818\nE3 no trata de cacao: 672\nE6 sin método de imagen o IA: 10\nE4 divulgativo sin datos: 3',fc='#f6f6f6',ec='#999999',fs=8.2)
arr(53,67.5,60,67.5);arr(31,62,31,53)
box(9,41,44,12,'Registros que cumplen los criterios\n(n = 600)\nAparte, 19 en «Quizá» (texto completo pendiente)',fs=8.3)
box(37,26,21,13,'Otros métodos\n(n = 33)\nLit. gris fase 1: 12\nComplementarios: 5\nWeb dirigida: 16',fc='#f6f6f6',ec='#999999',fs=8.3)
arr(20,41,20,24);arr(50,41,78,24);arr(40,26,34,22)
box(9,6,25,17,'Biblioteca colombiana\n(n = 387)\nF1: 109 · F2: 106\nF3: 55 · F4: 117',fc='#dcebfc')
box(60,6,38,17,'Corpus aparte: IA en cacao\nfuera de Colombia\n(n = 246)\nantecedente de método, no se suma\na la biblioteca',fc='#fff0e8',ec='#f47230')
plt.savefig('f_prisma.png',dpi=200,bbox_inches='tight');print('ok')

import openpyxl,json,re,collections,unicodedata
def na(s): return unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower()
def norm(s): return re.sub(r'[^a-z0-9]+',' ',na(s)).strip()
wb=openpyxl.load_workbook('/home/claude/tumaco/v3/Revision_cacao_ruta_suroccidental_datos.xlsx',read_only=True,data_only=True)
T=[r for r in list(wb['Todos (387 + contexto)'].iter_rows(values_only=True))[1:] if r[14] and 'ontexto' not in str(r[14])]
u4=json.load(open('/home/claude/tumaco/fase4/u4_final.json'))
ab={norm(x['titulo'])[:60]:x.get('ab','') for x in u4}
PROB={'Moniliasis':r'monili|roreri|frosty','Mazorca negra (Phytophthora)':r'phytophthora|mazorca negra|black pod|palmivora','Escoba de bruja':r'escoba de bruja|perniciosa|witches','Mal de machete (Ceratocystis)':r'ceratocystis|mal de machete|llaga macana|wilt','Pudrición de raíz (Rosellinia)':r'rosellinia|pudricion(es)? de raiz|root rot','Insectos plaga':r'monalonion|carmenta|xyleborus|steirastoma|antiteuchus|thrips|trips\b|hormiga|atta |chinche|taladrador|barrenador|perforador|insectos? plaga|pest insect|insect pest|insectos (que|del)|\bmirid'}
MAN={'Biológico':r'trichoderma|bacillus|clonostachys|pseudomonas|biocontrol|control biologico|biological control|antagon|endofit|endophyt|microorganismos? nativ|bioinsumo|entomopat|beauveria|metarhizium|hongos? (que atacan|entomo)','Extractos botánicos':r'extracto|aceite esencial|essential oil|botanic|vegetal(es)? para el control|plant extract','Químico':r'fungicid|quimic|chemical|cobre|copper|insecticid|sistemica|protectante|compuestos','Cultural':r'cultural|poda|pruning|remocion|removal|sanitari|cosecha sanitaria|labores|frecuencia de cosecha','Genético (resistencia)':r'resisten|toleran|clones? (de cacao )?(frente|contra|against)|genotip|gwas|candidate genes|selection of clones|clones','Integrado (MIP)':r'integrad|integrated|\bmip\b|\bipm\b|manejo integral','Diagnóstico y epidemiología':r'incidencia|incidence|prevalen|distribu|diversidad|diversity|estructura poblacional|population structure|caracterizacion (morfologica y )?patogen|epidemiolog|severidad|severity|diagnost|biogeograf|identificaci|aislamientos|isolates|genom','Detección con IA o imágenes':r'deep learning|aprendizaje|vision|imagen|image|neural|machine learning|convolution|yolo'}
REG={'TUMACO Y PACIFICO NARINENSE':'Tumaco y Pacífico','OTRAS REGIONES DE COLOMBIA':'Otras regiones','COLOMBIA (NACIONAL)':'Nacional','VALLE DEL CAUCA':'Valle del Cauca','REGIONAL (FUERA DE COLOMBIA INCLUIDO)':'Regional','CAUCA Y SUROCCIDENTE':'Cauca','NARINO ANDINO Y DEPARTAMENTAL':'Nariño andino'}
def regn(s): return REG.get(unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().upper(),str(s))
docs=[]
for r in T:
    t=na(' '.join(str(x or '') for x in (r[3],r[8],r[9]))+' '+ab.get(norm(r[3])[:60],''))
    ti=na(r[3])
    pr=[k for k,p in PROB.items() if re.search(p,t)]
    if r[12]!='Sanidad' and not pr: continue
    mn=[k for k,p in MAN.items() if re.search(p,t)]
    if not pr: pr=['Enfermedades en general']
    try:y=int(str(r[1])[:4])
    except:y=None
    docs.append(dict(id=r[0],ti=r[3],y=y,reg=regn(r[13]),tema=r[12],prob=pr,man=mn or ['Sin manejo explícito'],dis=str(r[8] or ''),txt=t))
json.dump(docs,open('g25/sanidad_docs.json','w'),ensure_ascii=False)
print(len(docs))
print(collections.Counter(p for d in docs for p in d['prob']))
print(collections.Counter(m for d in docs for m in d['man']))
print(collections.Counter(d['dis'] for d in docs).most_common(12))
print([ (d['id'],d['ti'][:60]) for d in docs if 'Insectos plaga' in d['prob']])

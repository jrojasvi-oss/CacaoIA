# Gráficos adicionales de bibliometrix sobre los 387 documentos colombianos · 25 nov 2026
suppressMessages({library(bibliometrix); library(ggplot2)})
M <- read.csv("M387.csv", stringsAsFactors = FALSE, encoding = "UTF-8"); M[is.na(M)] <- ""; M$TI_ORIG <- NULL
M$PY <- suppressWarnings(as.numeric(M$PY)); M$TC <- 0
M$C1 <- NA; M$RP <- NA; M$AU_UN <- NA; M$SR <- M$UT; M$JI <- M$SO; M$J9 <- M$SO
class(M) <- c("bibliometrixDB","data.frame")
sw <- c("cif","par","pod","rot","spp","san","management","plan","norte","cacao","theobroma","cocoa","colombia","colombian","colombiano","colombiana","municipio","departamento","l","sas","evaluacion","evaluation","analisis","analysis","efecto","effect","effects","uso","use")
# unigramas y bigramas de título
M1 <- termExtraction(M, Field="TI", ngrams=1, stemming=FALSE, remove.numbers=TRUE, remove.terms=sw, verbose=FALSE)
f1 <- sort(table(unlist(strsplit(M1$TI_TM, ";"))), decreasing=TRUE); f1 <- f1[names(f1)!=""]
write.csv(data.frame(termino=names(f1), n=as.integer(f1)), "g387/terminos_1.csv", row.names=FALSE)
M2 <- termExtraction(M, Field="TI", ngrams=2, stemming=FALSE, remove.numbers=TRUE, remove.terms=sw, verbose=FALSE)
f2 <- sort(table(unlist(strsplit(M2$TI_TM, ";"))), decreasing=TRUE); f2 <- f2[names(f2)!=""]
write.csv(data.frame(termino=names(f2), n=as.integer(f2)), "g387/terminos_2.csv", row.names=FALSE)
# temas en tendencia
tt <- fieldByYear(M1, field="TI_TM", timespan=c(2000,2026), min.freq=5, n.items=4, graph=FALSE)
write.csv(tt$df, "g387/trend_topics.csv", row.names=FALSE)
# evolución temática: un mapa temático por periodo
for (p in list(c(1950,2009),c(2010,2019),c(2020,2026))) {
  Mp <- M2[!is.na(M2$PY) & M2$PY>=p[1] & M2$PY<=p[2],]; class(Mp) <- c("bibliometrixDB","data.frame")
  tm <- tryCatch(thematicMap(Mp, field="TI", n=200, minfreq=2, ngrams=2, size=0.5, n.labels=3, repel=TRUE, remove.terms=sw), error=function(e) {print(e); NULL})
  if (!is.null(tm)) { write.csv(tm$clusters, sprintf("g387/clusters_%d_%d.csv",p[1],p[2]), row.names=FALSE)
    ggsave(sprintf("g387/tm_%d_%d.png",p[1],p[2]), tm$map + ggtitle(sprintf("%d–%d (%d documentos)",max(p[1],min(Mp$PY)),p[2],nrow(Mp))), width=8, height=6.5, dpi=170) }
}
te <- tryCatch(thematicEvolution(M2, field="TI", years=c(2009,2019), n=200, minFreq=2, ngrams=2, remove.terms=sw), error=function(e) {print(e);NULL})
if (!is.null(te)) write.csv(te$Edges, "g387/evolucion_aristas.csv", row.names=FALSE)
if (!is.null(te)) saveRDS(te, "g387/te.rds")
# estructura conceptual (MCA sobre términos de título)
cs <- conceptualStructure(M1, field="TI", method="MCA", minDegree=8, clust=4, k.max=8, stemming=FALSE, labelsize=10, documents=10, graph=FALSE, remove.terms=sw)
ggsave("g387/estructura_conceptual.png", cs$graph_terms + ggtitle("Estructura conceptual (MCA, términos de título)"), width=10, height=7.5, dpi=170)
# Bradford
b <- bradford(M); write.csv(b$table, "g387/bradford.csv", row.names=FALSE)
ggsave("g387/bradford.png", b$graph + ggtitle("Ley de Bradford: fuentes núcleo"), width=10, height=6, dpi=170)
# tres campos (datos): autor - tema - región
write.csv(M[,c("UT","AU","DE","ID","SO","PY")], "g387/tres_campos.csv", row.names=FALSE)
cat("OK\n")
d <- cs$graph_terms$data; write.csv(d[, intersect(names(d), c("word","Dim.1","Dim.2","Dim1","Dim2","cluster","color","dim1","dim2","label"))], "g387/mca_terminos.csv", row.names=FALSE)
print(names(d))

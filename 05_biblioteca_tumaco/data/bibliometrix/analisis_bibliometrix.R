# Análisis bibliométrico de la biblioteca de cacao del suroccidente colombiano (270 documentos)
# bibliometrix 4.3.0 · Juan David Rojas Villafañe · 24 nov 2026
suppressMessages({library(bibliometrix); library(ggplot2)})
M <- read.csv("M.csv", stringsAsFactors = FALSE, encoding = "UTF-8")
M[is.na(M)] <- ""; M$TI_ORIG <- NULL
M$PY <- suppressWarnings(as.numeric(M$PY))
M$TC <- 0
M$C1 <- NA; M$RP <- NA; M$AU_UN <- NA; M$SR <- paste(M$UT); M$JI <- M$SO; M$J9 <- M$SO
class(M) <- c("bibliometrixDB", "data.frame")
res <- biblioAnalysis(M, sep = ";")
s <- summary(res, k = 15, pause = FALSE, verbose = FALSE)
write.csv(s$MainInformationDF, "resumen_principal.csv", row.names = FALSE)
write.csv(s$AnnualProduction, "produccion_anual.csv", row.names = FALSE)
write.csv(s$MostProdAuthors, "autores_mas_productivos.csv", row.names = FALSE)
write.csv(s$MostRelSources, "fuentes_mas_frecuentes.csv", row.names = FALSE)
L <- lotka(res); write.csv(L$AuthorProd, "lotka.csv", row.names = FALSE)
cat("Lotka beta:", L$Beta, " R2:", L$R2, "\n")
# Términos de título (bigramas) sin palabras vacías
sw <- c("de","del","la","las","el","los","en","y","con","para","por","una","un","al","sus","su","a","o","e","the","of","and","in","on","for","with","to","from","by","an","as","its","at","l","cacao","theobroma","cocoa","colombia","colombian","municipio","departamento","l.","s.a.s")
M <- termExtraction(M, Field = "TI", ngrams = 2, stemming = FALSE, language = "spanish", remove.numbers = TRUE, remove.terms = sw, keep.terms = NULL, verbose = FALSE)
NetMatrix <- biblioNetwork(M, analysis = "co-occurrences", network = "titles", sep = ";")
png("red_coterminos.png", width = 2200, height = 1600, res = 200)
net <- networkPlot(NetMatrix, normalize = "association", n = 40, Title = "Co-ocurrencia de términos de título (bigramas)", type = "fruchterman", size.cex = TRUE, size = 12, remove.multiple = FALSE, labelsize = 0.8, label.n = 40, edges.min = 1, remove.isolates = TRUE, cluster = "louvain", verbose = TRUE)
dev.off()
tm <- thematicMap(M, field = "TI_TM", n = 250, minfreq = 3, ngrams = 2, stemming = FALSE, size = 0.5, n.labels = 3, repel = TRUE, remove.terms = sw)
ggsave("mapa_tematico.png", tm$map + ggtitle("Mapa temático (términos de título)"), width = 11, height = 8, dpi = 200)
write.csv(tm$clusters, "mapa_tematico_clusters.csv", row.names = FALSE)
# Colaboración entre autores
NetA <- biblioNetwork(M, analysis = "collaboration", network = "authors", sep = ";")
png("red_coautoria.png", width = 2200, height = 1600, res = 200)
netA <- networkPlot(NetA, n = 40, Title = "Red de coautoría (40 autores más conectados)", type = "fruchterman", size = 10, size.cex = TRUE, remove.isolates = TRUE, labelsize = 0.8, cluster = "louvain", verbose = TRUE)
dev.off()
# Evolución temática por periodo
te <- tryCatch(thematicEvolution(M, field = "TI_TM", years = c(2014, 2020), n = 250, minFreq = 2, ngrams = 2, remove.terms = sw), error = function(e) NULL)
if (!is.null(te)) write.csv(te$Data, "evolucion_tematica.csv", row.names = FALSE)
saveRDS(M, "M_bibliometrix.rds")
cat("OK\n")

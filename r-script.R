library(factoextra)

####NOTE: ALL THIS IS COMMENTED OUT BECAUSE I DON'T READ THE XML DIRECTLY ANYMORE.
#### IT IS MUCH FASTER TO CONVERT TO CSV WITH XQUERY AND READ A TABLE INSTEAD


# library(xml2)
# library(XML)

#xml <- read_xml("<root><child><prop1/><prop2/><prop3/></child><child><prop1/></child></root>")

#NOTE: The default XML library for R (not xml2) will handle turning into a data frame pretty easily if each element (each word, I suppose) is under the root.


#xml <- xmlParse("<root><group><child><prop1/><prop2/><prop3/></child><child><prop1/></child></group><group><child><prop1/><prop2/><prop3/></child><child><prop1/></child></group></root>")
# 
# #results <- "C:/Users/T470s/Documents/GitHub/cltk-2025-atticus/atticus-study-results.xml"
# results <- "C:/Users/T470s/Documents/GitHub/cltk-2025-atticus/postagged_only.xml"
# perseus <- xmlParse(results)
# #perseus <- xmlTreeParse(results)
# #p_root <- xmlRoot(perseus)
# 
# #root <- xmlRoot(xml)
# 
# #xmlToDataFrame(nodes=xmlChildren(root[['group']]))
# 
# #test <- perseus$doc$children$root$children$work[[5]]$children$sentence
# 
# #system.time(data <- xmlToDataFrame(nodes=getNodeSet(perseus, "//word")))
# system.time(data <- xmlToDataFrame(perseus))

#xmlToDataFrame(nodes=xmlChildren(perseus$doc$children$root$children$work[[5]]$children$sentence))


#####Creating a new data frame with the number of each value
data <- read.csv("C:/Users/T470s/Documents/GitHub/cltk-2025-atticus/postagged_only.csv", na.strings="")

titles <- unique(data$title)
num_words <- table(data$title)
final.frame <- data.frame(title=titles)

for (i in 1:length(titles)) {
  frame <- data[data$title == titles[i],]
  frame <- subset(frame, select= c(-form, -path, -NumType))
  for (n in 2:length(frame)) {
    t <- table(frame[,n])
    t <- prop.table(t)
    names <- names(t)
    
    for (name_index in seq(1, length(names))) {
      final.frame[i, names[name_index]] <- unname(t[names[name_index]])
    }
  }
}

#Clean up NAs and filter out Cicero's works that are not the Letters to Atticus
final.frame[is.na(final.frame)] <- 0

#CAN GET RID OF THIS LATER WHEN I FIX TITLES
final.frame$title[46] <- "Apocolocynthosis"

cicero_works_nonatt <- c("M. Tulli Ciceronis Orationes", "Librorum de Re Publica Sex", "M. Tulli Ciceronis\nscripta quae manserunt omnia,\nfasc. 43", "de Natura Deorum", "M. Tullii Ciceronis opera quae supersunt omnia", "Tusculanae Disputationes", "M. Tulli Ciceronis Rhetorica, Tomus II", "De Senectute De Amicitia De Divinatione, With An English Translation", "Epistulae ad Familiares")

final.frame <- final.frame[(final.frame$title %in% cicero_works_nonatt) == FALSE,]

#Multiply to get larger values
final.frame[,2:55] <- final.frame[,2:55] * 100

#These values give NA, cause issues
final.frame[c("Neg", "Rcp", "Art")] <- NULL

rownames(final.frame) <- final.frame$title

data_kmeans <- final.frame[,2:52]
data_kmeans$Voc <- NULL

scaled_data <- scale(data_kmeans)

kmeans_basic_cluster <- kmeans(scaled_data, centers=4, nstart=20)
kmeans_basic_table <- data.frame(kmeans_basic_cluster$size, kmeans_basic_cluster$centers)
kmeans_basic_df <- data.frame(Clusters = kmeans_basic_cluster$cluster, final.frame)

hcut_results <- hcut(data_kmeans, k=4)

#Visualize ideal number of clusters
fviz_nbclust(data_kmeans, kmeans, method="wss", nstart=50)
fviz_nbclust(data_kmeans, hcut, method="wss")

#Plot hierarchy
fviz_cluster(kmeans_basic_cluster, data = data_kmeans, palette = c("#2E9FDF", "#00AFBB", "#E7B800", "red"), 
             geom = "point",
             ellipse.type = "convex", 
             ggtheme = theme_bw(),
             ) + geom_text(aes(label=rownames(data_kmeans)))

fviz_dend(hcut_results, palette = c("#2E9FDF", "#00AFBB", "#E7B800", "red"), 
          geom = "point",
          ellipse.type = "convex", 
          ggtheme = theme_bw(),
)


#Multiply by number of words in each work
for (i in 2:length(final.frame[1,])) {
  for (n in 1:length(final.frame[,1])) {
    final.frame[n,i] <- final.frame[n,i] * (10000 / num_words[[final.frame[n,]$title]])
  }
}

#Normalize
z <- final.frame[,-c(1,1)]
means <- apply(z,2,mean)
sds <- apply(z,2,sd)
nor <- scale(z,center=means,scale=sds)

#Get distances
distance <- dist(nor)

#####NOTES############
#69/641 items marked Poss were not possessive

final.frame$title <- lapply(X=final.frame$title, FUN=substr, start=1, stop=8)
#An alternative for doing this to rownames
rownames(final.frame) <- lapply(X=rownames(final.frame), FUN=substr, start=1, stop=12)


plot(hclust(distance), labels=final.frame$title)

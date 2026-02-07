
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
plot(hclust(distance), labels=titles)

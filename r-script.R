library(xml2)
library(XML)

#xml <- read_xml("<root><child><prop1/><prop2/><prop3/></child><child><prop1/></child></root>")

#NOTE: The default XML library for R (not xml2) will handle turning into a data frame pretty easily if each element (each word, I suppose) is under the root.


xml <- xmlParse("<root><group><child><prop1/><prop2/><prop3/></child><child><prop1/></child></group><group><child><prop1/><prop2/><prop3/></child><child><prop1/></child></group></root>")

results <- "C:/Users/T470s/Documents/GitHub/cltk-2025-atticus/atticus-study-results.xml"
perseus <- xmlParse(results)
#perseus <- xmlTreeParse(results)
p_root <- xmlRoot(perseus)

root <- xmlRoot(xml)

xmlToDataFrame(nodes=xmlChildren(root[['group']]))

#test <- perseus$doc$children$root$children$work[[5]]$children$sentence

data <- xmlToDataFrame(nodes=getNodeSet(perseus, "//word"))
#xmlToDataFrame(nodes=xmlChildren(perseus$doc$children$root$children$work[[5]]$children$sentence))


#####Creating a new data frame with the number of each value

data <- subset(data, select= -title)
titles <- unique(data$title)
final.frame <- data.frame(title=titles)

for (i in 1:length(titles)) {
  frame <- data[data$title == titles[i],]
  frame <- subset(frame, select= c(-form, -title, -path))
  for (n in c(1:22)) {
    t <- table(frame[,n])
    t <- prop.table(t)
    names <- names(t)
    
    for (name_index in seq(1, length(names))) {
      final.frame[i, names[name_index]] <- unname(t[names[name_index]])
    }
  }
}

for (i in 2:length(final.frame)) {
  frame <- final.frame[,i]
  final.frame[,i] <- frame * (10000/sum(frame))
}

#####NOTES############
#69/641 items marked Poss were not possessive


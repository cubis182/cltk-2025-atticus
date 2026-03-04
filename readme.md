This repository contains the data and scripts used in Matthew DeHass' 2026
 CAMWS presentation "Plebeius Sermo: A Corpus Study of Cicero's Letters to Atticus."
 
atticus-study-results.csv is a spreadsheet with all the postagged and lemmatized words.

postag-tests.csv is a spreadsheet I used to QA the data. Each line is a 
randomly selected word. The columns show a 1 where that field was 
correctly coded, and a 0 where the field was incorrectly coded. So, for 

example, the fourth field is part of speech, so, if the word is sum but the field said NOUN, it would have a 0.

data-processing.Rmd is an R Markdown file with all the statistical processing and graphs. data-processing.nb.html shows all of that off in a format that anyone is able to view.

postag_perseusDL.py is the python script I created which takes the Perseus Digital Library texts and postags them, saving the results to a file.

Here are some sources for the technology I used:
Peng Qi, Yuhao Zhang, Yuhui Zhang, Jason Bolton and Christopher D. Manning. 2020. Stanza: A Python Natural Language Processing Toolkit for Many Human Languages. 
  In Association for Computational Linguistics (ACL) System Demonstrations. 2020.

R Core Team (2025). _R: A Language and Environment for Statistical Computing_. R
  Foundation for Statistical Computing, Vienna, Austria. <https://www.R-project.org/>.

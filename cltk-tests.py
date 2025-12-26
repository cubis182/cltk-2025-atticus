
"""
Made for Python 3.13.7

=================================
*        Letters to Atticus     *
*        Parsing Tests          *
*         (Matthew DeHass)      *
=================================

"""

from cltk.nlp import NLP
import cltk.core.data_types as types
import cltk.morphosyntax.conll as conll

import os
os.chdir('C:/Users/T470s/Documents/GitHub/cltk-2025-atticus')
from importlib import *
import datetime



def conll_convert(doc: types.Doc) -> str:
    """
    conll_convert(doc: cltk.Doc)

    This function deals with an issue where
    the root of Conllu sentences in the 
    doc_to_conllu function is given as N/A 
    (the character '_') and not 0. The function
    loops between each line and replaces a '_'
    in the 7th position
    """

    returnStr = ''
    
    for sent in doc.sentences:
        stringVal = conll.words_to_conllu(sent.words)
        
        #Go line-by-line into the Conll and replace _ in the root position with 0

        finalStr = '\n'
        for line in stringVal.split('\n'):
            splitLine = line.split('\t')
            try:
                gov = splitLine[6]

                if splitLine[6] == '_':
                    splitLine[6] = '0'
                    line = '\t'.join(splitLine)
            except IndexError:
                pass
            
            #If it's the start of a new sentence, add a gap
            #try:

            #    if line[0:2] == '1\t':
            #        line = '\n' + line
            #except IndexError:
            #    pass

            finalStr += line + '\n'

        returnStr += finalStr
    
    return returnStr



nlp = NLP('lat', backend='stanza')

#doc = nlp.analyze(text='ego sum magister linguae latinae.')

import cltk.morphosyntax.conll as conll

text = open('./cic-att-8.11.txt', 'r', encoding='utf-8')
doc = nlp.analyze(text=text.read())

file = open('./text-cltk.txt', 'w', encoding='utf-8')
#file.write(conll.doc_to_conllu(doc))
#file.write(conll.words_to_conllu(doc.words))
file.write(conll_convert(doc))
file.close()

print(doc.words[0])
doc.words[0].upos.tag

#Testing an algorithm for printing the info to a file
AttOutput = open(f'./att-parsing-{datetime.datetime(1,1,1).today().strftime("%d-%m-%y")}.txt', 'w', encoding='utf-8')
i = 1
for sent in doc.sentences:
    AttOutput.write(f'Sentence {i}:\n')
    i += 1
    for w in sent.words:
        #Get the features in a string
        sFeats = ''
        try:
            for feat in w.features.features:
                sFeats += f'{feat.key}({feat.value}), '
        except AttributeError:
            pass
        AttOutput.write(f"{w.string}: postag(tag: {w.upos.tag}, name: {w.upos.name}), {sFeats}\n")
AttOutput.close()






"""
Some pathlib experiments
"""
"""
import pathlib
from pathlib import Path
print(Path('.').cwd())

p = Path('C:/Users/T470s/Documents')
list(p.glob('*'))[0]
print(p.parts)
print(p / 'Latin Seminar')
"""
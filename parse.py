# -*- coding: utf-8 -*-
"""
Filename: parse.py
Author: Matthew DeHass
Date: 12/21/2025
Version: 1.0
Description: 
    This script accepts a PDF of Shackleton Bailey's Teubner editions of 
    M. Ciceronis Epistulae ad Atticum. The clean_text() function returns
    a string with the text cleaned to remove header information. 

    Each page ends with a double line-break for identifying  page breaks
    later.

    Sources:

    Marcus Tullius Cicero, and Shackleton Bailey, David R.. Fasc 34 Epistulae ad Atticum: Vol. I. Libri I-VIII, Berlin, Boston: B. G. Teubner, 1987. https://doi.org/10.1515/9783110953831
                    

License: MIT License
Contact: matthew_dehass@yahoo.com
Dependencies: 
os
pdfplumber
re

"""

"""
TODO: Decide what to do on failure. How do I insert a page
back into the stream with no page identifiers? Easiest would be to
store each on a different line.
"""

import os
import pdfplumber
import re

Y_DENSITY = 8
DEBUG_DIR = "C:/Users/T470s/Documents/GitHub/cltk-2025-atticus"

#directory of the PDFs at the moment
dir = 'C:/Users/T470s/Documents/Letters to Atticus/'

#Testing the pdf cleaning functions on Books 1-8 first; here is the PDF
Vol1 = 'BOOKS 1-8 Ciceronis, M_ Tulli, Epistulae Ad Atticum_ Vol_ I, Libri I - -- [9783110953831 - Epistulae ad Atticum] Epistulae ad -- Bibliotheca scriptorum.pdf'


"""
Procedure:

Every page has 'n' number of lines at the end to be removed, from 0 to max page length.

I did 27 trials with the "layout=True" setting on extract_text and y_density=8. In all of them, 
when going from the bottom up, three empty lines in a row or more were always at the boundary
between the body and footer. There were gaps within the footer, but never more than 2.

It appears that the first line with actual text on it is always the header, need
to do more tests.


"""

pdfV1 = pdfplumber.open(str(dir + Vol1))

def save_output(text: str) -> bool:
    """
    Saves text to a file called 'letters-tests.txt'.
    The directory is specified in the DEBUG_DIR at 
    the top of the file."""
    with open((DEBUG_DIR + './letters-tests.txt'), 'w', encoding='utf-8') as output:
        output.write(text)
        output.close()

#NEEDED: REMOVE THE FRONTMATTER FROM THE PDF

def test_formatting(index: int=-1, y_density=Y_DENSITY):
    """
    THIS CODE IS NOT MODULAR AND SHOULD NOT BE USED OUTSIDE OF THE
    DEBUGGING PHASE. IF YOU DON'T KNOW WHAT THIS IS TALKING ABOUT,
    DON'T USE IT.
    Takes a page of the test PDF as specified by the arguments and 
    uses pdfplumber's extract_text() method, saving the output to
    a file. The purpose was to test the layout argument. Index is 
    the index of a page in the list of pages contained within the PDF.
    If no index is given, a random one is selected. Y_Density tells
    the extract_text() function how much space to put between lines.
    """

    final_index :int = index
    if index == -1:
        final_index = rand_letter()
    
    save_output(pdfV1.pages[final_index].extract_text(layout=True, y_density=y_density))

import random
def rand_letter() -> int:
    """
    NOT FOR USE IN FINAL PROGRAM 
    Gives the number of a random letter in the test PDF
    """
    return random.randint(0, len(pdfV1.pages))

    

def clean_text(page):
    """Takes a pdfplumber.Page and normalizes the text.
    The function removes headers, footers, and spaces. It joins words 
    across line boundaries, and adds a gap between letters.

    Dependencies:
    re
    pdfplumber

    """
    text = page.extract_text(layout=True, y_density=Y_DENSITY)
    
    #Create a version of the text which is split into lines
    #This variable is 
    stichic_text = text.splitlines() 

    num_lines = len(stichic_text) - 1 #subtract one to make indexing easy

    for n_line in range(num_lines, -1, -1):
        line_is_blank = (stichic_text[n_line].isspace())
        #print(line_is_blank)
        if line_is_blank:
            del stichic_text[n_line]
        else:
            break    

    num_lines = len(stichic_text) - 1 #subtract one to make indexing easy

    # Get the block of text at the end of the page which has
    #at minimum 3 blank lines above it. <string>.isspace() will 
    #return True if it's a blank line
    index_footer = -1
    num_empty_lines = 0 #Needs to equal three before exiting the loop
    for n_line in range(num_lines, -1, -1):
        if stichic_text[n_line].isspace():
            num_empty_lines += 1
        #If we hit text, we reset the empty line count
        else:
            num_empty_lines = 0
        
        #If we hit three empty spaces, save the index
        if num_empty_lines == 3:
            index_footer = n_line
            break
    
    print(f"clean_text(): Debug message: index_footer is equal to {index_footer}")

    try:
        del stichic_text[index_footer:]
    except IndexError:
        print(f"Error in clean_text(): Index of footer not found\n Below is the page:\n{text}")

    # Remove the header. This involves removing all the blank
    #lines at the start of the page, the first alphanum line, and 
    #all the blank lines after that

    for n_line in range(0, len(stichic_text)):
        #We delete the firsst line that is alpha num
        line = stichic_text[n_line]

        #print(line)
        if not line.isspace():
            print(f"The line to be deleted is: {line}")
            del stichic_text[n_line]
            break
    
    # TODO Remove the letter heading ('CICERO ATTICO SAL.')

    # TODO Remove Liber Primus, Secundus, etc.

    ##############EVERY FUNCTION AFTER THIS OPERATES ON THE WHOLE STRING############
    ##############MAKE SURE TO USE THE text VAR, NOT THE stichic_text var############
    text = '\n'.join(stichic_text)

    # Remove numeric
    text = re.sub('[0-9]', '', text)

    # Look for hyphens followed by a line break and zero or
    #more spaces/line breaks. After identifying these, all matches. 
    text = re.sub('- *\n[\n ]*', '', text)

    #Remove gaps between words bigger than a space
    text = re.sub('[\n ]+', ' ', text)

    # TODO Remove pairs of parentheses where one of the two are 
    #right next to a letter. In that case, it's usually an 
    #emendation NOTE: I realize there might be an issue where
    #the OCR doesn't correctly identify both parentheses, which
    #could cause this type of algorithm to fail. Need to think about 
    #this. This might be a step for manual correction

    #NOTE: I'm not removing punctuation, because I want the choice of
    #including or excluding it at the last stage.

    #NOTE TODO adding a line end after the page to make each one
    #fit on a new line, I'm not committed to doing this permanently, 
    #though
    return text + '\n\n'

#with pdfplumber.open(dir + Vol1) as pdf, open("volume1_books1-8.txt", "w", encoding="utf-8") as f:
    #for page in pdf.pages:
        #print(clean_text(page))

# TODO THESE ARE LINES OF CODE FOR DEBUGGING I NEED TO CLEAN UP
#page = pdfV1.pages[143]
#print(page.extract_text(layout=True, y_density=Y_DENSITY))
#print(clean_text(page))
#save_output(clean_text(page))

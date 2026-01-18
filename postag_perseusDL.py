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

RESPONSE: Create an XML file to store the data. Structure:

<root>
    <work>
        <plaintext @reviewed="(accepted|rejected|notreviewed|)"/>
        <page>
            <postagged/>
        </page>
    </work>
</root>

Solutions required:
- Functions for quickly opening the file and accessing data.
- A command-line tool for reviewing the data. Needs to pretty-print it too.
"""

import os
import pdfplumber
import re

Y_DENSITY = 8
DEBUG_DIR = "C:/Users/T470s/Documents/GitHub/cltk-2025-atticus"

# directory of the PDFs at the moment
dir = "C:/Users/T470s/Documents/Letters to Atticus/"

# Testing the pdf cleaning functions on Books 1-8 first; here is the PDF
Vol1 = "BOOKS 1-8 Ciceronis, M_ Tulli, Epistulae Ad Atticum_ Vol_ I, Libri I - -- [9783110953831 - Epistulae ad Atticum] Epistulae ad -- Bibliotheca scriptorum.pdf"


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
    with open((DEBUG_DIR + "./letters-tests.txt"), "w", encoding="utf-8") as output:
        output.write(text)
        output.close()


# NEEDED: REMOVE THE FRONTMATTER FROM THE PDF


def test_formatting(index: int = -1, y_density=Y_DENSITY):
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

    final_index: int = index
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

    # Create a version of the text which is split into lines
    #
    stichic_text = text.splitlines()

    num_lines = len(stichic_text) - 1  # subtract one to make indexing easy

    for n_line in range(num_lines, -1, -1):
        line_is_blank = stichic_text[n_line].isspace()
        # print(line_is_blank)
        if line_is_blank:
            del stichic_text[n_line]
        else:
            break

    num_lines = len(stichic_text) - 1  # subtract one to make indexing easy

    # Get the block of text at the end of the page which has
    # at minimum 3 blank lines above it. <string>.isspace() will
    # return True if it's a blank line
    index_footer = -1
    num_empty_lines = 0  # Needs to equal three before exiting the loop
    for n_line in range(num_lines, -1, -1):
        if stichic_text[n_line].isspace():
            num_empty_lines += 1
        # If we hit text, we reset the empty line count
        else:
            num_empty_lines = 0

        # If we hit three empty spaces, save the index
        if num_empty_lines == 3:
            index_footer = n_line
            break

    print(f"clean_text(): Debug message: index_footer is equal to {index_footer}")

    try:
        del stichic_text[index_footer:]
    except IndexError:
        print(
            f"Error in clean_text(): Index of footer not found\n Below is the page:\n{text}"
        )

    # Remove the header. This involves removing all the blank
    # lines at the start of the page, the first alphanum line, and
    # all the blank lines after that

    for n_line in range(0, len(stichic_text)):
        # We delete the firsst line that is alpha num
        line = stichic_text[n_line]

        # print(line)
        if not line.isspace():
            print(f"The line to be deleted is: {line}")
            del stichic_text[n_line]
            break

    # TODO Remove the letter heading ('CICERO ATTICO SAL.')

    # TODO Remove Liber Primus, Secundus, etc.

    ##############EVERY FUNCTION AFTER THIS OPERATES ON THE WHOLE STRING############
    ##############MAKE SURE TO USE THE text VAR, NOT THE stichic_text var############
    text = "\n".join(stichic_text)

    return remove_invalid_characters(text)


def remove_invalid_characters(text: str) -> str:
    """
    Used in the clean_text() function.
    Cleans up the whole string by removing numeric and empty characters"""
    # Remove numeric
    text = re.sub("[0-9]", "", text)

    # Look for hyphens followed by a line break and zero or
    # more spaces/line breaks. After identifying these, all matches.
    text = re.sub("- *\n[\n ]*", "", text)

    # Remove gaps between words bigger than a space
    text = re.sub("[\n ]+", " ", text)

    # TODO Remove pairs of parentheses where one of the two are
    # right next to a letter. In that case, it's usually an
    # emendation NOTE: I realize there might be an issue where
    # the OCR doesn't correctly identify both parentheses, which
    # could cause this type of algorithm to fail. Need to think about
    # this. This might be a step for manual correction

    # NOTE: I'm not removing punctuation, because I want the choice of
    # including or excluding it at the last stage.

    # NOTE TODO adding a line end after the page to make each one
    # fit on a new line, I'm not committed to doing this permanently,
    # though

    # Add a newline character after each sentence for easy reading.
    split = text.split(".")
    text = ".\n".join(split)

    return text + "\n\n"


# TODO THESE ARE LINES OF CODE FOR DEBUGGING I NEED TO CLEAN UP
# page = pdfV1.pages[143]
# print(page.extract_text(layout=True, y_density=Y_DENSITY))
# print(clean_text(page))
# save_output(clean_text(page))


# -*- coding: utf-8 -*-
"""
Filename: postag-perseusDL.py
Author: Matthew DeHass
Date: 1/6/2026
Version: 1.0
Description:
    This script uses Etree to parse the Perseus DL texts
    and then uses the CLTK to add postags.

    Step 1: Load and parse the Perseus data

    Make sure that the Perseus data excludes text from within these elements:
    (note: tei namespace is defined within the file below)
    tei:note
    tei:del
    head
    sic #this one is a child of the <choice/> element, and the <corr/> tag next to it has the correct version

    Step 2: Add the


License: MIT License
Contact: matthew_dehass@yahoo.com
Dependencies:
"""


def prettyprint(element, **kwargs):
    xml = etree.tostring(element, pretty_print=True, **kwargs)
    print(xml.decode(), end="")


from lxml import etree
from lxml.builder import E
from pathlib import Path
from random import choice
import re

# Add the directory containing your module to the Python path
import os
import sys

dir_path = Path(__file__)
dir_path = dir_path.parents[0]
sys.path.append(dir_path)
os.chdir(dir_path)

s_xml_template = """
<root xmlns:xsi="http://www.w3.org/2001/XMLSchema">
    <work>
        <title/>
        <author/>
        <plaintext/>
        <postagged reviewed=/>
    </work>
</root>
"""

# Retrieve the schema that sets the format for the data we'll parse
data_schema = etree.XMLSchema(file="results-schema.xsd")


parser_xml_template = etree.XMLParser(schema=data_schema)

try:
    xml_template = etree.fromstring(s_xml_template, parser=parser_xml_template)
except etree.XMLSyntaxError as invalid_error:
    print(
        f"Error! The default XML format doesn't match the schema. Details:\n {invalid_error.args}."
    )


inval_tags = [
    "note",
    "del",
    "head",
    "speaker",
    "sic",
    #    "corr",
    # "choice",
    "{http://www.tei-c.org/ns/1.0}note",
    "{http://www.tei-c.org/ns/1.0}del",
    "{http://www.tei-c.org/ns/1.0}head",
    "{http://www.tei-c.org/ns/1.0}speaker",
    "{http://www.tei-c.org/ns/1.0}sic",
    #    "{http://www.tei-c.org/ns/1.0}corr",
    # "{http://www.tei-c.org/ns/1.0}choice",
]


def is_valid_tag(element) -> int:
    l = list(element.iterancestors(tag=inval_tags))
    boolean = bool(l)
    if element.tag in inval_tags:
        return 0
    elif boolean:
        return -1
    else:
        return 1


def get_text(element) -> str:
    string = ""
    sTail = element.tail
    sText = element.text
    parent = element.getparent()
    pText = parent.text
    pTail = parent.tail

    if pTail:
        if any(re.search("[A-Za-z0-9]", s) for s in pTail):
            return string

    tagValid = is_valid_tag(element)
    if tagValid == 1:
        if sText:
            string += sText

    # Make sure it has a tail and that it isn't inside of an invalid tag
    if (sTail) and (tagValid == 1):
        if not (re.search("[A-Za-z0-9]", sTail) is None):
            children = [x for x in element.iterdescendants() if (x.tail or x.text)]
            for child in children:
                if is_valid_tag(child):
                    string += ("" if child.text is None else child.text) + (
                        "" if child.tail is None else child.tail
                    )
        string += sTail
    elif sTail:
        string += sTail

    # DEBUG
    if string == "":
        pass

    return string


def TEI_to_text(pathArg="", index=-1):
    """
    This function returns a plaintext version of the TEI XML files in the
    Perseus Digital Library. The function currently assumes the path to the
    Perseus DL is the one on my system:
    C:/Users/T470s/Documents/GitHub/cltk-2025-atticus/perseus-debug.txt.
    The function can work with no namespace or TEI.
    @param pathArg: An optional string or list of strings which gives the specific path(s) you want to parse. Type "rand" if you want a random one
    @param index: An optional integer index of the location in the file list of the path. Can also be a sequence of integers
    """

    # path to PerseusDL
    dir = Path("C:/Users/T470s/Documents/GitHub/canonical-latinLit/data/")

    # paths to all the files in the corpus, identified by -lat and the .xml extension.
    paths = list(dir.glob("**/**-lat*.xml"))

    # Check whether the index argument was given and whether it's a valid value. If both a path or index is given, default to index
    if index != -1:
        if isinstance(index, list):
            pathsByIndex = []
            for i in index:
                pathsByIndex.append(paths[i])
            paths = pathsByIndex
        else:
            paths = [paths[index]]

    # Check whether the path argument was given and whether it's a valid value
    if index == -1:
        if pathArg == "rand":
            paths = [choice(paths)]
        elif pathArg == "":
            pass
        elif isinstance(pathArg, list):
            paths = []
            for s in pathArg:
                paths.append(s)

    # An lxml.etree._Element which is a single element, <root></root>
    worksProcessed = etree.fromstring("<root></root>")

    for path in paths:
        # Don't resolve entities to avoid potential errors (entities are things like &colon;)
        parser = etree.XMLParser(resolve_entities=False)
        tree = etree.parse(path, parser)  # Use path 22 for debugging
        tei = {"tei": "http://www.tei-c.org/ns/1.0"}

        # Get the root of the tree. This variable will eventually hold the tei:body element
        body = tree.getroot()

        # We need to make sure it's a real TEI file with the xml namespace.
        # Some files in the PerseusDL use TEI without the namespace

        # First, assume no namespace
        expression = ".//body"

        # XPath expression for the title
        title = "./tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text()"
        titleString = ""

        # XPath expression for the author's name
        author = "./tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:author/text()"
        authorString = ""

        # However, if there is a namespace with the TEI URI (which is given in the 'tei' variable above), we need a tei namespace declared
        nsmap = list(body.nsmap.values())
        if tei["tei"] == nsmap[0]:
            expression = ".//tei:body"
            body = tree.xpath(expression, namespaces=tei)
            titleString = tree.xpath(title, namespaces=tei)
            authorString = tree.xpath(author, namespaces=tei)
        # If there is no namespace, stick with the './/body' xpath expression with no namespace
        else:
            body = tree.xpath(expression)
            titleString = tree.xpath(re.sub("tei:", "", title))
            authorString = tree.xpath(re.sub("tei:", "", author))

        # Remember, when there are potentially Greek characters, we need encoding set to UTF-8.
        # This debug file will store the results before the final version of the program
        debug = open(
            "C:/Users/T470s/Documents/GitHub/cltk-2025-atticus/perseus-debug.txt",
            "w",
            encoding="utf-8",
        )
        debug.write(path.__str__())

        if len(body):
            body = body[0]

        string = "\n"
        for element in body.iter():
            string += get_text(element)

        string = re.sub("\t", "", string)

        string = remove_invalid_characters(string)

        work = E.work(
            E.title(),
            E.author(),
            E.plaintext(string, reviewed="notreviewed"),
        )
        worksProcessed.append(work)

        return worksProcessed


def create_page(page_text: str, title: str, author: str) -> etree._Element:
    """This function returns a set of elements in the format defined in
    results-schema.xsd in this repository. It takes the cleaned text for
    a file, which is generated in the TEI_to_text function"""

    E.work(
        E.title(),
        E.author(),
        E.plaintext(string, reviewed="notreviewed"),
    )


# QUESTIONS TO ANSWER:
# How to save the results?
#   As XML?
#   As a CSV?
#   As CONLLU?
#   XML might be ideal, because I needed a structured way to look at the data (divided into texts, which are further divided into words)
#   TEI XML would be

if __name__ == "__main__":
    print(Path(__file__).parents[0])
    # Debug
    print(f"Printing the xml template:\n{xml_template}")

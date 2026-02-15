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

    NOTE HERE ARE SOME ONGOING ISSUES:
    The '/' is used to signal an apex in Cicero's De Re Publica, so "A/strologorum si/gna"

    daturu's es cenam

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
from copy import deepcopy
import pdfplumber
import re
import regex
import datetime

from lxml import etree  # type: ignore
from lxml.builder import E
from pathlib import Path
from random import choice
import io

Y_DENSITY = 4
EMPTY = 4
DEBUG_DIR = "C:/Users/T470s/Documents/GitHub/cltk-2025-atticus"

# directory of the PDFs at the moment
dir = "C:/Users/T470s/Documents/Letters to Atticus/"

# Testing the pdf cleaning functions on Books 1-8 first; here is the PDF
Vol1 = "BOOKS 1-8 Ciceronis, M_ Tulli, Epistulae Ad Atticum_ Vol_ I, Libri I - -- [9783110953831 - Epistulae ad Atticum] Epistulae ad -- Bibliotheca scriptorum.pdf"
Vol2 = "BOOKS 9-16 Ciceronis, M_Tulli, epistulae ad Atticum__ Vol_II, Libri -- [9783110953824 - Epistulae ad Atticum] Epistulae ad -- Bibliotheca scriptorum Graecorum et -- 9783110953824 -- 6452b88664ff783678ce.pdf"


"""
Procedure:

Every page has 'n' number of lines at the end to be removed, from 0 to max page length.

I did 27 trials with the "layout=True" setting on extract_text and y_density=8. In all of them, 
when going from the bottom up, three empty lines in a row or more were always at the boundary
between the body and footer. There were gaps within the footer, but never more than 2.

It appears that the first line with actual text on it is always the header, need
to do more tests.


"""


def save_output(text: str, method: str = "w") -> None:
    """
    Saves text to a file called 'letters-tests.txt'.
    The directory is specified in the DEBUG_DIR at
    the top of the file."""
    with open((DEBUG_DIR + "./letters-tests.txt"), method, encoding="utf-8") as output:
        output.write(datetime.datetime.now().isoformat() + "\n")
        output.write(str(text) + "\n")
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
    pdfV1 = pdfplumber.open(str(dir + Vol1))
    pdfV2 = pdfplumber.open(str(dir + Vol2))
    pages = pdfV1.pages[keep_Vol1:] + pdfV2.pages[keep_Vol2:]

    final_index: int = index
    if index == -1:
        final_index = rand_letter()

    save_output(pages[final_index].extract_text(layout=True, y_density=y_density))


import random


def rand_letter() -> int:
    """
    NOT FOR USE IN FINAL PROGRAM
    Gives the number of a random letter in the test PDF
    """
    pdfV1 = pdfplumber.open(str(dir + Vol1))
    pdfV2 = pdfplumber.open(str(dir + Vol2))
    return random.randint(0, len(pdfV1.pages))


def rand_page():
    """
    NOT FOR USE IN FINAL PROGRAM
    Gives the number of a random letter in the test PDF
    """
    pdfV1 = pdfplumber.open(str(dir + Vol1))
    pdfV2 = pdfplumber.open(str(dir + Vol2))
    pages = pdfV1.pages[keep_Vol1:] + pdfV2.pages[keep_Vol2:]
    rand = random.randint(0, len(pages))
    return pages[rand]


def get_pages():
    pdfV1 = pdfplumber.open(str(dir + Vol1))
    pdfV2 = pdfplumber.open(str(dir + Vol2))
    pages = pdfV1.pages[keep_Vol1:] + pdfV2.pages[keep_Vol2:]
    return pages


def clean_text(page, spaces_algorithm=True):
    """Takes a pdfplumber.Page and normalizes the text.
    The function removes headers, footers, and spaces. It joins words
    across line boundaries, and adds a gap between letters.

    spaces_algorithm, when set to true, performs the heuristic for removing the footer

    Dependencies:
    re
    pdfplumber

    """
    text = page.extract_text(layout=True, y_density=Y_DENSITY)

    # Create a version of the text which is split into lines
    #
    stichic_text = text.splitlines()

    num_lines = len(stichic_text) - 1  # subtract one to make indexing easy

    # Remove blank lines at the end
    for n_line in range(num_lines, -1, -1):
        line_is_blank = stichic_text[n_line].isspace()
        # print(line_is_blank)
        if line_is_blank:
            del stichic_text[n_line]
        else:
            break

    num_lines = len(stichic_text) - 1  # subtract one to make indexing easy

    if spaces_algorithm:
        # Get the block of text at the end of the page which has
        # at minimum EMPTY blank lines above it. <string>.isspace() will
        # return True if it's a blank line
        index_footer = -1
        num_empty_lines = 0  # Needs to equal three before exiting the loop
        for n_line in range(num_lines, -1, -1):
            line = stichic_text[n_line]

            if line.isspace():
                num_empty_lines += 1
            # If we hit text, we reset the empty line count
            else:
                num_empty_lines = 0

            # If we hit three empty spaces, save the index
            if num_empty_lines == EMPTY:
                index_footer = n_line
                break

        # print(f"clean_text(): Debug message: index_footer is equal to {index_footer}")

        try:
            del stichic_text[index_footer:]
        except IndexError:
            print(
                f"Error in clean_text(): Index of footer not found\n Below is the page:\n{text}"
            )

    stichic_text = remove_app_crit(stichic_text)
    # Remove the header. This involves removing all the blank
    # lines at the start of the page, the first alphanum line, and
    # all the blank lines after that

    for n_line in range(0, len(stichic_text)):
        # We delete the firsst line that is alpha num
        line = stichic_text[n_line]

        # print(line)
        if not line.isspace():
            # print(f"The line to be deleted is: {line}")
            del stichic_text[n_line]
            break

    # TODO Remove the letter heading ('CICERO ATTICO SAL.')

    # TODO Remove Liber Primus, Secundus, etc.

    ##############EVERY FUNCTION AFTER THIS OPERATES ON THE WHOLE STRING############
    ##############MAKE SURE TO USE THE text VAR, NOT THE stichic_text var############
    text = "\n".join(stichic_text)
    text = fix_common_ocr(text)
    return remove_invalid_characters(text)


def remove_app_crit(stichic_text: list[str]) -> list[str]:
    # Only check the last half for markers of an app crit
    length = len(stichic_text)
    stichic_copy = stichic_text
    stichic_text = [
        x
        for x in stichic_text
        if not (
            re.search(
                "( Δ | : |om\\.|ed\\.|Ep\\.|cett\\.| Ω | λ | Σ | Δ | ς |vel sim\\.|Corradus|Casaubon|Madvig|Phoenix|Kayser|Goodyear|Housman|Meutzner|Schmidt|Reid|cod\\.|codd\\.|corr\\.|MSS\\.)",
                x,
            )
        )
        or stichic_copy.index(x) < int(0.75 * length)
    ]
    return stichic_text


def fix_common_ocr(text: str):
    """
    Replace common mistakes, like 'tarnen' with 'tamen'
    """
    text = text.replace("tarnen", "tamen")
    text = text.replace("Ser.", "Scr.")
    return text


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

    text = re.sub("\n\n", "", text)

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
    # The regex doesn't count occurences of common epistolary abbreviations and abbreviated Praenomina.
    # NOTE need to use the regex module instead of re (installed by -m pip install regex).
    # NOTE    The reason for using regex is because the lookbehind assertion is not a fixed width
    split = regex.split(
        "(?<!Prid|prid|Kal|kal|Non|Id|a|d|Ian|Febr|Mart|Apr|Mai|Iun|Quint|Sext|Sept|Oct|Nov|Dec|Nrib|Luc|Agr|Ap|A|K|D|F|C|Cn|L|Mam|M'|M|N|Oct|Opet|Post|Pro|P|Q|Sert|Ser|Sex|S|St|Ti|T|Vol|Vop)\\.",
        text,
    )
    text = ".\n".join(split)

    return text


def validate_page(page: str) -> bool:
    """
    TODO ADD THIS TO THE process_pages_att() FUNCTION!!!!!!!
    Docstring for validate_page
    Currently, some pages are going through without any text. Need to flag these in the
    results file.

    :param page: The string extracted from the PDF
    :type page: str
    :return: Description
    :rtype: bool
    """
    b = any(i.isalnum() for i in page)
    return b


# Index of the first real page in each PDF
# This is important for the following function, process_pages_att()
keep_Vol1 = 18
keep_Vol2 = 4


def process_pages_att() -> etree._Element:
    """
    Docstring for process_pages
    This function is for the letters to Atticus PDFs only.
    It opens the files, processes each page, and adds them
    to an element.
    """

    # Open the PDFs
    with pdfplumber.open(str(dir + Vol1)) as pdfV1:
        with pdfplumber.open(str(dir + Vol2)) as pdfV2:
            # Get a list of all the pages
            pages = pdfV1.pages[keep_Vol1:] + pdfV2.pages[keep_Vol2:]

            # list comprehension with clean_text()
            str_pages = [clean_text(p) for p in pages]

            tree = etree.Element("pages")

            # Combine the text together
            plaintext = "".join(str_pages)

            i = 0
            for p in str_pages:
                # create a page element (any arbitrary element can fit in <content/>)
                p_element: etree._Element = etree.Element("page")
                # Add the page's processed text as the element's content
                if i in [39, 241, 247, 249, 252, 430, 481, 486, 595, 672]:
                    # These pages proved troublesome, need manual handling
                    special_text = pages[i]
                    special_text = clean_text(
                        special_text, spaces_algorithm=False
                    )  # make sure to unlist it!!!!
                    p_element.text = special_text
                else:
                    p_element.text = p

                p_element.set("n", str(i))

                # If the page doesn't validate, that currently means it's empty. i
                # Add an attribute that identifies it as empty
                b = validate_page(p)
                if not b:
                    p_element.set("flag", "empty")

                # Add the final page element to the content we are going to add
                tree.append(p_element)
                i += 1

            final_work = create_work(
                tree, "Letters to Atticus", "Marcus Tullius Cicero", Vol1, pages=True
            )

            # add the plaintext
            final_work.append(E.content(plaintext, type="plaintext"))
            return final_work


def save_pages_att(work: etree._Element) -> None:
    """
    This function takes the results of process_pages_att() and saves it to the results file
    (see the results_file var below)

    :param work: An element tree returned from process_pages_att()
    :type work: etree._Element
    """

    data_file = open_results()
    add_work(work, data_file=data_file)
    write_results(data_file)


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


# Add the directory containing your module to the Python path
import os
import sys

dir_path = Path(__file__)
dir_path = dir_path.parents[0]
sys.path.append(str(dir_path))
os.chdir(dir_path)

# TODO CREATE A TABLE OF CONTENTS FOR ALL THESE NEW FUNCTIONS!!!!

s_xml_template = """
<root xmlns:xsi="http://www.w3.org/2001/XMLSchema">
    <work reviewed="UNREVIEWED">
        <title/>
        <author/>
        <path></path>
        <content type="plaintext"/>
        <content type="postagged"/>
    </work>
</root>
"""

# Retrieve the schema that sets the format for the data we'll parse
data_schema: etree.XMLSchema = etree.XMLSchema(file="results-schema.xsd")
# data_schema: etree.XMLSchema = etree.XMLSchema(file="C:/Users/T470s/Documents/GitHub/cltk-2025-atticus/results-schema.xsd")

# NOTE: this template is NEVER to be modified directly. Assign it to a
# new variable each time.
parser_xml_template = etree.XMLParser(schema=data_schema)

try:
    xml_template: etree._Element = etree.fromstring(
        s_xml_template, parser=parser_xml_template
    )
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
    "bibl",
    "ex",
    "expan",
    #    "corr",
    # "choice",
    "{http://www.tei-c.org/ns/1.0}note",
    "{http://www.tei-c.org/ns/1.0}del",
    "{http://www.tei-c.org/ns/1.0}head",
    "{http://www.tei-c.org/ns/1.0}speaker",
    "{http://www.tei-c.org/ns/1.0}sic",
    "{http://www.tei-c.org/ns/1.0}bibl",
    "{http://www.tei-c.org/ns/1.0}ex",  # When an abbr / expan is given, let's go with the abbreviated form. The reason is given in a comment just under this
    #    "{http://www.tei-c.org/ns/1.0}corr",
    # "{http://www.tei-c.org/ns/1.0}choice",
]

# NOTE For abbreviations, their usage in the Perseus DL is inconsistent. Sometimes <abbr/> surrounds both the abbreviation and the exputf-8on. Other times, the abbreviation is next to the exputf-8on.
# However, the exputf-8ons are consistent, so we'll just get rid of those. I would prefer the expanded forms, but this is cleaner for now.


def is_valid_tag(element: etree._Element) -> int:
    """
    Checks whether a tag from a TEI:XML document is valid. A valid tag is one whose text we want for the purpose of processing the text. A tag like <note> has irrelevant text, so it's invalid. See the inval_tags variable above for a full list
    """
    l: list = list(element.iterancestors(tag=inval_tags))
    boolean = bool(l)
    if boolean:
        return -1
    elif element.tag in inval_tags:
        return 0
    else:
        return 1


def has_tail(element) -> bool:
    try:
        tail = element.tail
        if any(re.search("[A-Za-z0-9]", s) for s in tail):
            return True
        else:
            return False
    except TypeError:
        return False


def get_text(element) -> str:
    string = ""
    sTail: str = element.tail
    sText: str = element.text
    parent: etree._Element = element.getparent()
    pText: str = parent.text
    pTail: str = parent.tail

    if pTail:
        if has_tail(parent):
            return string

    tagValid = is_valid_tag(element)
    if tagValid == 1:
        if sText:
            string += sText

    # Make sure it has a tail with alphanumeric characters in it and that it isn't inside of an invalid tag
    if (has_tail(element)) and (tagValid == 1):
        children: list = [x for x in element.iterdescendants() if (x.tail or x.text)]
        for child in children:
            if is_valid_tag(child):
                string += ("" if child.text is None else child.text) + (
                    "" if child.tail is None else child.tail
                )
        string += sTail
    elif sTail and tagValid > -1:
        string += sTail

    # DEBUG
    if string == "":
        pass

    if element.tag == "{http://www.tei-c.org/ns/1.0}add":
        pass

    return string


def perseus_to_file(pathArg, index) -> None:
    """
    TODO TEST!
    This function wraps around the TEI_to_text file, adding each file to the output data file

    @param pathArg : A list of strings which gives the specific path(s) you want to parse. Type "rand" if you want a random one, or pass "" to NEEDSDOC
    @param index   : An integer index of the location in the file list of the path. Can also be a sequence of integers. Enter -1 for default behavior NEEDSDOC
    """

    # File the results will go in.
    data_file: etree._Element = open_results()

    list_of_works = TEI_to_text(pathArg=pathArg, index=index)

    for work in list_of_works:
        add_work(work, data_file)

    # Finally, add the updated results
    write_results(data_file=data_file)


def write_results(data_file: etree._ElementTree) -> None:
    """
    NEEDSDOC
    Docstring for write_results

    :param data_file: Description
    :type data_file: etree._Element
    """
    # Save the old one to a backup
    # old_tree = open_results()
    # filename = "results_backup_" + datetime.datetime.now().isoformat() + ".xml"
    # old_tree.getroottree().write(
    #    filename,
    #    encoding="utf-8",
    # )

    data_file.write(results_file, encoding="utf-8")


def get_paths() -> list[Path]:
    """
    Returns a list of paths to all Perseus DL Latin texts"""

    # path to PerseusDL
    dir: Path = Path("C:/Users/T470s/Documents/GitHub/canonical-latinLit/data/")

    # paths to all the files in the corpus, identified by -lat and the .xml extension.
    return list(dir.glob("**/**-lat*.xml"))


def get_title_auth_body(tree: etree._ElementTree) -> dict:
    """ """

    # We need to make sure it's a real TEI file with the xml namespace.
    # Some files in the PerseusDL use TEI without the namespace

    tei: dict = {"tei": "http://www.tei-c.org/ns/1.0"}

    # First, assume no namespace
    expression: str = ".//body"

    # XPath expression for the title
    # TODO Debug this title creator; it didn't work for Pro roscio
    title: str = "./teiHeader/fileDesc/titleStmt/title"
    titleString: str = ""

    # XPath expression for the author's name
    author: str = "./teiHeader/fileDesc/titleStmt/author"
    authorString: str = ""

    # However, if there is a namespace with the TEI URI (which is given in the 'tei' variable above), we need a tei namespace declared
    nsmap: list = list(tree.nsmap.values())
    try:
        is_TEI: bool = tei["tei"] == nsmap[0]
    except IndexError:
        is_TEI: bool = False

    body = __run_xpath(expression, is_TEI, tree, tei)

    # We need to test a few things in case the title isn't in the right spot
    titleEl = __run_xpath(title, is_TEI, tree, tei)

    # if titleEl is None:
    #    titleEl = __run_xpath(".//biblStruct/monogr/title", is_TEI, tree, tei)

    authorEl = __run_xpath(author, is_TEI, tree, tei)

    # if authorEl is None:
    #    authorEl = __run_xpath(".//biblStruct//author", is_TEI, tree, tei)

    # If we still don't have a valid author or title node, we give up
    if titleEl is not None:
        titleString = titleEl.text
    else:
        titleString = ""

    if authorEl is not None:
        authorString = authorEl.text
    else:
        authorString = ""

    return {"body": body, "title": titleString, "author": authorString}


def __run_xpath(expr: str, is_tei: bool, tree: etree._Element, tei: dict):
    """
    NEEDSDOC"""

    if is_tei:
        expr = re.sub("/(?=[A-Za-z0-9])", f"/tei:", expr)
        # make sure no namespace is in front of 'text()'
        expr = re.sub("tei:text\\(\\)", "text()", expr)
        elem = tree.find(expr, namespaces=tei)
        return elem
    else:
        elem = tree.find(expr)
        return elem


def TEI_to_text(pathArg, index) -> list[etree._Element]:
    """
    This function returns a plaintext version of the TEI XML files in the
    Perseus Digital Library. The function currently assumes the path to the
    Perseus DL is the one on my system:
    C:/Users/T470s/Documents/GitHub/cltk-2025-atticus/perseus-debug.txt.
    The function can work either with no namespace or TEI.

    @param pathArg : A list of strings which gives the specific path(s) you want to parse. Type "rand" if you want a random one, or pass "" to NEEDSDOC
    @param index   : An integer index of the location in the file list of the path. Can also be a sequence of integers. Enter -1 for default behavior NEEDSDOC
    """

    # Get the Perseus DL paths
    paths = get_paths()

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
    else:
        # If the pathArg is rand, that means we select a random path.
        # If the pathArg is the default value, we already got all the paths we need with the get_paths()
        # If we passed a list of paths to pathArg, we replace paths with that list
        if pathArg == "rand":
            paths = [choice(paths)]
        elif pathArg == "":
            pass
        elif isinstance(pathArg, list):
            # Don't know why I went with this method of assignment, but I won't touch it until I debug this function
            paths = []
            for s in pathArg:
                paths.append(s)

    # An lxml.etree._Element which is a single element, <root></root>
    worksProcessed: list = []

    for path in paths:
        # Don't resolve entities to avoid potential errors (entities are things like &colon;)
        parser: etree.XMLParser = etree.XMLParser(resolve_entities=False)
        tree: etree.ElementTree = etree.parse(path, parser)  # Use path 22 for debugging

        # Get the root of the tree. This variable will eventually hold the tei:body element
        body: etree._Element = tree.getroot()

        authority_dict = get_title_auth_body(body)

        body = authority_dict["body"]
        titleString = authority_dict["title"]
        authorString = authority_dict["author"]

        # Remember, when there are potentially Greek characters, we need encoding set to utf-8.
        # This debug file will store the results before the final version of the program
        debug: io.TextIOWrapper = open(
            "C:/Users/T470s/Documents/GitHub/cltk-2025-atticus/perseus-debug.txt",
            "w",
            encoding="utf-8",
        )
        debug.write(path.__str__())
        """
        if len(body):
            body = body[0]"""

        # Now we have the <body> element, let's get the text######################3

        # Add the text for each element, using the get_text() function
        string: str = "\n"
        for element in body.iter():
            string += get_text(element)

        string = re.sub("\t", "", string)

        string = remove_invalid_characters(string)

        # Use my create_work function to get a set of elements
        work: etree._Element = create_work(
            to_add=string, title=titleString, author=authorString, path=str(path)
        )

        # Add breakpoint here to test the create_work function's results
        worksProcessed.append(work)

    return worksProcessed


# Store the path to the file with the results here so its globally accessible
results_file: str = "./atticus-study-results.csv"


def open_results() -> etree._ElementTree:
    """
    TODO TEST!
    Returns the root element of the atticus-study-results.xml file"""
    etree.XMLParser(schema=etree.XMLSchema(file="./results-schema.xsd"))
    tree = etree.parse(results_file)
    return tree


###############################################33
class ResultsFailureError(Exception):
    """If one of the following functions in this section fails to execute, it
    will raise this error to signal that the work information
    didn't successfully get added to the results XML."""

    pass


def validate_result(element: etree._Element) -> bool:
    """
    TODO TEST!
    This is used in one of the following functions (create_work, create_plaintext, create_postagged, create_page)
    in order to make sure the result is schema compliant

    @param element: An element other than <root>"""
    # Create this so we can validate our results against the schema
    from copy import deepcopy

    local_template: etree._Element = deepcopy(xml_template)

    # If it's an element with a unique name like <work>, check if it's in the model
    tag = element.tag

    matching_desc = [x for x in local_template.iterdescendants() if x.tag == tag]

    # Otherwise, check the type
    try:
        e_type = element.get("type")
        if e_type is not None:
            matching_desc = [x for x in matching_desc if x.get("type") == e_type]
    except IndexError:
        pass

    try:
        matching_desc = matching_desc[0]
    except IndexError:
        print(etree.tostring(local_template, pretty_print=True))
        return False

    matching_desc.getparent().replace(
        old_element=matching_desc,
        new_element=element,
    )

    # raise an unhandled exception if it doesn't validate
    # print(etree.tostring(local_template, pretty_print=True))
    try:
        data_schema.assertValid(local_template)
        # Only returns True is the assertValid function doesn't raise an exception
        return True
    except etree.DocumentInvalid as e:
        save_output(etree.tostring(local_template))
        print(f"Issues with validation: {e.args}")
        return False


def create_work(
    to_add, title: str, author: str, path: str, pages=False
) -> etree._Element:
    """
    TODO TEST!
    This function returns a set of elements in the format defined in
    results-schema.xsd in this repository. It takes the cleaned text for
    a file, which is generated in the TEI_to_text function


    @param to_add       : Plaintext or tagged words, as pulled from the Perseus DL
    @param title        : The title of the work as given in the tei:titleStmt/tei:title
    @param author       : The author of the work as given in the tei:titleStmt/tei:author
    @param path         : The path which was used to find the original XML file ("**-lat*.xml")
    @param pages        : NEEDSDOC
    """

    content_type: str = ""

    # Check whether to_add was a string
    if type(to_add) == str:
        content_type = "plaintext"
    elif pages:
        content_type = "pages"

    # If it isn't a string, the content is postagged
    else:
        content_type = "postagged"

    path = str(path)
    path = path.replace("\\", "/")

    element = E.work(
        E.title(title),
        E.author(author),
        E.path(path),
        E.content(to_add, type=content_type),
        reviewed="UNREVIEWED",
        timestamp=datetime.datetime.now().isoformat(),
    )

    if validate_result(element):
        return element
    else:
        raise ResultsFailureError(
            f"Error! Element {etree.tostring(element)} could not be validated"
        )


def add_to_work(
    element_to_add: etree._Element, element_destination: etree._Element
) -> None:
    """
    Adds or replaces the contents of plaintext or pages.
    NOTE: This doesn't modify the original work in some cases.
    If the changes aren't propagating, use the add_work() function
    after this

    @param element_to_add      : A new <content> element
    @param element_destination : An element with the <work> tag from an element tree
    """
    # make sure it matches the parameter
    if element_destination.tag != "work":
        raise ResultsFailureError(
            "Error! Tried to add plaintext or postagged elements to an element without the tag 'work'"
        )
    if element_to_add.tag != "content":
        raise ResultsFailureError(
            "Error! Tried to add an element without the tag 'content' to a work"
        )
    # See whether we are replacing or adding. If this evaluates to true, there is already an element with the same tag and same attributes
    existing_elements: list[etree._Element] = [
        x
        for x in element_destination.iterdescendants()
        if (x.tag == element_to_add.tag) and (x.values() == element_to_add.values())
    ]

    if existing_elements:
        element_destination.replace(existing_elements[0], element_to_add)
    else:
        element_destination.append(element_to_add)

    if not validate_result(element_destination):
        raise ResultsFailureError(
            "Error! Element could not be added to destination. Recommend adding a breakpoint and debugging"
        )


def __work_exists__(path: str, data_file: etree._ElementTree):
    """
    TODO TEST!

    Passed tests for 3 works
    THIS INTERNAL FUNCTION IS FOR USE IN work_exists() ONLY!
    Checks if a work for a parsed file already exists based on the path. This is a helper function for work_exists(), which takes an element instead of a path and tells whether it exists. If successful, returns the Element that has the same path

    @param path      : The path used to find the original XML file in the create_work() function, in the format **.lat*.xml
    @param data_file : The results file where all the results end up. The recommended value is always the results of the open_results() function for consistency
    @return : either an etree._Element or None, depending on whether the work exists.
    """

    # Tested with a basic file in the interpreter, algorithm seems to work
    xpath_expr = f"/root/work/path[.='{path}']"
    sub_work = data_file.xpath(xpath_expr)
    try:
        sub_work = sub_work[0]
    except IndexError:
        return None
    return sub_work.getparent()


def work_exists(element: etree._Element, data_file: etree._ElementTree):
    """
    Checks whether a work element already has a previous version present. If successful, it returns the

    @param element   : A <work> element to be checked
    @param data_file : The results file where all the results end up. The recommended value is always the results of the open_results() function for consistency
    """

    # Make sure the element is a <work> element
    if element.tag == "work":
        # Set the annotation to string so we can catch any errors here
        path: str = element.xpath("./path/text()")[
            0
        ]  # added the [0] because it returns a list of 1
        existing_work = __work_exists__(path, data_file)

        if existing_work is not None:
            return existing_work
        else:
            return None
    else:
        raise ResultsFailureError(
            f"Error! The element {etree.tostring(element)} is not a valid <work> element"
        )


def element_in_tree():  # -> bool:
    """
    TODO"""
    pass


def remove_duplicates(data: etree._Element):
    """
    TODO
    This function removes works when more than one have the same author/title combo.
    Priority is given to the newest element.

    @param data: the <root> element of a data to be exported"""


def add_work(element: etree._Element, data_file: etree._ElementTree) -> None:
    """
    TODO TEST!
    Adds the work to the data_file. If the work already exists, replace it

    @param element   : A <work> element to be output to the data file
    @param data_file : The <root> node of the ElementTree from the data file returned from open_results()
    """

    # Don't need to check whether the element passed to this function is actually a <work> element, because work_exists will raise an error if it isn't

    existing_work = work_exists(element, data_file)
    if existing_work is not None:
        parent: etree._Element = existing_work.getparent()
        parent.replace(existing_work, element)
    else:
        root = data_file.getroot()
        root.append(element)


"""
def automatic_validation() -> None:
    
    Docstring for automatic_validation

    This function goes through the results file specified in open_results() and does tests to validate each work.

    Tests:
    NEEDSDOC

    data_file = open_results()

    # Size of the sampled strings minus 1
    test_size = 4

    schema: etree.XMLSchema = data_schema

    schema_validated: bool = schema.validate(data_file.getroottree())

    if schema_validated:
        # Works are direct children of the root, therefore we're able to just loop through the Element as an iterable
        for work in data_file:
            path = work.find("path").text
            save_output(path, "a")
            with open(path, "r", encoding="utf-8") as file:
                # Do our tests here.
                content = work.xpath('content[@type="plaintext"]')
                content = content[0]
                content = content.text

                tokenized = content.split(" ")

                source: str = str(file.read())
                source = re.sub("\t", "", source)

                source = remove_invalid_characters(source)

                save_output(
                    str(work.xpath("/path/text()")) + "\n" + ("*" * 25) + "\n\n", "a"
                )

                for i in range(0, 99):
                    index = random.randrange(0, len(tokenized))
                    final_string = ""
                    try:
                        final_string = " ".join(tokenized[index : (index + 4)])
                    except IndexError:
                        final_string = " ".join(tokenized[index:])
                    if not final_string in source:
                        save_output(final_string, "a")
    else:
        save_output("Error! Could not validate results file\n\n", "a")
"""


def automatic_validation():

    path: str = str(choice(get_paths()))
    with open(path, "r", encoding="utf-8") as file:
        text = __get_body(path)
        tokenized = text.split(" ")

        source: str = str(file.read())
        source = re.sub("\t", "", source)

        source = remove_invalid_characters(source)

        save_output(path + "\n" + ("*" * 25) + "\n\n", "a")

        for i in range(0, 99):
            index = random.randrange(0, len(tokenized))
            final_string = ""
            try:
                final_string = " ".join(tokenized[index : (index + 4)])
            except IndexError:
                final_string = " ".join(tokenized[index:])
            if not final_string in source:
                save_output(final_string, "a")


# THIS FUNCTION MAY GET NIXED!
def test_text(plaintext: str, validate_against: str) -> None:
    """
    Docstring for test_text

    NEEDSDOC
    :param plaintext: Description
    :type plaintext: str
    :param validate_against: Description
    :type validate_against: str


    """

    # This is the stuff removed from the final result:
    """
    # Remove numeric
    text = re.sub("[0-9]", "", text)

    # Look for hyphens followed by a line break and zero or
    # more spaces/line breaks. After identifying these, all matches.
    text = re.sub("- *\n[\n ]*", "", text)

    # Remove gaps between words bigger than a space
    text = re.sub("[\n ]+", " ", text)
    """

    # Number of times to check
    trials = 100

    # Length to check

    for i in range(0, trials):
        pass

    # validate_against = re.sub("\t", "", validate_against)

    # validate_against = remove_invalid_characters(validate_against)

    pass


#########################################################


def identify_duplicates_perseus(paths: list = get_paths()):  # -> list:
    """
    Docstring for identify_duplicates_perseus

    :param paths: A list of paths from the get_paths() function
    :type paths: list
    :return: Description
    :rtype: list[Any]
    """

    """
    
    If more than one path has the same directory, pick the first"""

    pass


def get_paths_no_file() -> list[str]:
    ret_value = []
    for p in get_paths():
        sP = str(p)
        sP = sP.split("\\")
        sP = sP[0:-1]
        ret_value.append("\\".join(sP))
    return ret_value


# QUESTIONS TO ANSWER:
# How to save the results?
#   As XML?
#   As a CSV?
#   As CONLLU?
#   XML might be ideal, because I needed a structured way to look at the data (divided into texts, which are further divided into words)
#   TEI XML would be

##############CLASSICAL LANGUAGES TOOLKIT#########################

from cltk.nlp import NLP
import cltk.core.data_types as types
import cltk.morphosyntax.conll as conll


def process_text(text: str, nlp: NLP) -> types.Doc:
    f"""
    Docstring for process_text
    Processes the Perseus DL texts and the Letters to Atticus with the CLTK
    
    :param text: The plaintext for a work, as retrieved from the <content type="plaintext"/> element in the {results_file} file
    :type text: str 
    :param nlp: An NLP for Latin from the CLTK. Added this so it didn't have to create a new parser every time. In theory, could also work with an older version of CLTK before AI backends, although the return type annotation would no longer be valid (I don't believe the 'Doc' datatype is in cltk.core.data_types in the original).
    :type nlp: cltk.nlp.NLP
    :return: Description
    :rtype: NLP from the CLTK for a single work
    """
    doc = nlp.analyze(text)
    return doc


def doc_to_element(
    tagged: types.Doc, title: str, author: str, path: str
) -> etree._Element:
    """
    Docstring for doc_to_element
    This function takes the sentence and word classes from an NLP and placed them in
    <sentence> and <word> elements, with the relevant information for each word
    being placed in attributes.
    SUCCESSFULLY TESTED

    :param tagged: An NLP which is the parsed form of the provided work
    :type tagged: NLP
    :param title: The title of the work
    :type title: str
    :param path: The path to the original Perseus DL TEI XML file
    :type path: str
    :return: Returns an element tree of the type <content type="postagged"/>, containing sentence and word nodes with the information
    :rtype: etree._Element
    """
    content = etree.Element("content", type="postagged")

    # Get all the sentences
    sents = tagged.sentences

    for s in sents:
        sent = etree.Element("sentence")
        # Add an attribute with the sentence number
        n_sent = sents.index(s)
        sent.set("n", str(n_sent))
        for word in s.words:
            s_form = word.string

            w_elem = etree.Element("word")

            # Add the title and path
            w_elem.append(E.title(title))
            w_elem.append(E.author(author))
            w_elem.append(E.path(path))

            # Add the word form
            form = etree.Element("form")
            form.text = s_form

            w_elem.append(form)

            for item in word.upos:
                if item[0] in ["name", "open_class"]:
                    continue
                # w_elem.set(str(item[0]), str(item[1])) NO LONGER USING ATTRIBUTES, BUT ELEMENTS

                # Add a child element for each POS feature.
                # The feature name is the element name, and the value is the element text
                child = etree.Element(str(item[0]))
                child.text = str(item[1])
                w_elem.append(child)

            try:
                for item in word.features.features:
                    # Add a child element for each feature.
                    # The feature name is the element name, and the value is the element text
                    if item.key in ["Foreign", "Poss", "Reflex", "Abbr"]:
                        continue
                    child = etree.Element(str(item.key))
                    child.text = str(item.value)
                    w_elem.append(child)
            # Some words don't have features if indeclinable.
            # If so, it'll throw an attribute error when we try to access features. In that case, just skip
            except AttributeError:
                pass

            sent.append(w_elem)
        content.append(sent)
    return content


def postag_validation(tagged: NLP) -> None:
    """
    Docstring for postag_validation
    Throw an error if the postagged text doesn't meet standards.
    Ideally, print offending token(s) to console.

    :param tagged: A cltk.NLP with the parsed text
    :type tagged: NLP
    """
    pass


def process_results(skip_finished=False, path="") -> None:
    f"""
    Docstring for process_results
    This function takes the results file, {results_file}, and adds a postagged content element for each one

    :param skip_finished: If true, the algorithm only processes texts which don't already have a <content type="postagged"/> element. Default behavior is to re-postag everything, so it's set to False.
    :type skip_finished: bool
    """

    # Get every work in the results page
    results_xml: etree._ElementTree = open_results()

    nlp = NLP("lati1261", backend="stanza")

    if path != "":
        works = results_xml.xpath(f"/root/work[./path = '{path}']")
    else:
        works = results_xml.xpath("/root/work")

    for work in works:
        content = work.find("./content[@type='plaintext']")
        # DEBUG: GET RID OF THIS!!!!
        path = work.find("./path")

        print(f"process_results: Now postagging {str(path.text)}")

        # If the skip_finished bool is True, we want to skip works where there already is a postagged set.
        if skip_finished and (work.find("./content[@type='postagged']") is not None):
            continue

        doc: types.Doc

        # Get the CLTK Doc. If there is no content, continue to the next iteration of the loop
        try:
            doc = process_text(content.text, nlp)
        except AttributeError:
            continue

        # Get the title and path for each work to save to each word.
        # This is technically redundant, but makes importing into R easier
        e_title = work.find("./title")
        try:
            e_title = str(e_title.text)
        except AttributeError:
            e_title = ""
        e_author = work.find("./author")
        try:
            e_author = str(e_author.text)
        except AttributeError:
            e_author = ""
        e_path = work.find("./path")
        try:
            e_path = str(e_path.text)
        except AttributeError:
            e_path = ""

        # Put the text in XML format
        postagged: etree._Element = doc_to_element(
            doc, title=e_title, author=e_author, path=e_path
        )

        # save_output("Iteration: " + etree.tostring(results_xml).decode("utf-8") + "\n" * 8)
        add_to_work(postagged, work)
        # save_output("Work: " + etree.tostring(work).decode("utf-8") + "\n" * 8)
        add_work(work, results_xml)
        write_results(results_xml)

    # write_results(results_xml)


def __get_paths(path):  # -> list[str]:
    """
    This is a helper function to csv_postag which processes the path argument.
    If an argument isn't specified, we need to get the full list.

    :return: NEEDSDOC
    :rtype: list[str]
    """

    # Check whether the path argument was given and whether it's a valid value
    # If the pathArg is rand, that means we select a random path.
    # If the pathArg is the default value, we already got all the paths we need with the get_paths()
    # If we passed a list of paths to pathArg, we replace paths with that list
    if path not in ("", "rand"):
        return [path]

    paths: list[str] = [str(x) for x in get_paths()]

    if path == "":
        return paths
    elif isinstance(path, list):
        return path


import csv
import shutil


def __get_body(path: str) -> str:
    """
    Helper function for automatic_validation (plan to also incorporate this into
    csv_postag()). This returns the body text for a TEI file

    :param path: A path to a TEI XML file from the Perseus DL
    :type path: str
    """
    parser: etree.XMLParser = etree.XMLParser(resolve_entities=False)
    tree: etree.ElementTree = etree.parse(path, parser)  # Use path 22 for debugging

    # Get the root of the tree. This variable will eventually hold the tei:body element
    body: etree._Element = tree.getroot()

    authority_dict = get_title_auth_body(body)

    body = authority_dict["body"]

    if len(body):
        body = body[0]

    # Now we have the <body> element, let's get the text######################3

    # Add the text for each element, using the get_text() function
    string: str = ""
    for element in body.iter():
        string += get_text(element)

    string = re.sub("\t", "", string)

    s_final_body = remove_invalid_characters(string)
    return s_final_body


def csv_postag(path: str = "", skip_finished=True) -> None:
    """
    Docstring for csv_postag NEEDSDOC

    :param path: An optional path of the file to write manually
    :type path: str
    :param skip_finished: NEEDSDOC
    :type skip_finished: bool
    """
    paths: list = __get_paths(path)

    nlp = NLP("lati1261", backend="stanza")

    # If we want to keep a line, we place it in the
    with open(
        results_file, "r", encoding="utf-8", errors="replace", newline=""
    ) as f_read:
        with open(
            "./temp.csv", "w", encoding="utf-8", errors="replace", newline=""
        ) as f_write:
            # If we're skipping already finished ones, lets remove paths
            # that we're not going to parse
            if skip_finished:
                try:
                    s = f_read.read()
                except UnicodeDecodeError as e:
                    print(e.reason)
                    raise KeyboardInterrupt()

                for p in paths:
                    if s.find(p) > -1:
                        paths.remove(p)
            else:
                wr = csv.writer(f_write)
                for l in csv.reader(f_read):
                    if l[2] not in paths:
                        wr.writerow(l)
        if not skip_finished:
            shutil.copyfile("temp.csv", results_file)
            os.remove("./temp.csv")

    # Get the csv.writer
    with open(results_file, "a", encoding="utf-8", errors="replace", newline="") as f:
        writer = csv.writer(f, escapechar="#")

        l_paths = len(paths)
        for p in paths:
            i_paths = paths.index(p)

            print(f"Completion: {i_paths}/{l_paths}")
            parser: etree.XMLParser = etree.XMLParser(resolve_entities=False)
            tree: etree.ElementTree = etree.parse(
                p, parser
            )  # Use path 22 for debugging

            # Get the root of the tree. This variable will eventually hold the tei:body element
            body: etree._Element = tree.getroot()

            authority_dict = get_title_auth_body(body)

            body = authority_dict["body"]
            titleString = authority_dict["title"]
            authorString = authority_dict["author"]

            # Remember, when there are potentially Greek characters, we need encoding set to utf-8.
            # This debug file will store the results before the final version of the program

            """debug: io.TextIOWrapper = open(
                "C:/Users/T470s/Documents/GitHub/cltk-2025-atticus/perseus-debug.txt",
                "w",
                encoding="utf-8",
            )
            debug.write(str(p))"""

            if len(body):
                body = body[0]

            # Now we have the <body> element, let's get the text######################3

            # Add the text for each element, using the get_text() function
            string: str = ""
            for element in body.iter():
                string += get_text(element)

            string = re.sub("\t", "", string)

            s_final_body = remove_invalid_characters(string)

            # now that we have the TEI XML, let's parse the body text
            doc = process_text(s_final_body, nlp)

            for word in doc.words:
                # Skip most punctuation that doesn't break sentences
                if word.upos.tag != "PUNCT" or word.string in [".", "!", "?"]:
                    s_form = word.string

                    s_lemma = word.lemma

                    # Get the tag
                    tag = word.upos.tag

                    # Only get the features we're interested in
                    features = {}
                    f_set = [
                        "Aspect",
                        "Mood",
                        "Number",
                        "Person",
                        "Tense",
                        "VerbForm",
                        "Voice",
                        "Case",
                        "PronType",
                        "Gender",
                        "Polarity",
                        "Degree",
                        "NumType",
                    ]
                    try:
                        w_features = word.features.features
                        for key in f_set:
                            try:
                                features[key] = __proc_feature(
                                    [val.value for val in w_features if val.key == key]
                                )
                            # The next two lines are superfluous, it seems, as we never get a KeyError, but I'll leave them for now
                            except KeyError:
                                features[key] = ""
                    # Some words don't have features, so Python will throw an Attribute Error.
                    except AttributeError:
                        for key in f_set:
                            features[key] = ""

                    # Start putting together the line to write
                    metadata = [
                        titleString,
                        authorString,
                        p,
                        s_form,
                        s_lemma,
                        tag,
                    ]  # NOTE: Not only metadata, but also includes the word and the tag
                    to_write = metadata + [
                        features[x] for x in f_set
                    ]  # This didn't need to be a dictionary, but it helps to know that I will always do this in the same order

                    writer.writerow(to_write)


def __proc_feature(feature):
    if not feature:
        return ""
    else:
        return str(feature[0])


def save_abridged_results():
    f"""
    This function opens {results_file} and puts only the relevant postagged results into a separate file
    """

    data_file: etree._Element = open_results()

    # Get the root we will make the toplevel of the final document
    root: etree._Element = etree.Element("root")

    for e in data_file.iter(tag="word"):
        root.append(e)

    rootTree = root.getroottree()

    rootTree.write("./postagged_only.xml", encoding="utf-8")


def update_info(mode: str, path: str = ""):
    f"""
    This function goes through each <work> in {results_file}, replacing the title along the way

    :param mode: Either "title" or "author", depending on what needs replacing
    :type mode: str
    :param path: Optional, mainly used for debugging. Allows picking a single work, especially a troublesome one.
    :type path: str
    """

    results_xml = open_results()

    if path:
        works = results_xml.xpath(f"/root/work[./path = {path}]")
    else:
        works = results_xml.findall(".//work")

    for work in works:
        e_path = work.find("path")
        tei = etree.parse(e_path.text)

        # Get the root of the tree and pass it to the function for getting the title
        authority_dict = get_title_auth_body(tree=tei.getroot())

        e = E.title(authority_dict[mode])
        # print(etree.tostring(e_title).decode("utf-8"))

        # title or author
        titles = [t for t in work.findall(f".//{mode}")]
        for t in range(0, len(titles)):
            e_title = deepcopy(e)
            parent = titles[t].getparent()
            parent.replace(titles[t], e_title)
            add_work(work, results_xml)
            pass
            # debug_work = etree.tostring(work, pretty_print=True).decode("utf-8")
            # debug_results = etree.tostring(results_xml, pretty_print=True).decode("utf-8")
            # print(etree.tostring(t).decode("utf-8"))

        # print(etree.tostring(work).decode("utf-8"))
        # debug_work = etree.tostring(work, pretty_print=True).decode("utf-8")
        # debug_results = etree.tostring(results_xml, pretty_print=True).decode("utf-8")

        # save_output(etree.tostring(results_xml, pretty_print=True).decode("utf-8"))
    write_results(results_xml)


##################################################################

if __name__ == "__main__":
    # print(f"Current file path: {Path(__file__).parents[0]}\n")
    # Debug

    # print(f"Printing the xml template:\n{prettyprint(xml_template)}")

    # save_output(etree.tostring(process_pages_att(), pretty_print=True).decode("utf-8"))

    # print(etree.tostring(content))

    # perseus_to_file(pathArg="", index=-1)

    # save_pages_att(process_pages_att())

    # process_results(skip_finished=False)

    # work = "C:/Users/T470s/Documents/GitHub/canonical-latinLit/data/phi0474/phi003/phi0474.phi003.perseus-lat2.xml"
    # perseus_to_file(pathArg=[work], index=-1)

    p = "C:/Users/T470s/Documents/GitHub/canonical-latinLit/data/phi0474/phi002/phi0474.phi002.perseus-lat2.xml"
    p2 = get_paths()[22]
    p3 = get_paths()[23]
    print(str(p3))

    csv_postag(path="", skip_finished=True)

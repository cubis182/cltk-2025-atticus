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
import datetime

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


def save_output(text: str, method: str = "w") -> None:
    """
    Saves text to a file called 'letters-tests.txt'.
    The directory is specified in the DEBUG_DIR at
    the top of the file."""
    with open((DEBUG_DIR + "./letters-tests.txt"), method, encoding="utf-8") as output:
        output.write(datetime.datetime.now().isoformat() + "\n")
        output.write(text + "\n")
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


from lxml import etree  # type: ignore
from lxml.builder import E
from pathlib import Path
from random import choice
import io

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

    NEEDSDOC
    @param pathArg : An optional string or list of strings which gives the specific path(s) you want to parse. Type "rand" if you want a random one
    @param index   : An optional integer index of the location in the file list of the path. Can also be a sequence of integers
    """

    # File the results will go in.
    data_file: etree._Element = open_results()

    list_of_works = TEI_to_text(pathArg=pathArg, index=index)

    for work in list_of_works:
        add_work(work, data_file)

    # Finally, add the updated results
    data_file.getroottree().write(results_file, encoding="utf-8")


def get_paths() -> list[Path]:
    """
    Returns a list of paths to all Perseus DL Latin texts"""

    # path to PerseusDL
    dir: Path = Path("C:/Users/T470s/Documents/GitHub/canonical-latinLit/data/")

    # paths to all the files in the corpus, identified by -lat and the .xml extension.
    return list(dir.glob("**/**-lat*.xml"))


def get_title_auth_body(tree: etree._Element) -> dict:
    # We need to make sure it's a real TEI file with the xml namespace.
    # Some files in the PerseusDL use TEI without the namespace

    tei: dict = {"tei": "http://www.tei-c.org/ns/1.0"}

    # First, assume no namespace
    expression: str = "//body"

    # XPath expression for the title
    title: str = "/teiHeader/fileDesc/titleStmt/title/text()"
    titleString: str = ""

    # XPath expression for the author's name
    author: str = "/teiHeader/fileDesc/titleStmt/author/text()"
    authorString: str = ""

    # However, if there is a namespace with the TEI URI (which is given in the 'tei' variable above), we need a tei namespace declared
    nsmap: list = list(tree.nsmap.values())
    is_TEI: bool = tei["tei"] == nsmap[0]

    body = __run_xpath(expression, is_TEI, tree, tei)

    # We need to test a few things in case the title isn't in the right spot
    titleEl = __run_xpath(title, is_TEI, tree, tei)

    if not titleEl:
        titleEl = __run_xpath("//biblStruct/monogr/title/text()", is_TEI, tree, tei)

    authorEl = __run_xpath(author, is_TEI, tree, tei)

    if not authorEl:
        authorEl = __run_xpath("//biblStruct//author/text()", is_TEI, tree, tei)

    # If we still don't have a valid author or title node, we give up
    if titleEl:
        titleString = titleEl[0]
    else:
        titleString = ""

    if authorEl:
        authorString = authorEl[0]
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
        elem = tree.xpath(expr, namespaces=tei)
        return elem
    else:
        return tree.xpath(expr)


def TEI_to_text(pathArg="", index=-1) -> list[etree._Element]:
    """
    This function returns a plaintext version of the TEI XML files in the
    Perseus Digital Library. The function currently assumes the path to the
    Perseus DL is the one on my system:
    C:/Users/T470s/Documents/GitHub/cltk-2025-atticus/perseus-debug.txt.
    The function can work with no namespace or TEI.

    @param pathArg : An optional string or list of strings which gives the specific path(s) you want to parse. Type "rand" if you want a random one
    @param index   : An optional integer index of the location in the file list of the path. Can also be a sequence of integers
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

        # Remember, when there are potentially Greek characters, we need encoding set to UTF-8.
        # This debug file will store the results before the final version of the program
        debug: io.TextIOWrapper = open(
            "C:/Users/T470s/Documents/GitHub/cltk-2025-atticus/perseus-debug.txt",
            "w",
            encoding="utf-8",
        )
        debug.write(path.__str__())

        if len(body):
            body = body[0]

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
results_file: str = "./atticus-study-results.xml"


def open_results() -> etree._Element:
    """
    TODO TEST!
    Returns the root element of the atticus-study-results.xml file"""
    tree = etree.parse(results_file)
    return tree.getroot()


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

    local_template: etree._Element = xml_template

    # If it's an element with a unique name like <work>, check if it's in the model
    matching_desc = [
        x for x in local_template.iterdescendants() if x.tag == element.tag
    ]

    # Otherwise, check the type
    try:
        element.get("type")
        matching_desc = [
            x for x in matching_desc if x.get("type") == element.get("type")
        ]
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
        print(f"Issues with validation: {e.args}")
        return False


def create_work(to_add, title: str, author: str, path: str) -> etree._Element:
    """
    TODO TEST!
    This function returns a set of elements in the format defined in
    results-schema.xsd in this repository. It takes the cleaned text for
    a file, which is generated in the TEI_to_text function


    @param to_add       : Plaintext or tagged words, as pulled from the Perseus DL
    @param title        : The title of the work as given in the tei:titleStmt/tei:title
    @param author       : The author of the work as given in the tei:titleStmt/tei:author
    @param path         : The path which was used to find the original XML file ("**-lat*.xml")
    """

    content_type: str = ""

    # Check whether to_add was a string
    if type(to_add) == str:
        content_type = "plaintext"

    # If it isn't a string, the content is postagged
    else:
        content_type = "postagged"

    element = E.work(
        E.title(title),
        E.author(author),
        E.path(str(path)),
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
    TODO TEST
    Adds or replaces the contents of plaintext or pages

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


def create_page(text: str, data_file: etree._Element) -> etree._Element:
    """
    TODO TEST
    Packs the results of the clean_text() function to a <page> element.
    TODO NEEDS TO BE USED IN THE CLEAN_TEXT() FUNCTION TO SAVE DATA!!!!!

    @param text     : The text from the page to be added
    @param data_file: The file (currently atticus-study-results.xml) where the results will go
    """

    # Get list of all current page elements
    id_final = 1

    page_ids = data_file.xpath(".//page/@id")

    # Get the biggest existing id, add 1, and then we have our ID
    if page_ids:
        id = (max([int(item) for item in page_ids])) + 1

    return E.page(text, id=id_final)


def __work_exists__(
    path: str, data_file: etree._Element = open_results()
) -> etree._Element:
    """
    TODO TEST!
    Checks if a work for a parsed file already exists based on the path. This is a helper function for work_exists(), which takes an element instead of a path and tells whether it exists. If successful, returns the Element that has the same path

    @param path      : The path used to find the original XML file in the create_work() function, in the format **.lat*.xml
    @param data_file : The results file where all the results end up. The recommended value is always the results of the open_results() function for consistency
    """

    # Tested with a basic file in the interpreter, algorithm seems to work
    xpath_expr = f"//work/path[text()='{path}']"
    sub_work = data_file.xpath(xpath_expr)
    sub_work = sub_work[0]
    return sub_work.getparent()


def work_exists(element: etree._Element, data_file: etree._Element = open_results()):
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


def add_work(element: etree._Element, data_file: etree._Element) -> None:
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
        data_file.append(element)


def automatic_validation() -> None:
    """
    Docstring for automatic_validation

    This function goes through the results file specified in open_results() and does tests to validate each work.

    Tests:
    NEEDSDOC"""

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


def identify_duplicates_perseus(paths: list = get_paths()) -> list:
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

if __name__ == "__main__":
    # print(f"Current file path: {Path(__file__).parents[0]}\n")
    # Debug
    # print(f"Printing the xml template:\n{prettyprint(xml_template)}")

    # perseus_to_file(pathArg="", index=[0, 22])

    """
    data_file = open_results()

    schema: etree.XMLSchema = data_schema

    schema_validated: bool = schema.assertValid(data_file.getroottree())

    automatic_validation()
    """

    my_list = get_paths_no_file()
    indices = [index for index, value in enumerate(my_list) if my_list.count(value) > 1]

    for i in indices:
        print(my_list[i])

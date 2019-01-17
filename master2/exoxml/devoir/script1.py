"""
XML Glozz project
------------------------------------------------------------

Discussion files extracted from wikipedia are stored in the TEIP5 XML format.
This project contains:
    + a simple Log class to log all output (in log.py)
    + a TEIP5Reader to transform TEIP5 XML file to a TEIP5Document
    + a TEIP5Document an object representing the discussion
    + a TEIP5Document is composed of TEIP5Post (serialised as div in the XML)
    + a TEIP5Post is composed of sub post or paragraphs (simple string).
    + a GlozzWriter writing the discussion data into the Glozz format.
        - It writes the ac file (one line corpus).
        - It writes the aa file (basic annotations for title, paragraph, etc.).

Damien Gouteux - 2019 - CC 3.0 BY-SA-NC
"""

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

# External library
from lxml import etree

# Project library
from log import Log

#-------------------------------------------------------------------------------
# TEIP5 objet model and reader
#-------------------------------------------------------------------------------

class TEIP5Document:
    """A lightweight representation of an TEI-P5 document.
       Warning:
       This is not a proper deserialization of TEI-P5, we
       deserialize only the needed parts for our need."""
    
    def __init__(self):
        self.title = None
        self.date = None
        self.source = None
        self.author = None
        self.sourcefile = None
        self.lang = None
        self.parts = []

    def info(self):
        print(self.title)
        if self.title is not None:
            print('-' * len(self.title))
        print('Date  ', self.date)
        print('Source', self.source)
        print('Author', self.author)
        print('File  ', self.sourcefile)
        print('Lang  ', self.lang)

    def add_part(self, p):
        self.parts.append(p)


class TEIP5Element:
    pass


class TEIP5Part(TEIP5Element):
    """A part of a TEIP5Document (corresponding to a div)
       Warning:
       This is not a proper deserialization of TEI-P5, we
       deserialize only the needed parts for our need."""

    def __init__(self, head):
        self.head = head
        self.elements = [] # can be Part or Post

    def add(self, element):
        self.elements.append(element)


class TEIP5Post(TEIP5Element):
    """A post in a part of a TEIP5Document (corresponding to a post)
       Warning:
       This is not a proper deserialization of TEI-P5, we
       deserialize only the needed parts for our need."""

    def __init__(self, when, who, signature):
        self.when = when
        self.who = who
        self.signature = signature
        self.elements = [] # can be only strings

    def add(self, element):
        if not isinstance(element, str) and not isinstance(element, list) and not isinstance(element, tuple):
            Log.error("Can't add a non string object to a post : " + str(type(element)))
        self.elements.append(element)


class TEIP5Reader:
    """A loader for XML TEI-P5 encoded file
       Format of the XML file:
       TEI
           teiHeader
           text
               front
                   titlePage
                       docTitle
               body
                   div*
                       head
                       post*
                           p*
                       div*
    """

    @staticmethod
    def make_div(div_xml, debug):
        if debug: print('div---')
        head = div_xml.find('head').text
        div_obj = TEIP5Part(head)
        for element in list(div_xml): # iter on all children of first level
            if element.tag == 'head':
                pass
            elif element.tag == 'post':
                when = element.attrib['when']
                who = element.attrib['who']
                s = element.find('.//signed/ref/name')
                signature = s.text if s is not None else None
                post = TEIP5Post(when, who, signature)
                for p in list(element):
                    if p.tag == 'p':
                        txt = p.text
                        if txt is not None:
                            txt = txt.strip()
                            if len(txt) > 0:
                                post.add(txt)
                                if debug: print(txt[0:10])
                    elif p.tag == 'list':
                        lst = []
                        for item in list(p):
                            lst.append(item.text)
                        post.add(lst)
                # signature
                if s is not None:
                    post.add((s.text, 'signature'))
                elif post.who is not None:
                    post.add((post.who, 'signature'))
                div_obj.add(post)
            elif element.tag == 'div':
                div_obj.add(TEIP5Reader.make_div(element, debug))
            else:
                Log.error('Unkwon tag ' + element.tag + ' found in a div.')
        return div_obj


    @staticmethod
    def load_from_file(filepath : str, debug : bool = False):
        try:
            file = open(filepath, mode='r', encoding='utf8')
        except (FileNotFoundError, IOError) as e:
            Log.error(f'On opening {filepath} : ' + str(e))
        try:
            tree = etree.parse(file)
        except RuntimeError as e:
            Log.error(f'On decoding {filepath} : ' + str(e))
        else:
            file.close()
        root = tree.getroot()
        tei_obj = TEIP5Document()
        # Header
        tei_xml = root.find('teiHeader')
        tei_obj.title = tei_xml.find('.//analytic/title').text
        tei_obj.date = tei_xml.find('.//imprint/date').text
        tei_obj.source = tei_xml.find('.//pubPlace').text
        tei_obj.author = tei_xml.find('.//analytic/author').text
        tei_obj.sourcefile = tei_xml.find('.//titleStmt/title').text
        tei_obj.lang = tei_xml.find('.//language').attrib['ident']
        # Content
        body = root.find('text/body')
        for div_xml in body.iterfind('div'):
            tei_obj.add_part(TEIP5Reader.make_div(div_xml, debug))
        return tei_obj


#-------------------------------------------------------------------------------
# Glozz writer
#-------------------------------------------------------------------------------

class GlozzWriter:
    """Write the aa and am files."""

    #MAX_NAME = 30
    
    @staticmethod
    def write_annotation(anno_file, start, end, typ):
        """ Basic Glozz annotations:
            title
            numberedList*
                listItem
            list
                listItem
            paragraph
            sectionTitle
            *In this implementation, numberedList element are not handled.
        """
        anno_file.write('<unit id="anonymous_0">\n')
        anno_file.write('\t<metadata>\n')
        anno_file.write('\t\t<author>anonymous</author>\n')
        anno_file.write('\t\t<creation-date>0</creation-date>\n')
        anno_file.write('\t</metadata>\n')
        anno_file.write('\t<characterisation>\n')
        anno_file.write('\t\t<type>' + typ + '</type>\n')
        anno_file.write('\t\t<featureSet/>\n')
        anno_file.write('\t</characterisation>\n')
        anno_file.write('\t<positioning>\n')
        anno_file.write('\t\t<start>\n')
        anno_file.write('\t\t\t<singlePosition index="' + str(start) + '"/>\n')
        anno_file.write('\t\t</start>\n')
        anno_file.write('\t\t<end>\n')
        anno_file.write('\t\t\t<singlePosition index="' + str(end) + '"/>\n')
        anno_file.write('\t\t</end>\n')
        anno_file.write('\t</positioning>\n')
        anno_file.write('</unit>\n')

    @staticmethod
    def write_space(corpus_file, anno_file, space, icount):
        old = icount
        icount += len(space)
        GlozzWriter.write_annotation(anno_file, old, icount, 'subSectionTitle')
        corpus_file.write(space)
        return icount
    
    @staticmethod
    def write_part(corpus_file, anno_file, part, icount, level=0, line=False):
        "Write a part or a post"
        if line: icount = GlozzWriter.write_space(corpus_file, anno_file, " " * (level*40) + "=" * (80 - level*40), icount)
        head = part.head if part.head is not None and len(part.head) > 0 else '(Untitled)'
        head = " " * (level*40) + head
        corpus_file.write(head)
        old = icount
        icount += len(head)
        GlozzWriter.write_annotation(anno_file, old, icount, 'sectionTitle')
        for post in part.elements:
            if isinstance(post, TEIP5Part):
                icount = GlozzWriter.write_part(corpus_file, anno_file, post, icount, level + 1, line)
            elif isinstance(post, TEIP5Post):
                for par in post.elements:
                    if isinstance(par, str):
                        par = par.replace('\t', '')
                        par = par.replace('\n', '')
                        par = par.strip()
                        if len(par) == 0:
                            return icount
                        old = icount
                        icount += len(par)
                        #if count < len(post.elements) - 1 or len(par) > GlozzWriter.MAX_NAME:
                        GlozzWriter.write_annotation(anno_file, old, icount, 'paragraph')
                        corpus_file.write(par)
                    elif isinstance(par, tuple):
                        old = icount
                        icount += len(par[0])
                        GlozzWriter.write_annotation(anno_file, old, icount, 'paragraph')
                        GlozzWriter.write_annotation(anno_file, old, icount, 'bold')
                        GlozzWriter.write_annotation(anno_file, old, icount, 'Signature')
                        corpus_file.write(par[0])
                    elif isinstance(par, list):
                        anno = []
                        for elem in par:
                            old = icount
                            icount += len(elem)
                            corpus_file.write(elem)
                            anno.append((old, icount))
                        GlozzWriter.write_annotation(anno_file, anno[0][0], anno[-1][1], 'list')
                        for elem in anno:
                            GlozzWriter.write_annotation(anno_file, elem[0], elem[1], 'listItem')
                if line: icount = GlozzWriter.write_space(corpus_file, anno_file, " " * (level*40) + "-" * (80 - level*40), icount)
        if line: icount = GlozzWriter.write_space(corpus_file, anno_file, " " * (level*40) + "=" * (80 - level*40), icount)
        return icount
    
    @staticmethod
    def write_from_teip5(doc):
        # Preparing annotation file (.aa)
        anno_file = open(doc.sourcefile.replace('.xml', '.aa'), mode='w', encoding='utf8')
        anno_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        anno_file.write('<annotations>\n')
        # Writing corpus (.ac)
        corpus_file = open(doc.sourcefile.replace('.xml', '.ac'), mode='w', encoding='utf8')
        corpus_file.write(doc.title)
        icount = len(doc.title)
        GlozzWriter.write_annotation(anno_file, 0, icount, 'title')
        for part in doc.parts:
            icount = GlozzWriter.write_part(corpus_file, anno_file, part, icount, level=0, line=False)
        anno_file.write('</annotations>\n')
        corpus_file.close()


#-------------------------------------------------------------------------------
# Main & tool function
#-------------------------------------------------------------------------------

def translate(filename, debug):
    Log.info('Translating: ' + filename)
    
    # reading discussion content
    tei = TEIP5Reader.load_from_file(filename, debug=debug)
    
    # writing Glozz
    GlozzWriter.write_from_teip5(tei)

if __name__ == '__main__':
    Log.start()
    translate('15075.xml', False)   # Nietzsche
    translate('333612.xml', False)  # Race (le + gros)
    translate('207754.xml', False)  # Son musical, tout petit, do not use
    translate('124179.xml', False)  # Tchernobyl (plutôt gros)
    translate('405394.xml', False)  # Françafrique
    translate('672388.xml', False)
    translate('1350243.xml', False)
    translate('1352965.xml', False)
    Log.end()
    

#
# This file handles all the building of the corpus.
# 339687 titres
#
# It requires :
#   recodage-josette.tsv
#   data\total-articles-HAL.tsv => Title metadata
#   data\output_tal_01.txt      => TAL data
#   data\output_tal_02.txt      => TAL data
#   data\output_tal_03.txt      => TAL data
#   data\output_tal_04.txt      => TAL data
#   data\output_tal_05.txt      => TAL data
#   data\output_tal_06.txt      => TAL data
#
# It produces :
#   corpus of titles following the datamodel (in memory)
#   unknown_lemma.txt           => list of all the unknown lemma
#
# Summary :
#   1. Imports
#   2. Handling of simplification of Domains
#   3. Data model for Words and Titles
#   4. Read titles metadata
#   5. Reading Talismane data file and updating titles
#   6. Boot

#-------------------------------------------------
# Imports
#-------------------------------------------------

# Standard
import datetime
from enum import Enum
from importlib import reload # Dynamic code

# Project
import whiteboard as wb # Dynamic code

#-------------------------------------------------
# Handling of simplification of Domains
#-------------------------------------------------

# Loading recoding dictionary
recode=dict()

def load_recode(debug=False):
    global recode
    entree = open("recodage-josette.tsv", mode="r", encoding="UTF8")
    header = entree.readline()
    for line in entree:
        line=line.rstrip("\n")
        t=line.split("\t")
        recode[t[0]]=t[3]
    entree.close()

def domain(domains):
     champs = domains.split(",")
     dom=""
     for c in champs:
          if (c.startswith("0") or c.startswith("1")) and c != "0.shs":
               if c in recode:
                    return recode[c] #first domain only
               else:
                    return 'RECODE FAIL'

#-------------------------------------------------
# Data model for Words and Titles
#-------------------------------------------------

class Word:

    unknown_lemma = {}
    
    def __init__(self, form, lemma, pos, info, gov, dep):
        self.form = form
        if lemma == '_':
            self.lemma = f"?{form}"
            Word.unknown_lemma[form + ':::' + pos] = ''
        else:
            self.lemma = lemma
        self.pos = pos
        self.info = info
        self.gov = gov # = index in title.words + 1 (start at 1, 0 = no gov)
        self.dep = dep

    def __str__(self):
        return f"{self.form}"
    
    def __repr__(self):
        return f"<Word {self.form, self.lemma, self.pos}>"

    @classmethod
    def write_unknown_lemma(cls):
        out = open('unknown_lemma.txt', mode='w', encoding='utf8')
        for wp in cls.unknown_lemma:
            out.write(wp + '==>?\n')
        out.close()


class Title:

    def __init__(self, idt, year, typ, domains, authors, text):
        self.idt = idt
        self.year = year
        self.typ = typ
        self.domains = domains
        self.authors = authors
        self.nb = authors.count(',') + 1
        self.text = text
        self.words = []

    def __repr__(self):
        return f"<Title |{self.text[:20]}| #{self.typ} @{self.year}>"

    def __str__(self):
        return f"{self.text}"

#-------------------------------------------------
# Read titles metadata
#-------------------------------------------------

def read_titles_metadata(file_name):
    """Create the titles from a TSV file"""
    print('[RUN ] --- read_titles_metadata @' + file_name)
    start_time = datetime.datetime.now()
    print('[INFO] --- Started at', start_time)
    titles = {}
    try:
        file = open(file_name, encoding='utf8', mode='r')
        content = file.readlines()
    except FileNotFoundError:
        print('File not found.')
    except UnicodeDecodeError:
        print('Invalid utf-8 format.')
    else:
        print('[INFO] ---', len(content), 'lines.') # 339687
        for line in content:
            elements = line.split('\t')
            idt = elements[0]
            year = elements[1]
            typ = elements[2][1:-1]
            domains = elements[3][1:-1]
            authors = elements[4][1:-1]
            text = elements[5][1:-1]
            t = Title(idt, year, typ, domains, authors, text)
            titles[t.idt] = t
        file.close()
    print('[INFO] ---', len(titles), 'titles.') # 339687
    end_time = datetime.datetime.now()
    print('[INFO] --- Ending at', end_time)
    delta = end_time - start_time
    print(f"[INFO] --- Script has ended [{delta} elapsed].\n")
    return titles

#-------------------------------------------------
# Reading Talismane data file and updating titles
#-------------------------------------------------

class State(Enum):
    START = 1
    IN_TITLE = 2

def read_update_from_talismane_data(titles, file_name):
    """Update the titles with Talismane informations"""
    print('[RUN ] --- read_update_from_talismane_data @ ' + file_name)
    start_time = datetime.datetime.now()
    print('[INFO] --- Started at', start_time)
    # read
    try:
        file = open(file_name, encoding="utf8", mode="r")
    except FileNotFoundError:
        raise Exception("File not found: " + file_name)
    else:
        lines = file.readlines()
        print('[INFO] --- Lines read:', len(lines))
    # parcours
    state = State.START
    words = []
    idt = None
    key_lin = ''
    nb_line = 1
    updated = 0
    for lin in lines:
        if state == State.START:
            if lin.startswith('<title id="'):
                state = State.IN_TITLE
                idt = lin[11:len(lin)-3]
                key_lin = lin
                words = []
            elif lin.startswith("</title>"):
                pass # bug, multiple </title>
            else:
                raise Exception(str(state) + " encountered: |" + lin + "| @line " + str(nb_line))
        elif state == State.IN_TITLE:
            if len(lin) == 1: #only \n
                pass
            elif lin.startswith("</title>"):
                state = State.START
                try:
                    titles[idt].words = words
                    updated += 1
                except KeyError:
                    print('[ERROR] ---', key_lin)
                    exit(1)
            else:
                try:
                    elements = lin.split('\t')
                    #idw = elements[0]
                    form = elements[1]
                    lemma = elements[2]
                    typ1 = elements[3]
                    #typ2 = elements[4]
                    info = elements[5]
                    gov = elements[6]
                    dep = elements[7]
                    #x3 = elements[8]
                    #x4 = elements[9]
                    words.append(Word(form, lemma, typ1, info, gov, dep))
                except IndexError:
                    #unclosed title
                    titles[idt].words = words
                    updated += 1
                    state = State.IN_TITLE
                    idt = lin[11:len(lin)-3]
                    key_lin = lin
                    words = []
                    #raise Exception(str(state) + " IndexError : |" + lin + "| @line " + str(nb_line))
        nb_line += 1
    print('[INFO] --- Titles updated:', updated)
    end_time = datetime.datetime.now()
    print('[INFO] --- Ending at', end_time)
    delta = end_time - start_time
    print(f"[INFO] --- Script has ended [{delta} elapsed].\n")
    return titles

#-------------------------------------------------
# Boot
#-------------------------------------------------

titles = {}

def init(debug):
    global titles
    load_recode(debug)
    if debug: print('[INFO] --- Domain recode dictionary loaded\n')
    titles = read_titles_metadata(r'data\total-articles-HAL.tsv')
    files = [r"data\output_tal_01.txt",
             r"data\output_tal_02.txt",
             r"data\output_tal_03.txt",
             r"data\output_tal_04.txt",
             r"data\output_tal_05.txt",
             r"data\output_tal_06.txt"]
    for file in files:
        read_update_from_talismane_data(titles, file)
    #Word.write_unknown_lemma()
    t = titles[list(titles.keys())[0]]
    print(t)

if __name__ == '__main__':
    init(True)

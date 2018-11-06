#-------------------------------------------------
# Import
#-------------------------------------------------

# standard
from enum import Enum
import datetime

#-------------------------------------------------
# Data model
#-------------------------------------------------

class Word:
    
    def __init__(self, form, lemma, pos, info, gov, dep):
        self.form = form
        self.lemma = lemma
        self.pos = pos
        self.info = info
        self.gov = gov
        self.dep = dep

    def __str__(self):
        return "f{self.form}"
    
    def __repr__(self):
        return f"<Word {self.form, self.lemma, self.pos}>"

class Title:

    def __init__(self, idt, year, typ, domains, authors, text):
        self.idt = idt
        self.year = year
        self.typ = typ
        self.domains = domains
        self.authors = authors
        self.text = text
        self.words = []

    def __repr__(self):
        return f"<Title |{self.text[:20]}| #{self.typ} @{self.year}>"

    def __str__(self):
        return f"{self.text}"

#-------------------------------------------------
# Split talismane data file into multiple parts
#-------------------------------------------------

def split(file_name, nb_total_part = 6):
    print('[RUN ] --- split')
    start_time = datetime.datetime.now()
    print('[INFO] --- Started at', start_time)
    try:
        file = open(file_name, encoding='utf8', mode='r')
    except FileNotFoundError:
        print('File not found.')
    except UnicodeDecodeError:
        print('Invalid utf-8 format.')
    else:
        content = file.readlines()
        nb = 0
        nb_part = 0
        nb_by_part = len(content) // nb_total_part
        output = None
        # begin counting
        itercount = 0
        iterdisplay = 10000
        iterstep = 10000
        for line in content:
            itercount += 1
            if itercount == iterdisplay:
                print('Titles done : ', itercount, ' / ', len(lines), '.', sep='')
                iterdisplay += iterstep
            # end counting
            if nb == nb_by_part:
                output.close()
                nb = 0
            if nb == 0:
                nb_part += 1
                output = open(f"output_{nb_part:02d}.txt", encoding='utf8', mode='w')
            nb += 1
            output.write(line)
        if output is not None:
            output.close()
        print('File', nb_part, 'created.')
    end_time = datetime.datetime.now()
    print('[INFO] --- Ending at', end_time)
    delta = end_time - start_time
    print(f"[INFO] --- Script has ended [{delta} elapsed].\n")

#-------------------------------------------------
# Read titles metadata
#-------------------------------------------------

def read_titles_metadata(file_name):
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
# Output titles only
#-------------------------------------------------

def output_titles(titles):
    print('[RUN ] --- output_titles')
    output = open(r'data\titles_' + str(len(titles)) + '.txt', encoding='utf8', mode='w')
    for key, t in titles.items():
        output.write(t.text.replace('\\,', ',').replace('""', '"') + '\n')
    output.close()
    print('[END ] --- end output_titles.\n')

def output_titles_multifiles(titles):
    print('[RUN ] --- output_titles_multifiles')
    for key, t in titles.items():
        output = open('data\\titles\\' + t.idt + '.txt', encoding='utf8', mode='w')
        output.write(t.text.replace('\\,', ',').replace('""', '"'))
        output.close()
    print('[END ] --- end output_titles.\n')

#-------------------------------------------------
# Info on titles
#-------------------------------------------------

def info(titles):
    print('[RUN ] --- info on pos and dep labels')
    pos = []
    dep = []
    nb_words = 0
    for key, t in titles.items():
        for w in t.words:
            if w.dep not in dep:
                dep.append(w.dep)
            if w.pos not in pos:
                pos.append(w.pos)
            nb_words += 1
    print(f'[INFO] --- {len(pos)} dependencies types:')
    for p in sorted(pos):
        print('          ', p)
    print(f'[INFO] --- {len(dep)} dependencies types:')
    for d in sorted(dep):
        print('          ', d)
    print(f'[INFO] --- {len(titles)} titles.')
    print(f'[INFO] --- {nb_words} words.')

#-------------------------------------------------
# Write only title, one title per line
#-------------------------------------------------

if __name__ == '__main__':
    # OK split('titres-articles-HAL.tal', 6)
    # Read meta data and output titles only
    titles = read_titles_metadata(r'data\total-articles-HAL.tsv')
    # OK output_titles(titles)
    # output_titles_multifiles(titles)
    # Read Talismane data
    files = [r"data\output_tal_01.txt",
             r"data\output_tal_02.txt",
             r"data\output_tal_03.txt",
             r"data\output_tal_04.txt",
             r"data\output_tal_05.txt",
             r"data\output_tal_06.txt"]
    for file in files:
        read_update_from_talismane_data(titles, file)
    # Info on titles
    # if len(titles) > 0:
    #    t = titles[list(titles.keys())[0]]
    #    print(t)
    info(titles)

# 339687 titres

# http://joliciel-informatique.github.io/talismane/#section2.3.5
# The CoNLL format used by Talismane outputs the following information in each row:

# The token number (starting at 1 for the first token)
# The original word form (or _ for an empty token)
# The lemma found in the lexicon (or _ when unknown)
# The part-of-speech tag
# The grammatical category found in the lexicon
# The additional morpho-syntaxic information found in the lexicon.
# Additional morpho-syntaxic information:
#   g=m|f: gender = male or female
#   n=p|s: number = plural or singluar
#   p=1|2|3|12|23|123: person = 1st, 2nd, 3rd (or a combination thereof if several can apply)
#   poss=p|s: possessor number = plural or singular
#   t=pst|past|imp|fut|cond: tense = present, past, imperfect, future or conditional. Verb mood is not included, since it is already in the postag.
# The token number of this token's governor (or 0 when the governor is the root)
# The label of the dependency governing this token
# Labels :
#   _
#   a_obj
#   aff
#   arg
#   ato
#   ats
#   aux_caus
#   aux_pass
#   aux_tps
#   comp
#   coord
#   de_obj
#   dep
#   dep_coord
#   det
#   mod
#   mod_rel
#   obj
#   p_obj
#   ponct
#   prep
#   root
#   sub
#   suj


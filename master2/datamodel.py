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
#   6. Utils
#       find_title(attr, value, stop_on_first=True, listing=True)
#       pprint(dic)
#   7. Stats
#   8. Boot

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

def load_recoding_table(debug=False):
    global recode
    entree = open("recodage-josette.tsv", mode="r", encoding="UTF8")
    header = entree.readline()
    for line in entree:
        line=line.rstrip("\n")
        t=line.split("\t")
        recode[t[0]]=t[3]
    entree.close()

def recode_domain(title):
     champs = title.domains.split(",")
     dom=""
     for c in champs:
          if (c.startswith("0") or c.startswith("1")) and c != "0.shs":
               if c in recode:
                    return recode[c] #first domain only
               else:
                    raise Exception('Recoding domain failed for title: ' + title.idt)

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
        self.domain = recode_domain(self)
        self.authors = authors
        self.nb = authors.count(',') + 1
        self.text = text
        self.words = []
        self.restart = 0
        # updated in stats, must be called afer words is set
        self.nb_root = 0
        self.len_with_ponct = 0
        self.len_without_ponct = 0
        self.nb_seg = 1
    
    def __repr__(self):
        return f"<Title |{self.text[:20]}| #{self.typ} @{self.year} D{self.domain} Len({self.len_without_ponct} +{self.len_with_ponct - self.len_without_ponct}) Seg({self.nb_seg}) Root({self.nb_root})>"

    def __str__(self):
        return f"{self.text}"

    ponct_no_seg = {}
    
    def stats(self):
        for w in self.words:
            if is_root(w):
                self.nb_root += 1
            if w.pos != 'PONCT':
                self.len_without_ponct += 1
            elif is_seg(w):
                self.nb_seg += 1
            else:
                if w.form in Title.ponct_no_seg:
                    Title.ponct_no_seg[w.form] += 1
                else:
                    Title.ponct_no_seg[w.form] = 1
            self.len_with_ponct += 1

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

titles_with_more_than_one_paragraph = 0

class State(Enum):
    START = 1
    IN_TITLE = 2

def read_update_from_talismane_data(titles, file_name):
    global titles_with_more_than_one_paragraph
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
                if idt is not None:
                    titles[idt].stats() # on previous
                    titles[idt].restart = restart
                state = State.IN_TITLE
                idt = lin[11:len(lin)-3]
                key_lin = lin
                words = []
                prev_idw = 0
                restart = 0
                len_last_restart = 0
                count_before_restart = 0
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
                    idw = elements[0]
                    int_idw = int(idw)
                    if int(idw) <= prev_idw:
                        #raise Exception('Title with restarting Talismane indexes, aborting on ' + idt)
                        titles_with_more_than_one_paragraph += 1
                        restart += 1
                        len_last_restart = count_before_restart
                        count_before_restart = 0
                    prev_idw = int_idw
                    form = elements[1]
                    lemma = elements[2]
                    typ1 = elements[3]
                    #typ2 = elements[4]
                    info = elements[5]
                    gov = int(elements[6])
                    if gov != 0:
                        gov += len_last_restart
                    dep = elements[7]
                    #x3 = elements[8]
                    #x4 = elements[9]
                    words.append(Word(form, lemma, typ1, info, gov, dep))
                    count_before_restart += 1
                # ValueError is for int(idw)
                # IndexError is for access to elements
                except (ValueError, IndexError):
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
# Filtering
#-------------------------------------------------

filter_text = """           We keep :
             - only the title with 0 or 1 restart (= 1 or 2 paragraph)
             - only the title with 1 root
             - the root must be of type NC or NPP
             - nb_seg <= 2
"""

def filter_titles(debug=False):
    global titles
    too_many_restart = 0
    too_many_root = 0
    too_many_seg = 0
    root_not_nc_npp = 0
    ponct_not_known = 0
    keys_to_delete = []
    for kt, t in titles.items():
        if t.restart > 1:
            keys_to_delete.append(kt)
            too_many_restart += 1
        elif t.nb_root != 1:
            keys_to_delete.append(kt)
            too_many_root += 1
        elif t.nb_seg > 2:
            keys_to_delete.append(kt)
            too_many_seg += 1
        else:
            for w in t.words:
                if is_root(w) and w.pos not in ['NC', 'NPP']:
                    keys_to_delete.append(kt)
                    root_not_nc_npp += 1
                    break
                elif w.pos == 'PONCT' and not is_seg(w) and not ponct_ok(w):
                    keys_to_delete.append(kt)
                    ponct_not_known += 1
                    break
    old_len = len(titles)
    for k in keys_to_delete:
        del titles[k]
    if debug:
        print(f"[INFO] --- Starting length =     {old_len:10d}")
        print(f"[INFO] --- Too many restart =    {too_many_restart:10d}")
        print(f"[INFO] --- Too many root =       {too_many_root:10d}")
        print(f"[INFO] --- Too many seg =        {too_many_seg:10d}")
        print(f"[INFO] --- Root not nc or npp =  {root_not_nc_npp:10d}")
        print(f"[INFO] --- Ponct not known =     {ponct_not_known:10d}")
        print(f"[INFO] --- Length after filter = {len(titles):10d}")

#-------------------------------------------------
# Utils
#-------------------------------------------------

def find_title(attr, value, stop_on_first=True, listing=True):
    for kt, t in titles.items():
        if getattr(t, attr) == value:
            print(kt)
            print(t)
            print(repr(t))
            if stop_on_first:
                if listing:
                    for i, w in enumerate(t.words):
                        print(f"{i+1:2d} {w.form:10s} {w.lemma:10s} {w.gov:3d}, {w.dep:5s}")
                return t

def tabpprint(tab,
              sort_key,
              until_total_percent = None,
              with_line = True,
              max_line = 50):
    lines = 0
    for k1 in sorted(tab, key=lambda x: tab[x][sort_key], reverse=True):
        for k2 in tab[k1]:
            print(tab[k1][k2], sep=' ', end='')
        print()
        lines += 1
        if lines >= max_line:
            break

def pprint(dic,
           min_num=None, min_percent=None,
           until_total_percent = None,
           with_line = True):
    total = sum(dic.values())
    total_percent = 0
    max_length = None
    if with_line: print("--------------------------------")
    for k in sorted(dic, key=dic.get, reverse=True):
        v = dic[k]
        if type(k) == str:
            if max_length is None:
                for kk in dic:
                    if max_length is None or max_length < len(kk):
                        max_length = len(kk)
                max_length = max(10, max_length)
            col1 = f"{k:{max_length}}"
        elif type(k) == int:
            col1 = f"{k:10d}"
        elif type(k) == tuple:
            col1 = f"{str(k):10}"
        col2 = f" | {v:7d}"
        col3 = f" | {((v/total)*100):8.4f}"
        total_percent += (v/total)*100
        print(col1 + col2 + col3)
        if with_line: print("--------------------------------")
        if min_num is not None and v < min_num: break
        if min_percent is not None and v/total*100 < min_percent: break
        if until_total_percent is not None and total_percent >= until_total_percent: break
    if max_length is None: max_length = 10
    if not with_line: print("--------------------------------")
    t = "TOTAL"
    print(f"{t:{max_length}} | {total:7d} | {total_percent:8.4f}")
    if with_line: print("--------------------------------")
    print()

def is_root(word):
    return word.gov == 0 and word.dep in ['_', 'root']

def is_seg(word):
     return word.pos == 'PONCT' and word.form in [
         ':', '.', '?', '!', '...', '…', ';', '..', '....', '?.', '?!',
         '...?', '?...', '.....', '!...', '!?', '!.', '!!!', '!!',
         '......', '??', '?..', '.?', '?!...']

def ponct_ok(word):
    if word.pos != 'PONCT':
        raise Exception('Not a ponct: ' + str(word))
    elif word.form in [',', '-', '"', '(', ')', "'", '[', ']', '&', '\\',
                       '*', '‑', '}', '{', '§', '†', '|', '·', '^', '‚', '‹',
                       '›', '¡', '‛', '・', '•', '/']:
        return True
    else:
        return False

def count(key, dic, typ=int):
    if key in dic:
        if type(dic[key]) == int:
            dic[key] += 1
        elif type(dic[key]) == dict:
            dic[key]['count'] += 1
    else:
        if typ == int:
            dic[key] = 1
        elif typ == dict:
            dic[key] = { 'count' : 1 }

def is_top_100_signoun(word):
    return word in ['exemple', 'cas', 'modèle', 'résultat', 'façon', 'problème',
                      'équation', 'théorie', 'terme', 'section', 'idée', 'point',
                      'figure', 'chose', 'système', 'table', 'question', 'raison',
                      'effet', 'méthode', 'procédé', 'facteur', 'type', 'fait',
                      'principe', 'réaction', 'problème', 'approche', 'expérience',
                      'procédure', 'forme', 'condition', 'taux', 'droit', 'type',
                      'solution', 'fonction', 'changement', 'valeur', 'étude',
                      'argument', 'possibilité', 'abilité', 'différence', 'loi',
                      'série', 'zone', 'concept', 'analyse', 'conclusion', 'situation',
                      'article', 'politique', 'vue', 'réponse', 'relation', 'stratégie',
                      'conséquence', 'supposition', 'étape', 'période', 'scène', 'but',
                      'discussion', 'échec', 'essai', 'propriété', 'chapitre', 'trait',
                      'caractéristique', 'expression', 'potentiel', 'technique', 'sujet',
                      'paramètre', 'mécanisme', 'instance', 'indice', 'partie',
                      'introduction', 'test', 'rôle', 'objectif', 'coefficient',
                      'décision', 'comportement', 'intention', 'prévision',
                      'hypothèse', 'nombre', 'implication', 'avantage', 'définition',
                      'observation', 'notion', 'phénomène', 'objectif', 'mot',
                      'difficulté', 'sujet']
                      
#-------------------------------------------------
# Stats
#-------------------------------------------------

stats = {}

def calc_stats(titles):
    global stats
    # Title stats
    keys = ["restart", "nb_seg", "nb_root"]
    for k in keys:
        stats[k] = {}
    # Word stats
    stats['root_pos']    = {} # pos of root
    stats['root_lemma']  = {} # lemma of root
    stats['seg_combi']   = {} # combinaison of seg
    stats['seg_lemma']   = {} # lemma of seg ponct
    for kt, t in titles.items():
        combi = []
        for k in keys:
            val = getattr(t, k)
            count(val, stats[k])
        for w in t.words:
            if is_root(w):
                count(w.pos, stats['root_pos'])
                count(w.lemma + '::' + w.pos, stats['root_lemma'], typ=dict)
            if is_seg(w):
                count(w.lemma, stats['seg_lemma'])
                combi.append(w.form)
        combi_tuple = tuple(combi)
        count(tuple(combi), stats['seg_combi'])
    for k in stats['root_lemma']:
        elements = k.split('::')
        stats['root_lemma'][k]['lemma'] = elements[0]
        stats['root_lemma'][k]['pos'] = elements[1]
        stats['root_lemma'][k]['top 100 SgN'] = is_top_100_signoun(elements[0])

#-------------------------------------------------
# Boot
#-------------------------------------------------

titles = {}

def init(debug):
    global titles
    load_recoding_table(debug)
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
    if debug:
        print("[INFO] --- Total Titles :", len(titles))
        print("[INFO] --- Titles with more than one paragraph (restarting index) :", titles_with_more_than_one_paragraph)
    #Word.write_unknown_lemma()
    filter_titles(debug)
    if debug:
        print('[INFO] Filtered with filter =')
        print(filter_text)
        print('[INFO] --- Total Titles filtered :', len(titles))
    calc_stats(titles)
    if debug: print('[INFO] --- Stats calculated, access by stats')
    if debug:
        print('[INFO] --- Ponctuation which is not segment :')
        pprint(Title.ponct_no_seg)
    print()
    t = titles[list(titles.keys())[0]]
    print(t)
    print(repr(t))
    print()
    print('Root pos :')
    pprint(stats["root_pos"])
    print('Nb root :')
    pprint(stats["nb_root"])
    print('Root lemma :')
    tabpprint(stats['root_lemma'], sort_key='count')
    #pprint(stats['root_lemma'], until_total_percent=50.00, with_line=False)
    print('Nb seg :')
    pprint(stats["nb_seg"])
    print('Lemma seg :')
    pprint(stats["seg_lemma"])
    print('Combi of seg :')
    pprint(stats["seg_combi"])
    print()

if __name__ == '__main__':
    init(True)

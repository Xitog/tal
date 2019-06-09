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
#   7. Model for results
#   8. Stats
#   9. Boot

#-------------------------------------------------
# Imports
#-------------------------------------------------

# Standard
import datetime
from enum import Enum
from importlib import reload # Dynamic code
import itertools # cribble

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
    return 'NONE'

#-------------------------------------------------
# Data model for Words and Titles
#-------------------------------------------------

class Word:

    unknown_lemma = {}
    
    def __init__(self, idw, form, lemma, pos, info, gov, dep):
        self.form = form
        if lemma == '_':
            self.lemma = f"?{form}"
            Word.unknown_lemma[form + ':::' + pos] = ''
        else:
            self.lemma = lemma
        self.idw = idw
        self.pos = pos
        self.info = info
        self.gov = gov # = index in title.words + 1 (start at 1, 0 = no gov) /!\ if restarts !
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
        self.restarts = []
        self.nb_restarts = 0
        self.nb_parts = 0 # nb_parts = nb_restarts + 1
        # updated in stats, must be called afer words is set
        self.nb_roots = 0
        self.roots = []
        self.len_with_ponct = 0
        self.len_without_ponct = 0
        self.nb_segments = 1
        self.segments = []
        self.roots_by_segments = 'NOVAL'
        # combi
        self.parts_segments = 'NOVAL'
    
    def __repr__(self):
        return f"<Title |{self.text[:20]}| #{self.typ} @{self.year} D{self.domain} Len({self.len_without_ponct} +{self.len_with_ponct - self.len_without_ponct}) Seg({self.nb_segments}) Root({self.nb_roots})>"

    def __str__(self):
        return f"{self.text}"

    def info(self):
        for i, w in enumerate(self.words):
            print(f"{i+1:2d}. {w.idw:3d} {w.form:16} {w.pos:5} {w.lemma:16} {w.gov:3d}, {w.dep:5}")
    
    ponct_no_seg = {}
    
    def init(self, words, restarts):
        self.words = words
        self.restarts = restarts
        self.nb_restarts = len(restarts)
        self.nb_parts = self.nb_restarts + 1
        current_seg_nb_roots = 0
        self.roots_by_segments = []
        for cpt, w in enumerate(self.words):
            if is_root(w):
                self.nb_roots += 1
                self.roots.append(cpt)
                current_seg_nb_roots += 1
            if w.pos != 'PONCT':
                self.len_without_ponct += 1
            elif is_seg(w):
                self.nb_segments += 1
                self.segments.append(cpt)
                self.roots_by_segments.append(current_seg_nb_roots)
                current_seg_nb_roots = 0
            else:
                if w.form in Title.ponct_no_seg:
                    Title.ponct_no_seg[w.form] += 1
                else:
                    Title.ponct_no_seg[w.form] = 1
            self.len_with_ponct += 1
        if not is_seg(self.words[-1]):
            self.roots_by_segments.append(current_seg_nb_roots)
        if sum(self.roots_by_segments) != len(self.roots):
            raise Exception("A root has no segment!")
        self.parts_segments = f"{self.nb_parts:1d}:{self.nb_segments:1d}"
        self.roots_by_segments = ':'.join([str(x) for x in self.roots_by_segments])

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
    updated = 0
    for index in range(len(lines)):
        line = lines[index]
        if line.startswith('<title id="'):
            idt = line[11:len(line)-3]
            words = []
            prev_idw = None
            restarts = []
            index += 1
            line = lines[index]
            while not line.startswith('<title id="'):
                elements = line.split('\t')
                if len(elements) == 10:
                    idw = int(elements[0])
                    if prev_idw is not None and idw < prev_idw:
                        restarts.append(len(words))
                    prev_idw = idw
                    form = elements[1]
                    lemma = elements[2]
                    typ1 = elements[3] # 4 is the same
                    info = elements[5]
                    gov = int(elements[6])
                    dep = elements[7] # 8 and 9 are the same
                    words.append(Word(idw, form, lemma, typ1, info, gov, dep))
                index += 1
                try:
                    line = lines[index]
                except IndexError:
                    break
            titles[idt].init(words, restarts)
            updated += 1
            index -= 1
        index += 1
    end_time = datetime.datetime.now()
    print(f'[INFO] --- Titles updated: {updated}')
    print(f'[INFO] --- Ending at {end_time}')
    print(f"[INFO] --- Script has ended [{end_time - start_time} elapsed].\n")
    return titles

#-------------------------------------------------
# Filtering
#-------------------------------------------------

MAX_NB_PART = 1
MIN_NB_ROOT = 1
MAX_NB_ROOT = 1
MAX_NB_SEG  = 2
ROOT_POS_OK = ['NC', 'NPP']

filter_text = f"""           We keep :
             - only the title with {MAX_NB_PART} part (restart = nb_part - 1)
             - only the title with {MIN_NB_ROOT} <= root <= {MAX_NB_ROOT}
             - the root must be of type {ROOT_POS_OK}
             - nb_segments <= {MAX_NB_SEG}
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
        if t.restart > (MAX_NB_PART - 1):
            keys_to_delete.append(kt)
            too_many_restart += 1
        elif not MIN_NB_ROOT <= t.nb_roots <= MAX_NB_ROOT:
            keys_to_delete.append(kt)
            too_many_root += 1
        elif t.nb_segments > MAX_NB_SEG:
            keys_to_delete.append(kt)
            too_many_seg += 1
        else:
            for w in t.words:
                if is_root(w) and w.pos not in ROOT_POS_OK:
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

def is_root(word : Word):
    return word.gov == 0 and word.dep in ['_', 'root']

def is_seg(word : Word): # : ; . ? ! + variantes du .?!
     return word.pos == 'PONCT' and word.form in [
         ':', '.', '?', '!', '...', '…', ';', '..', '....', '?.', '?!',
         '...?', '?...', '.....', '!...', '!?', '!.', '!!!', '!!',
         '......', '??', '?..', '.?', '?!...']

def ponct_ok(word : Word):
    if word.pos != 'PONCT':
        raise Exception('Not a ponct: ' + str(word))
    elif word.form in [',', '-', '"', '(', ')', "'", '[', ']', '&', '\\',
                       '*', '‑', '}', '{', '§', '†', '|', '·', '^', '‚', '‹',
                       '›', '¡', '‛', '・', '•', '/']:
        return True
    else:
        return False


def is_top_100_signoun(word : str):
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
# Model for results
#-------------------------------------------------

class Column:

    def __init__(self, data, name, kind='num', wide=10):
        self.data = data
        self.name = name # can be a tuple (or any kind) !
        self.kind = kind
        self.total = 0
        self.max_length = 10
        self.wide = 10
    
    def update(self):
        if self.kind == 'num':
            self.total = 0
            for rec in self.data:
                self.total += self.data[rec][self.name]
            self.max_length = max(self.wide, len(self.name), len(str(self.total)))
        elif self.kind in ['str', 'tuple']:
            self.max_length = 0
            for rec in self.data:
                if len(str(self.data[rec][self.name])) > self.max_length:
                    self.max_length = len(str(self.data[rec][self.name]))
            self.max_length = max(self.max_length, len(self.name))
        elif self.kind == 'bool':
            self.max_length = 5
        else:
            raise Exception('Type of column not known, must be num, str or bool for col ' + self.name)
    
    def __str__(self):
        return f"{str(self.name):{self.max_length}} "
    
    def __getitem__(self, rec):
        return self.data[rec][self.name]


class Data:

    def __init__(self, col_defs : dict):
        self.columns = {}
        for n, k in col_defs.items():
            self.columns[n] = Column(self, name=n, kind=k)
        self.content = {}
        self.default_counted_columns = self.columns[next(iter(self.columns))]

    @staticmethod
    def from_dict(dic):
        "convert a dict { 'abc' : 5, 'def' : 10 } to { 'abc' : { 'count' : 5 }, 'deg' : { 'count' : 10 } }"
        d = Data({'key' : 'str', 'count' : 'num'})
        for k, v in dic.items():
            d.set_cell(k, 'key', k)
            d.set_cell(k, 'count', v)
        return d
    
    def __getitem__(self, rec):
        return self.content[rec]

    def __iter__(self):
        self.itr = iter(self.content)
        return self

    def __next__(self):
        return next(self.itr)
    
    def set_cell(self, rec, col, val):
        if rec not in self.content:
            self.content[rec] = {}
        self.content[rec][col] = val

    def get_cell(self, rec, col):
        return self.content[rec][col]
    
    def __length__(self):
        return len(self.content)
    
    def nb_columns(self):
        return len(self.col_names)

    def update(self):
        for _, col in self.columns.items():
            col.update()
    
    def count(self, rec, col = None):
        if col is None:
            col = self.default_counted_columns
        if rec in self.content:
            self.content[rec]['count'] += 1
        else:
            self.set_cell(rec, col.name, rec)
            self.set_cell(rec, 'count', 1)
    
    def display(self, sort_key = 'count', with_line = True,
                max_line = None, until_total_percent = None, min_percent = None):
        self.update()
        total_percent = 0.0
        percent = None
        len_line = 8 # for percent col
        for _, col in self.columns.items():
            len_line += len(str(col))
        # Header
        print('-' * len_line)
        for _, col in self.columns.items():
            print(str(col), end='')
            if col.name == sort_key:
                print("percent ", end='')
        print()
        print('-' * len_line)
        # Body
        lines = 0
        for k1 in sorted(self.content, key=lambda x: self.content[x][sort_key], reverse=True):
            for _, col in self.columns.items():
                print(f"{str(col[k1]):{col.max_length}} ", end='')
                if col.name == sort_key:
                    percent = (col[k1]/col.total) * 100
                    total_percent += percent
                    print(f"{percent:8.4f} ", end='')
            print()
            if with_line: print('-' * len_line)
            lines += 1
            # breakers
            if max_line is not None and lines >= max_line:
                print("... (percent indicates what's taken)")
                break
            if until_total_percent is not None and total_percent >= until_total_percent:
                print("... (percent indicates what's taken)")
                break
            if min_percent is not None and percent is not None and percent < min_percent:
                print("... (percent indicates what's taken)")
                break
        # Footer
        if not with_line: print('-' * len_line)
        for _, col in self.columns.items():
            print(str(col), end='')
            if col.name == sort_key:
                print("percent ", end='')
        print()
        for _, col in self.columns.items():
            if col.name != sort_key:
                print(len(str(col)) * ' ', end='')
            else:
                print(f"{str(col.total):{col.max_length}}", end='')
                print(f"{total_percent:8.4f}", end='')
        print()
        print('-' * len_line)
        print()

#-------------------------------------------------
# Stats
#-------------------------------------------------

stats = {}


def match_title(t, tested_keys_values):
    """
        match_title is used by find & count
        -> find retrieves titles corresponding to a set of conditions
        -> count counts the number of titles corresponding to a set of conditions
        -> match tells only if a title corresponds to a set of contions
        Keys can be :
        -> an attribute of title : nb_roots
        -> an sub-attribute of an element in a list attribute : roots.0.pos
        -> a length of an attribute : #roots
        Values can be :
        - only one (the value of the key must be corresponding to it)
        - a min and a max : through a tuple : min:max
        - a list of values : through a list : v1|v2|v3
        Exemples :
            count({'nb_roots' : 0})      only 0
            count({'nb_roots' : (0, 2)}) from 0 to 2
            count({'nb_roots' : [0, 2]}) only 0 or 2
            count({'nb_roots' : 0, 'nb_segments' : 1})
    """
    ok = True # for inclusive conditions, set this to False and set it True when a condition is reached
    for tested_key, tested_value in tested_keys_values.items():
        # Get the value
        if tested_key[0] == '#':
            attr = getattr(t, tested_key[1:])
            val = len(attr)
        elif '.' in tested_key:
            attr_key, attr_index, obj_key, obj_val = k.split('.') # roots.0.pos
            attr = getattr(t, attr_key)
            if int(attr_index) >= len(attr):
                raise Exception('Index not in range')
            val = getattr(attr[int(attr_index)], obj_key)
        else:
            val = getattr(t, tested_key)
        # Test
        if type(tested_value) in [int, str]:
            if val != tested_value:
                ok = False
        elif type(tested_value) == tuple:
            min_val = tested_value[0]
            max_val = tested_value[1]
            if not min_val <= val <= max_val:
                ok = False
        elif type(tested_value) == list:
            if val not in tested_value:
                ok = False
        else:
            raise Exception('Tested value unknown type:' + str(type(tested_value)))
    return ok


def select(tested_keys_values):
    res_list = find(tested_keys_values, len(titles), display=False)
    res_dict = {}
    for t in res_list:
        res_dict[t.idt] = t
    return res_dict


def find(tested_keys_values, nb=5, display=True):
    selected = []
    for kt, t in titles.items():
        if match_title(t, tested_keys_values):
            selected.append(t)
            if display:
                print(t.idt, t)
                print('-' * len(str(t)))
                t.info()
            if len(selected) == nb:
                break
    return selected


def cribble(threshold, *keys):
    # get all the values
    vals = {}
    for k in keys:
        vals[k] = []
    for kt, t in titles.items():
        for k in keys:
            val = getattr(t, k)
            if val not in vals[k]:
                vals[k].append(val)
    # get the count for all combinaisons
    counted = {}
    total = 0
    length = len(titles)
    for combi in itertools.product(*vals.values()):
        tested = {}
        for i, k in enumerate(keys):
            tested[k] = combi[i]
        res = count(tested)
        if (res / length)* 100 >= threshold:
            counted[combi] = res
            total += res
    # display results
    print('number of combi   :', len(counted))
    print('number of titles  :', total)
    print('percent of titles :', f"{(total/length)*100:5.2}")
    # display the combi
    for combi in counted:
        print(f"{str(combi):10}", f"{counted[combi]:10d}", f"{(counted[combi]/length)*100:5.2f}")


def count(tested_keys_values=None):
    """
        Used to count the title corresponding to the values of the tested keys.
    """
    if tested_keys_values is None:
        return len(titles)
    count = 0
    for kt, t in titles.items():
        if match_title(t, tested_keys_values):
            count += 1
    return count


def stat(keys=None, display=True, until_total_percent=None):
    """
        Used to make stat on one or more keys of the titles.
        - If no keys is passed, it counts the number of titles.
        - If one key is passed, it counts the number of titles for each different values of this key.
        - If more than one key is passed, it counts the number of titles for each different combinations of the values of these keys.
        - The key can be of a special format : roots.0.pos <=> t.roots[0].pos
    """
    if keys is None:
        return len(titles)
    if type(keys) == str:
        keys = [keys]
    values = {}
    for key, t in titles.items():
        vals = []
        for k in keys:
            if '#' in k:
                attr = getattr(t, attr_key[1:])
                vals.append(len(attr))
            elif '.' in k:
                attr_key, attr_index, obj_key = k.split('.') # roots.0.pos
                attr = getattr(t, attr_key)
                if int(attr_index) >= len(attr):
                    vals.append('NO VAL')
                else:
                    vals.append(getattr(t.words[attr[int(attr_index)]], obj_key)) # works only for words
            else:
                vals.append(getattr(t, k))
        val = tuple(vals)
        if val not in values:
            values[val] = 0
        values[val] += 1
    total = 0
    for val in values:
        total += values[val]
    if display:
        s = f'*** {str(keys)} ***'
        print(s, '\n', '-' * len(s), sep='')
        i = 0
        cumul_percent = 0.0
        max_len = 10
        for key in values:
            if len(str(key)) > max_len: max_len = len(str(key))
        for key in sorted(values, key=values.get, reverse=True):
            i += 1
            percent = (values[key]/total)*100
            cumul_percent += percent
            d = '-'.join(map(str, key))
            print(f"{i:3d}. {d:>{max_len}} {values[key]:10d} {percent:8.4f} % {cumul_percent:6.2f} %")
            if until_total_percent is not None and cumul_percent > until_total_percent:
                print('...')
                break
    return values


def calc_stats(titles):
    global stats
    # Basic title stats
    keys = ['nb_restarts', 'nb_segments', 'nb_roots', 'nb', 'year', 'domain', 'typ',
            ('nb_parts', 'nb_segments'), ('domain', 'nb_segments') ]
    for key in keys:
        stat(key)
    # Word stats
    stats['root_pos']   = Data({ 'root_pos':'str', 'count':'num' }) # pos of root
    stats['root_lemma'] = Data({ 'root_lemma':'str', 'pos':'str', 'count':'num', 'is_sgn':'bool' }) # lemma of root
    stats['seg_combi']  = Data({ 'seg_combi':'tuple', 'count':'num' }) # combinaison of seg
    stats['seg_lemma']  = Data({ 'seg_lemma':'tuple', 'count':'num' }) # lemma of seg ponct
    # seg2 dependant from root of seg1
    stats['seg2_nb_dep_from_root'] = Data({ 'seg2_nb_dep_from_root' : 'num', 'count' : 'num' })
    stats['seg2_pos_dep_from_root'] = Data({ 'seg2_pos_dep_from_root' : 'str', 'count' : 'num' })
    stats['seg2_dep_dep_from_root'] = Data({ 'seg2_dep_dep_from_root' : 'str', 'count' : 'num' })
    stats['seg2_lem_dep_from_root'] = Data({ 'seg2_lem_dep_from_root' : 'str', 'pos' : 'str', 'count' : 'num', 'is_sgn' : 'bool' })
    for kt, t in titles.items():
        combi = []
        num_seg = 1
        pos_root = None
        nb_dep_from_root = 0
        for i, w in enumerate(t.words):
            if is_root(w):
                stats['root_pos'].count(w.pos)
                stats['root_lemma'].count(w.lemma + '::' + w.pos)
                pos_root = i + 1 # TALISMANE starts at 1
            if is_seg(w):
                stats['seg_lemma'].count(w.lemma)
                combi.append(w.form)
                num_seg += 1
            if num_seg > 1 and w.gov == pos_root:
                nb_dep_from_root += 1
                stats['seg2_pos_dep_from_root'].count(w.pos)
                stats['seg2_dep_dep_from_root'].count(w.dep)
                stats['seg2_lem_dep_from_root'].count(w.lemma + '::' + w.pos)
        if num_seg > 1:
            stats['seg2_nb_dep_from_root'].count(nb_dep_from_root)
        stats['seg_combi'].count(tuple(combi))
    for k in stats['root_lemma']:
        elements = k.split('::')
        stats['root_lemma'][k]['root_lemma'] = elements[0]
        stats['root_lemma'][k]['pos'] = elements[1]
        stats['root_lemma'][k]['is_sgn'] = is_top_100_signoun(elements[0])
    for k in stats['seg2_lem_dep_from_root']:
        elements = k.split('::')
        stats['seg2_lem_dep_from_root'][k]['seg2_lem_dep_from_root'] = elements[0]
        stats['seg2_lem_dep_from_root'][k]['pos'] = elements[1]
        stats['seg2_lem_dep_from_root'][k]['is_sgn'] = is_top_100_signoun(elements[0])

#-------------------------------------------------
# Boot
#-------------------------------------------------

old = None
titles = {}
t1   = None # t with 1 part
t11  = None # t with 1 part, 1 segment
t111 = None # t with 1 part, 1 segment, 1 root 
t12  = None # t with 1 part, 2 segments
t2   = None # t with 2 parts
t22  = None # t with 2 parts, 2 segments

fast = False
just_load = True

def init(debug):
    global titles, old, t1, t11, t111, t12, t2, t22
    load_recoding_table(debug)
    if debug: print('[INFO] --- Domain recode dictionary loaded\n')
    titles = read_titles_metadata(r'data\total-articles-HAL.tsv')
    if fast:
        files = [r"data\output_tal_01.txt"]
    else:
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
    # Selectors
    old = titles
    t1 = select({'nb_parts' : 1}) # len = 295331
    t11 = select({'parts_segments' : '1:1'}) # len = 175915
    t111 = select({'parts_segments' : '1:1', 'nb_roots' : 1}) # len = 155149
    t12 = select({'parts_segments' : '1:2'}) # len = 98931
    t2x = select({'nb_parts' : 2}) # len = 38808
    t2 = {} # len = 38346 (minus 462)
    t22 = {} # len = 25823
    for k, v in t2x.items():
        if is_seg(v.words[v.restarts[0] - 1]):
            t2[k] = v
            if v.nb_segments == 2:
                t22[k] = v
    del t2x
    print('t1 is available :', len(t1))
    print('t11 is available :', len(t11))
    print('t12 is available :', len(t12))
    print('t2 is available :', len(t2))
    print('t22 is available :', len(t22))
    print('Set titles to one of these values to change the corpus requested.')
    print('Set titles to old to reset')
    if not just_load:
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
            Data.from_dict(Title.ponct_no_seg).display()
        print()
        t = titles[list(titles.keys())[0]]
        print(t)
        print(repr(t))
        print()
        print('Root pos :')
        stats["root_pos"].display()
        print('Root lemma :')
        stats['root_lemma'].display(with_line=False, until_total_percent=50.00)
        print('Lemma seg :')
        stats["seg_lemma"].display()
        print('Combi of seg :')
        stats["seg_combi"].display()
        print()
        stats['seg2_nb_dep_from_root'].display()
        stats['seg2_pos_dep_from_root'].display()
        stats['seg2_dep_dep_from_root'].display()
        stats['seg2_lem_dep_from_root'].display(with_line=False, until_total_percent=50.0)
            
if __name__ == '__main__':
    init(True)

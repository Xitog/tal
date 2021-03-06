#-------------------------------------------------
# Import
#-------------------------------------------------

# Standard
import datetime
import pickle

# External lib
import xlwt

# Dynamic code
from importlib import reload
import whiteboard as wb

#-------------------------------------------------
# Switches
#-------------------------------------------------

LOAD_TITLES     = 'text' #'binary'
MAKE_STATS      = False
MAKE_POS_STATS  = False
MAKE_VERB_STATS = False
SEARCH_PATTERN  = [      # []
    "le cas de", "un cas de",
    "le problème de", "un problème de",
    "le exemple de", "un exemple de",
    "la question de", "une question de",
    "le étude de", "une étude de"]
PATTERN_OUTPUT  = None # 'excel'
DO_BINARY_SAVE  = False # 541 Mo, too slow to read!

#-------------------------------------------------
# Save or load results from binary dump
#-------------------------------------------------

def save(obj, filename):
    f = open(filename, mode='wb')
    pickle.dump(obj, f)
    f.close()

def load(filename):
    f = open(filename, mode='rb')
    data = pickle.load(f)
    f.close()
    return data

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
                print('Titles done : ', itercount, ' / ', len(content), '.', sep='')
                iterdisplay += iterstep
            # end counting
            if nb == nb_by_part:
                output.close()
                nb = 0
            if nb == 0:
                nb_part += 1
                output = open(f"data\\details\\{nb_part:02d}.txt", encoding='utf8', mode='w')
                #output = open(f"output_{nb_part:02d}.txt", encoding='utf8', mode='w')
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
    print('[END ] --- end info.\n')

#-------------------------------------------------
# Explore
#-------------------------------------------------

def explore(titles, lemma):
    print('[RUN ] --- explore')
    data = {}
    for key, t in titles.items():
        for iw in range(len(t.words)):
            w = t.words[iw]
            if w.lemma == lemma:
                if len(t.words)-1 > iw > 0:
                    key = (t.words[iw-1].lemma, lemma, t.words[iw+1].lemma)
                elif iw < len(t.words)-1:
                    key = ('START', lemma, t.words[iw+1].lemma)
                elif iw > 0:
                    key = (t.words[iw-1].lemma, lemma, 'END')
                if key in data:
                    data[key] += 1
                else:
                    data[key] = 1
    print('[END ] --- end explore.\n')
    return data

def explore_after(titles, lemma, ok_lemma_after):
    """Explore what comes after an expression"""
    print('[RUN ] --- explore_after')
    data = {}
    for key, t in titles.items():
        for iw in range(len(t.words)):
            w = t.words[iw]
            if w.lemma == lemma:
                if iw < len(t.words)-2:
                    if t.words[iw+1].lemma in ok_lemma_after:
                        key = t.words[iw+2].lemma
                    if key in data:
                        data[key] += 1
                    else:
                        data[key] = 1
    print('[END ] --- end explore2.\n')
    return data

def display(data, threshold=0):
    print('[INFO] --- Display threshold=', threshold)
    for key in sorted(data, key=data.get, reverse=True):
        value = data[key]
        if value >= threshold:
            print(f"{value:05d} {key}")
    print()


def gets(arr, idx):
    if idx < len(arr):
        return arr[idx]
    else:
        return None

#-------------------------------------------------
# Global information
#-------------------------------------------------

def title_stats(titles, attr):
    values = {}
    for k, t in titles.items():
        val = getattr(t, attr)
        if val in values:
            values[val] += 1
        else:
            values[val] = 1
    return values


def word_stats(titles, attr):
    values = {}
    for k, t in titles.items():
        for w in t.words:
            val = getattr(w, attr)
            if val in values:
                values[val] += 1
            else:
                values[val] = 1
    return values


def longueurs(titles):
    lng = {}
    for k, t in titles.items():
        cpt = 0
        for w in t.words:
            if w.pos != 'PONCT':
                cpt += 1
        if cpt in lng:
            lng[cpt] += 1
        else:
            lng[cpt] = 1
    return lng

def nb_with(titles, x, at_least = True):
    cpt = 0
    for k, t in titles.items():
        for w in t.words:
            if w.lemma == x or w.form == x:
                cpt += 1
                if at_least: break
    return cpt

# nb = nb_with(titles, ':')

#def at_least_one_verb(titles):
#    cpt = 0
#    for k, t in titles.items():
#        for w in t.words:
#            if w.pos in ['V', 'VIMP', 'VS']:
#                 if w.info.find('t=') != -1:
#                     cpt += 1
#                     break
#    return cpt

#def nb_true_phrases(titles):
#    cpt = 0
#    tenses = {}
#    for k, t in titles.items():
#        for w in t.words:
#            if w.pos == 'V':
#                i = w.info.find('t=')
#                if i != -1:
#                    cpt += 1
#                    t = w.info[i + 2]
#                    if t not in tenses:
#                        tenses[t] = 1
#                    else:
#                        tenses[t] += 1
#                    #print(w.form, t)
#    return cpt, tenses

def count_all_verbs(titles):
    combi = []
    combi_count = []
    for k, t in titles.items():
        count = {
            'VPP'  : 0,
            'VINF' : 0,
            'V'    : 0,
            'VPR'  : 0,
            'VS'   : 0,
            'VIMP' : 0
        }
        for w in t.words:
            if w.pos in count:
                count[w.pos] += 1
        if count in combi:
            index = combi.index(count)
            combi_count[index] += 1
        else:
            combi.append(count)
            combi_count.append(1)
    sortdict = {}
    for index, value in enumerate(combi_count):
        sortdict[index] = value
    # Output console
    for index in sorted(sortdict, key=sortdict.get, reverse=True):
        print("i=", index, "nb=", combi_count[index], "combi=", combi[index])
    # Output excel
    book = xlwt.Workbook()
    sheet1 = book.add_sheet('Verbs')
    header = sheet1.row(0)
    header.write(0, 'NB')
    header.write(1, 'VPP')
    header.write(2, 'VINF')
    header.write(3, 'V')
    header.write(4, 'VPR')
    header.write(5, 'VS')
    header.write(6, 'VIMP')
    irow = 1
    for index in sorted(sortdict, key=sortdict.get, reverse=True):
        row = sheet1.row(irow)
        icol = 0
        row.write(icol, combi_count[index])
        icol += 1
        for cpt, val in combi[index].items():
            row.write(icol, val)
            icol += 1
        irow += 1
    book.save('verbs.xls')

def count_all_tenses(titles, mode='V'):
    tenses = {}
    for k, t in titles.items():
        for w in t.words:
            if w.pos == mode:
                i = w.info.find('t=')
                if i != -1:
                    t = w.info[i + 2]
                    if t not in tenses:
                        tenses[t] = 1
                    else:
                        tenses[t] += 1
    for k in sorted(tenses, key=tenses.get, reverse=True):
        print(k, tenses[k])

#-----------------------------------------------------------
# Info
#-----------------------------------------------------------

def dump_text(titles, filename):
    f = open(filename, mode='w', encoding='utf8')
    for k in titles:
        print(titles[k].text, file=f)
    f.close()

# key can be a string !
def d2s(dic):
    total = 0
    kmax = None
    kmin = None
    for k in dic:
        total += dic[k]
    print('Total =', total)
    print()
    for k in sorted(dic, key=dic.get, reverse=True):
        print(f"{k:5d} {dic[k]:8d} {dic[k]/total:.3f}")
        if kmax is None: kmax = k
        elif kmax < k: kmax = k
        if kmin is None: kmin = k
        elif kmin > k: kmin = k
    print()
    print('Kmin =', kmin)
    print('Kmax =', kmax)
    print()
    cumul = 0
    for k in sorted(dic):
        cumul += dic[k]/total
        print(f"{k:5d} {dic[k]:8d} {dic[k]/total:.3f} {cumul:.3f}")

def dump_excel(titles, filename):
    print('[RUN ] --- dump_excel to', filename)
    book = xlwt.Workbook()
    sheet1 = book.add_sheet('Results')
    nb = 0
    for key, t in titles.items():
        row = sheet1.row(nb)
        row.write(0, domain(t.domains))
        row.write(1, t.nb)
        for index, word in enumerate(t.words):
            row.write(index + 2, word.form)
        nb += 1
    book.save(filename)
    print('[END ] --- dump_excel')

#-------------------------------------------------
# Combined
#-------------------------------------------------

class Search:

    def __init__(self, titles, pattern, name, output="text"):
        self.titles = titles
        if isinstance(pattern, str): self.pattern = pattern.split(' ')
        elif isinstance(pattern, list): self.pattern = pattern
        else: raise Exception('Pattern must be a list or a string')
        self.name = name
        self.output = output
        self.data = {}
        self.where = {}
        self.after_what_pos = { '$TART' : 0}
        self.after_what_form = {}
        
    def run(self):
        print('[RUN ] --- Search#run', ' '.join(self.pattern))
        print('[INFO] --- Matching')
        self.match()
        print('[INFO] --- Results')
        print('[INFO] Length:', len(self.data))
        #---
        print('[INFO] Position :')
        print('...  ', self.where)
        total = 0
        nb = 0
        for key, item in self.where.items(): 
            total += key * item
            nb += item
        if nb > 0:
            print('[INFO] Average position :', total / nb)
        else:
            print('[WARN] Nb is zero ! total=', total, 'nb=', nb)
        #---
        print('[INFO] What before :')
        print('... ', self.after_what_pos)
        print('... ', self.after_what_form)
        if self.output is not None:
            if 'bin' in self.output: save(self.data, self.name + ".bin")
            if 'text' in self.output: dump_text(self.data, self.name + ".txt")
            if 'excel' in self.output: dump_excel(self.data, self.name + ".xls")
        print('[END ] --- Search#run')


    def match(self):
        """match even there is not all elem"""
        for k, t in self.titles.items():
            nb = 0
            for wc in range(len(t.words)):
                w = t.words[wc]
                if w.lemma == self.pattern[0]:
                    res = True
                    for ec in range(1, len(self.pattern)):
                        wx = gets(t.words, wc + ec)
                        if wx is None or wx.lemma != self.pattern[ec]:
                            res = False
                            break
                    if res:
                        self.data[k] = t
                        if nb not in self.where:
                            self.where[nb] = 1
                        else:
                            self.where[nb] += 1
                        if nb > 0:
                            pos = t.words[nb - 1].pos
                            form = t.words[nb - 1].form
                            if pos in self.after_what_pos:
                                self.after_what_pos[pos] += 1
                            else:
                                self.after_what_pos[pos] = 1
                            if form in self.after_what_form:
                                self.after_what_form[form] += 1
                            else:
                                self.after_what_form[form] = 1
                        else:
                            self.after_what_pos['$TART'] += 1
                    break
                nb += 1

#-------------------------------------------------
# Lexique
#-------------------------------------------------

def lexique(titles, only=None):
    words = {}
    for k, t in titles.items():
        for w in t.words:
            o = w.lemma if w.lemma != '_' else w.form
            if only is not None and w.pos != only: continue
            if o not in words:
                words[o] = 1
            else:
                words[o] += 1
    return words


def total(data):
    cpt = 0
    for k in data:
        cpt += data[k]
    return cpt


def display(data, nb, maxx):
    print("Total = ", nb)
    for k in sorted(data, key=data.get, reverse=True):
        print(f"{k:14} {data[k]:8d} {data[k]/nb:.3f}")
        maxx -= 1
        if maxx == 0: break

def go(titles, maxx = 30):
    words = lexique(titles, 'NC')
    nb = total(words)
    display(words, nb, maxx)
    return words

#-------------------------------------------------
# Write only title, one title per line
#-------------------------------------------------

if __name__ == '__main__':
    # split(r'data\titles_339687.txt', 1000)
    # split('titres-articles-HAL.tal', 6)
    titles = {}
    if LOAD_TITLES == 'text':
        # Read meta data
        titles = read_titles_metadata(r'data\total-articles-HAL.tsv')
        # Output titles only
        #output_titles(titles)
        #output_titles_multifiles(titles, 5)
        # Read Talismane data
        files = [r"data\output_tal_01.txt",
                 r"data\output_tal_02.txt",
                 r"data\output_tal_03.txt",
                 r"data\output_tal_04.txt",
                 r"data\output_tal_05.txt",
                 r"data\output_tal_06.txt"]
        for file in files:
            read_update_from_talismane_data(titles, file)
    elif LOAD_TITLES == 'binary':
        print('[INFO] Load binary save for all titles.')
        titles = load("titles.bin")
    else:
        raise Exception("Titles must be loaded from text or binary.")
    if DO_BINARY_SAVE:
        print('[INFO] Do binary save for all titles.') 
        save(titles, "titles.bin")
    # Info on titles
    # if len(titles) > 0:
    #    t = titles[list(titles.keys())[0]]
    #    print(t)
    #info(titles)
    if SEARCH_PATTERN is not None and len(SEARCH_PATTERN) > 0:
        for pattern in SEARCH_PATTERN:
            s = Search(titles, pattern, pattern.replace(' ', '_'), PATTERN_OUTPUT).run()
            print()
    #data = explore(titles, "outil")
    #data = explore2(titles, "outil", ['de', 'pour'])
    #display(data, 10)
    #data = explore2(titles, "problème", ['de'])
    #display(data, 10)
    if MAKE_STATS:
        years = title_stats(titles, 'year')
        supports = title_stats(titles, 'typ')
        nb = title_stats(titles, 'nb')
    if MAKE_POS_STATS:
        pos = word_stats(titles, 'pos')
    if MAKE_VERB_STATS:
        count_all_verbs(titles)
        #count_all_tenses(titles, mode='V')






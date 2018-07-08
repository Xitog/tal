#===============================================================================
# Code handling the processing of the corpus of titles
#-------------------------------------------------------------------------------
# Author : Damien Gouteux
# Last updated : 25 June 2018
# Technologies & Tools : Python, Excel, XML, Talismane
#===============================================================================

#-------------------------------------------------------------------------------
# Import
#-------------------------------------------------------------------------------

# standard
import datetime
import os

# project
from titles import Word, Title, Corpus, has_only_one_form, no_filter, has_x_after_form, has_domain
from excel import ExcelFile, DynMatrix, MiniCell
from patterns import Pattern
#import pytalismane

#-------------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------------


def display(corpus : Corpus):
    print('[INFO] RUN dispay')
    print('[INFO] --- Processing')
    for title_id, title in corpus.titles.items():
        print('          ', title_id, ':', title.text)
    print('[INFO] END count')


def count_after_word(corpus : Corpus, form : str, display=True):
    """Count the number of words after a specific form in the titles. Return a dict:
         { 1 : title with only 1 word after this form,
           2 : title with two words after this form,
           ...
         }
    """
    print('[INFO] RUN count_after_word')
    print('[INFO] --- Processing')
    big = open('big.txt', mode='w', encoding='utf-8')
    one = open('one.txt', mode='w', encoding='utf-8')
    zero = open('zero.txt', mode='w', encoding='utf-8')
    counts = {}
    for title_id, title in corpus.titles.items():
        count = 0
        last = 0
        for i in range(0, len(title.words)):
            word = title.words[i]
            if word.form == form:
                count += 1
                last = i
        if count > 0: # at least once in the title
            after = len(title.words) - last - 1
            if after >= 30:
                big.write(f'{after} --- {title.docid} --- {title.text}\n')
            elif after == 0:
                zero.write(f'{after} --- {title.docid} --- {title.text}\n')
            elif after == 1:
                one.write(f'{after} --- {title.docid} --- {title.text}\n')
            if after not in counts:
                counts[after] = 1
            else:
                counts[after] += 1
    if display:
        print('[INFO] TXT Found ', len(counts), ' different number of words after ', form, sep='')
        for key in sorted(counts):
            print('          ', key, ':', f"{counts[key]:>6}")
    print('[INFO] --- Saving')
    excel = ExcelFile(name='count_after_' + form.replace(':', 'dblcol'), mode='w')
    data = {}
    for key, val in counts.items():
        data[key] = [key, val]
    excel.save_to_sheet_mul(
        name = 'COUNT_AFTER | nb occ %',
        values = data,
        order_col = 1,
        reverse_order = True,
        percent_col = 1)
    excel.close()
    zero.close()
    one.close()
    big.close()
    print('[INFO] END count_after_word')
    return counts


def count(corpus : Corpus, form : str, display=True):
    """Count a specific form in the titles. Return a dict:
         { 1 : title with only once this form,
           2 : title with twice this form,
           ...
         }
    """
    print('[INFO] RUN count')
    print('[INFO] --- Processing')
    counts = {}
    for title_id, title in corpus.titles.items():
        count = 0
        for word in title.words:
            if word.form == form:
                count += 1
        if count not in counts:
            counts[count] = 1
        else:
            counts[count] += 1
    if display:
        print('[INFO] TXT Found for form "', form, '", ', len(counts), ' configurations :', sep='')
        for key in sorted(counts):
            print('          ', key, ':', f"{counts[key]:>6}")
    print('[INFO] --- Saving')
    excel = ExcelFile(name='count_' + form.replace(':', 'dblcol'), mode='w')
    data = {}
    for key, val in counts.items():
        data[key] = [key, val]
    excel.save_to_sheet_mul(
        name = 'COUNT',
        values = data,
        order_col = 1,
        reverse_order = True,
        percent_col = 1)
    excel.close()
    print('[INFO] END count')
    return counts


def count_by_domain():
    corpus = Corpus.load(r'.\output_dump_repo\corpus_talismane.xml') #minidump
    domains = { 'UNKNOWN-DGX' : 0}
    itercount = 0
    iterdisplay = 1000
    iterstep = 1000
    print('-- Counting --')
    for title_id in corpus.titles:
        itercount += 1
        if itercount == iterdisplay:
            print(itercount, 'titles done.')
            iterdisplay += iterstep
        title = corpus[title_id]
        if len(title.domains) > 0:
            for dom in title.domains:
                if dom not in domains:
                    domains[dom] = 0
                domains[dom] += 1
        else:
            domains['UNKNOWN-DGX'] += 1
    print('-- Display --')
    excel = ExcelFile(name='titles_by_domain', mode='w')
    excel.save_to_sheet('Domains | nb', domains, corpus.count_titles())
    excel.close()
    # first by importance
    for key in sorted(domains, key=domains.get, reverse=True):
        if domains[key] > 0 and key.startswith('0. '):
            print(key, domains[key])
    print('---------------------------')
    print('---------------------------')
    # all by alphabetical order
    for key in sorted(domains.keys()):
        if domains[key] > 0:
            print(key, domains[key])
    

def filter_zero_words_duplicates_title(corpus):
    print('[INFO] RUN filter_zero_words_duplicates_title')
    key_to_delete = []
    nb_double = 0
    nb_empty = 0
    all_title_text = []
    itercount = 0
    iterdisplay = 1000
    iterstep = 1000
    old_length = len(corpus)
    print('[INFO] --- Processing : Filtering')
    for title_id in corpus.titles:
        itercount += 1
        if itercount == iterdisplay:
            print(itercount, 'titles done.')
            iterdisplay += iterstep
        title = corpus[title_id]
        if len(title.words) == 0:
            nb_empty += 1
            #print(nb_empty, '. (EMPTY) ', title.title, sep='')
            key_to_delete.append(title_id)
        elif title.title in all_title_text:
            nb_double += 1
            #print(nb_double, '. (DOUBLE) ', title.title, sep='')
            key_to_delete.append(title_id)
        else:
            #corpus.add_title(title)
            all_title_text.append(title.title)
    # Deletion
    for key in key_to_delete:
        del corpus.titles[key]
    print('[INFO] --- Saving')
    print('[INFO] TXT Origin corpus:', old_length)
    print('[INFO] TXT Saved corpus is:', len(corpus))
    print('[INFO] TXT Discarded: empty =', nb_empty, 'double =', nb_double, 'total =', nb_empty + nb_double)
    corpus.save('corpus_filtered')
    print('[INFO] END filter_zero_words_duplicates_title')


def basic_statistics():
    # Result file
    excel = ExcelFile(name='results3', mode='w')
    
    print('\n----- Loading corpus ------\n')
    corpus = Corpus.load(r'D:\Autres\dump.xml')
    
    print('\n----- Structures and words after : ------\n')
    TAGS = {}
    WORDS = {}
    window = 4
    for _, t in corpus.titles.items():
        current_tags = []
        current_words = []
        start = False
        for nb in range(0, len(t.words)):
            word = t.words[nb]
            tag  = t.pos_tags[nb]
            if word == ':':
                start = True
            elif start:
                current_tags.append(tag)
                current_words.append(word)
                if len(current_tags) == window:
                    break
        while len(current_tags) < window:
            current_tags.append('__EMPTY__')
        while len(current_words) < window:
            current_words.append('__EMPTY__')
        t_current_tags = tuple(current_tags)
        t_current_words = tuple(current_words)
        if t_current_tags not in TAGS:
            TAGS[t_current_tags] = 0
        if t_current_words not in WORDS:
            WORDS[t_current_words] = 0
        TAGS[t_current_tags] += 1
        WORDS[t_current_words] += 1
    
    excel.save_to_sheet('TAGS | nb', TAGS, corpus.count_titles())
    excel.save_to_sheet('WORDS | nb', WORDS, corpus.count_titles())
    
    print('\n----- Saving result file ------\n')
    
    excel.close()

def convert_to_new_format():
    corpus = Corpus.load(r'.\output_dump_repo\minidump.xml')
    corpus.save('mini_dump_converted')

def save_dont_mess(origin):
    print('[INFO] Running save_dont_mess')
    corpus = Corpus.load(r'.\output_dump_repo' + os.sep + origin)
    corpus.save(os.path.splitext(origin)[0] + '_same.xml')

def run_talismane(origin):
    print('[INFO] Running run_talismane')
    corpus = Corpus.load(r'.\output_dump_repo' + os.sep + origin)
    for title_id in corpus.titles:
        title = corpus[title_id]
        words = pytalismane.process_string(title.text)
        title.words = []
        for i in range(0, len(words)):
            title.words.append(Word(words[i].form, words[i].lemma, words[i].pos))
    corpus.save(os.path.splitext(origin)[0] + '_talismane.xml')

def run_talismane_heavy(origin):
    print('[INFO] --- Running run_talismane_heavy')
    print('[INFO] --- Loading corpus')
    corpus = Corpus.load(r'.\output_dump_repo' + os.sep + origin)
    itercount = 0
    iterdisplay = 1000
    iterstep = 1000
    print('[INFO] --- Counting')
    for title_id in corpus.titles:
        itercount += 1
        if itercount == iterdisplay:
            print(itercount, 'titles done.')
            iterdisplay += iterstep
        title = corpus[title_id]
        words = pytalismane.process_string(title.text)
        title.words = []
        for i in range(0, len(words)):
            title.words.append(Word(words[i].form, words[i].lemma, words[i].pos))
    print('[INFO] --- Saving')
    corpus.save(os.path.splitext(origin)[0] + '_talismane.xml')

def make_lexique(origin):
    excel = ExcelFile(name='lexiqueX', mode='w')
    print('[INFO] --- Running make_lexique')
    print('[INFO] --- Loading corpus')
    corpus = Corpus.load(r'.\output_dump_repo' + os.sep + origin)
    itercount = 0
    iterdisplay = 1000
    iterstep = 1000
    print('[INFO] --- Counting')
    lemmas = {}
    for title_id in corpus.titles:
        itercount += 1
        if itercount == iterdisplay:
            print(itercount, 'titles done.')
            iterdisplay += iterstep
        title = corpus[title_id]
        for w in title.words:
            key = w.lemma + '_' + w.pos
            if key not in lemmas:
                lemmas[key] = [w.lemma, w.pos, 1]
            else:
                lemmas[key][2] += 1
    print('[INFO] --- Saving')
    excel.save_to_sheet_mul(
        name = 'LEMME | POS | NB',
        values = lemmas,
        order_col = 2,
        reverse_order = True,
        percent_col = 2)
    excel.close()


def produce_antconc_files(origin):
    print('[INFO] --- Running produce_antconc_files')
    print('[INFO] --- Loading corpus')
    corpus = Corpus.load(r'.\output_dump_repo' + os.sep + origin)
    itercount = 0
    iterdisplay = 1000
    iterstep = 1000
    outfile = open(r'.\output_dump_repo' + os.sep + 'corpus_antconc.txt', mode='w', encoding='utf8')
    print('[INFO] --- Processing')
    for title_id in corpus.titles:
        itercount += 1
        if itercount == iterdisplay:
            print(itercount, 'titles done.')
            iterdisplay += iterstep
        title = corpus[title_id]
        outfile.write(title.text + '\n')
    print('[INFO] --- Saving')
    outfile.close()


def find_examples(corpus, start=':', after=5, rule=''):
    excel = ExcelFile(name='examples_' + rule.replace('|', '_'), mode='w')
    print('[INFO] --- Running produce_antconc_files')
    print('[INFO] --- Loading corpus')
    itercount = 0
    iterdisplay = 1000
    iterstep = 1000
    examples = {}
    count = 0
    print('[INFO] --- Processing')
    for title_id in corpus.titles:
        itercount += 1
        if itercount == iterdisplay:
            print(itercount, 'titles done.')
            iterdisplay += iterstep
        title = corpus[title_id]
        key = '' # we are going to make a key pos1|pos2|pos3...
        forms = ''
        lemmas = ''
        found = False
        nb = 0
        for w in title.words:
            if found == False and w.form != start:
                continue
            if found == False:
                found = True
                continue # do not take the start symbol into the key
            key += w.pos + '|'
            lemmas += w.lemma + '|'
            forms += w.form + '|'
            nb += 1
            if nb == after:
                break
        if found:
            if nb < after:
                key += '-|' * (after - nb) # complete to have keys of the same size
                lemmas += '-|' * (after - nb)
                forms += '-|' * (after - nb)
            key = key[:-1]
            lemmas = lemmas[:-1]
            forms = forms[:-1]
            if key == rule:
                examples[count] = lemmas + '|-----|' + forms
                count += 1
    print('[INFO] --- Saving')
    examples_excel = {}
    for i in range(0, len(examples)):
        examples_excel[i] = examples[i].split('|')
    excel.save_to_sheet_mul(
        name = 'EXAMPLES',
        values = examples_excel)
    excel.close()


#-------------------------------------------------------------------------------
# Iterative functions
# These functions must be used with iterate to work:
# - last_index_of_the_second_NC_NPP
# - stats_after_word
#-------------------------------------------------------------------------------

# we consider the block of NC/NPP like ONE occurence !
def last_index_of_the_second_NC_NPP(title, data_sets, **parameters):
    if "LENGTHS" not in data_sets:
        data_sets["LENGTHS"] = {}
    if "INDEXES_1" not in data_sets:
        data_sets["INDEXES_1"] = {}
    if "INDEXES_2" not in data_sets:
        data_sets["INDEXES_2"] = {}
    if "LAST_1" not in data_sets:
        data_sets["LAST_1"] = {}
    if "LAST_2" not in data_sets:
        data_sets["LAST_2"] = {}
    nb = 0              # How many NC/NPP (we want 2 maximum)
    start = 0           # Last starting index of NC/NPP
    length = 0          # Length of the current NC/NPP
    started = False     # In an NC/NPP suite?
    save = False
    for count in range(len(title.words)):
        w = title.words[count]
        if w.pos in ['NC', 'NPP']:
            if not started: # start an NC/NPP suite
                started = True
                length = 1
                start = count
            elif started: # in an NC/NPP suite
                length += 1
        else:
            if started: # exit an NC/NPP suite
                started = False
                nb += 1
                save = True
        # if this is the last iteration and we are in an NC/NPP, we must save!
        if started and count == len(title.words) - 1:
            nb += 1
            save = True
        # Saving info
        if save:
            if length in data_sets["LENGTHS"]: # we store the length of the suites
                data_sets["LENGTHS"][length][1] += 1
            else:
                data_sets["LENGTHS"][length] = [length, 1]
            key = "INDEXES_" + str(nb)
            #print(start, title.text)
            if start in data_sets[key]: # we store the starting index of the NC/NPP suite found
                data_sets[key][start][1] += 1
            else:
                data_sets[key][start] = [start, 1]
            key = "LAST_" + str(nb)
            if start + length in data_sets[key]: # we store the last index of the NC/NPP suite found
                data_sets[key][start + length][1] += 1
            else:
                data_sets[key][start + length] = [start + length, 1]
            save = False
            if nb == 2:
                break
    if nb < 2: # handling the titles where there is not 2 NC/NPP suites
        key = "INDEXES_" + str(nb + 1) # we will increment the key -1 in INDEXES_1 if 0 or INDEXES_2 if 1
        if -1 in data_sets[key]:
            data_sets[key][-1][1] += 1
        else:
            data_sets[key][-1] = [-1, 1]


def corpus2excel(title, data_sets, **parameters):
    """Translate a corpus (XML, my format) to an Excel file with 3 tabs:
        - TITLES : metadata + text
        - POS    : id + suite of POS
        - LEMMA  : id + suite of LEMME
        A given title is on the same line at the start.
    """
    # parameters
    if 'after' in parameters:
        after = parameters['after']
        if 'form' in parameters:
            form = parameters['form']
        else: raise Exception('After parameter needs a form')
    else:
        raise Exception('Should be user with after parameter')
    # data set
    titles = "TITLES"
    lemma = "LEMMA after" if after else "LEMMA"
    pos = "POS after" if after else "POS"
    if titles not in data_sets:
        data_sets[titles] = {}
    elif len(data_sets[titles]) == corpus2excel.MAX_TITLE_EXCEL:
        return
    if lemma not in data_sets:
        data_sets[lemma] = {}
    if pos not in data_sets:
        data_sets[pos] = {}
    # algorithm
    # 1. pos & lemma
    list_pos = [title.docid]
    list_lemma = [title.docid]
    save = False if not after else True
    for w in title.words:
        if save:
            list_pos.append(w.pos)
            list_lemma.append(w.lemma)
        elif w.form == form:
            save = True
    # 2. domain
    roots = {
        'shs' : 0, 'sdv' : 0, 'sdu' : 0, 'info' : 0, 'scco' : 0,
        'phys' : 0, 'spi' : 0, 'sde' : 0, 'math' : 0, 'chim' : 0,
        'stat' : 0, 'qfin' : 0, 'nlin' : 0, 'phys-atom ' : 0,
        'electromag' : 0, 'photon' : 0, 'other' : 0, 'image' : 0,
        'stic' : 0
    }
    for d in title.domains:
        if d.startswith('0.'):
            name = d[len('0.'):]
            if name not in roots:
                raise Exception("Unknown domain:" + name)
            roots[name] = 1
    # 3. save
    data_sets[titles][title.docid] = [
        title.docid,
        title.kind,
        len(title.authors),
        title.date,
        *roots.values(),
        title.text
    ]
    data_sets[pos][title.docid] = list_pos
    data_sets[lemma][title.docid] = list_lemma
corpus2excel.MAX_TITLE_EXCEL = 60000


# From a translation corpus2excel, this function has derivated into a pattern filtering machine
def corpus2excel_pattern(title, data_sets, **parameters):
    # parameters
    pattern = parameters['pattern']
    name = parameters['name']
    # data set
    if "TITLES" not in data_sets:
        data_sets["TITLES"] = {}
    if "LEMMA after" not in data_sets:
        data_sets["LEMMA after"] = {}
    if "POS after" not in data_sets:
        data_sets["POS after"] = {}
    if "MATCH after" not in data_sets:
        data_sets["MATCH after"] = {}
    if "STATS N1 after" not in data_sets:
        data_sets["STATS N1 after"] = {}
    if "STATS P after" not in data_sets:
        data_sets["STATS P after"] = {}
    if "STATS N2 after" not in data_sets:
        data_sets["STATS N2 after"] = {}
    if "STATS N1 N2" not in data_sets:
        data_sets["STATS N1 N2"] = {}
    if 'MATRIX' not in data_sets:
        data_sets['MATRIX'] = DynMatrix('matrix_' + name)
    # algorithm
    forms, lemma, pos = pattern.trilist(title.words, after=':')
    res = pattern.match_one(pos)
    if res is not None:
        data_sets["MATCH after"][title.docid] = [
            title.docid,
            len(res),
            *res
        ]
        # stats on pattern
        nb = 0
        inside = False
        suite = []
        n1 = None
        n2 = None
        for i in range(len(pos) + 1):
            if i < len(pos):
                p = pos[i]
            else:
                p = 'STOP'
            if p == 'NC':
                if inside:
                    if lemma[i] != '_':
                        suite.append(lemma[i])
                    else:
                        suite.append(forms[i])
                else:
                    if lemma[i] != '_':
                        suite = [lemma[i]]
                    else:
                        suite = [forms[i]]
                    inside = True
            else:
                if inside:
                    if nb == 0:
                        save = "STATS N1 after"
                        n1 = ' + '.join(suite)
                        nb += 1
                    elif nb == 1:
                        save = "STATS N2 after"
                        n2 = ' + '.join(suite)
                        # stats for n1 + n2
                        nkey = '1. ' + n1 + ' 2. ' + n2
                        if nkey not in data_sets["STATS N1 N2"]:
                            data_sets["STATS N1 N2"][nkey] = [nkey, 1]
                        else:
                            data_sets["STATS N1 N2"][nkey][1] += 1
                        data_sets['MATRIX'].add(n1, n2)
                    tsuite = tuple(suite)
                    if tsuite not in data_sets[save]:
                        data_sets[save][tsuite] = [0, *suite]
                    data_sets[save][tsuite][0] += 1
                    inside = False       
                if p in ['P+D', 'P']:
                    lemme = lemma[i]
                    if lemme not in data_sets["STATS P after"]:
                        data_sets["STATS P after"][lemma[i]] = [0, lemme]
                    data_sets["STATS P after"][lemme][0] += 1
    else:
        return
    roots = {
        'shs' : 0, 'sdv' : 0, 'sdu' : 0, 'info' : 0, 'scco' : 0,
        'phys' : 0, 'spi' : 0, 'sde' : 0, 'math' : 0, 'chim' : 0,
        'stat' : 0, 'qfin' : 0, 'nlin' : 0, 'phys-atom ' : 0,
        'electromag' : 0, 'photon' : 0, 'other' : 0, 'image' : 0,
        'stic' : 0
    }
    for d in title.domains:
        if d.startswith('0.'):
            name = d[len('0.'):]
            if name not in roots:
                raise Exception("Unknown domain:" + name)
            roots[name] = 1
    roots_style = []
    for roo in roots:
        roots_style.append(MiniCell(roots[roo], w=2))
    data_sets["TITLES"][title.docid] = [
        title.docid,
        title.kind,
        len(title.authors),
        title.date,
        *roots_style,
        title.text
    ]
    # Special for after ":" save
    pos_style = []
    for i in range(len(pos)):
        if i < len(res):
            pos_style.append(MiniCell(pos[i], bg = MiniCell.yellow))
        else:
            pos_style.append(pos[i])
    lemma_style = []
    for i in range(len(pos)):
        if i < len(res):
            lemma_style.append(MiniCell(lemma[i], MiniCell.yellow))
        else:
            lemma_style.append(lemma[i])
    data_sets["POS after"][title.docid] = [title.docid, len(pos)] + pos_style
    data_sets["LEMMA after"][title.docid] = [title.docid, len(lemma)] + lemma_style 


def post_process(excelfile):
    return


def stats_after_word(title, data_sets, **parameters):
    # data_set
    pos_lengths = "POS LENGTHS lengths | occ"
    pos_combi = "POS id | length | nb occ | combi..."
    pos_titles = "TITLES id_pos | id_titles..."
    if pos_lengths not in data_sets: data_sets[pos_lengths] = {}
    if pos_combi not in data_sets: data_sets[pos_combi] = {}
    if pos_titles not in data_sets: data_sets[pos_titles] = {}
    # parameters
    limit = parameters['limit'] if 'limit' in parameters else None
    start = parameters['start']
    # algorithm
    key = []
    found = False
    length = 0
    for w in title.words:
        if found == False and w.form != start:
            continue
        if found == False:
            found = True
            continue # do not take the start symbol into the key
        key.append(w.pos)
        length += 1
        if limit is not None and length == limit:
            break
    if found:
        tkey = tuple(key)
        if tkey not in data_sets[pos_combi]:
            stats_after_word.id_rule += 1
            data_sets[pos_combi][tkey] = [stats_after_word.id_rule, length, 1, *tkey]
            data_sets[pos_titles][tkey] = [stats_after_word.id_rule, title.docid]
        else:
            data_sets[pos_combi][tkey][2] += 1
            data_sets[pos_titles][tkey].append(title.docid)
        if length not in data_sets[pos_lengths]:
            data_sets[pos_lengths][length] = [length, 1]
        else:
            data_sets[pos_lengths][length][1] += 1
stats_after_word.id_rule = 0


import gc
# Iterate through the corpus with a function
# name : name of the excel file
# fun : a special function to call on the Excel file
def iterate(corpus, function, excel=False, **parameters):
    print('[INFO] RUN ' + function.__name__)
    print('[INFO] --- Loading corpus')
    itercount = 0
    iterdisplay = 1000
    iterstep = 1000
    data_sets = {}
    print('[INFO] --- Processing')
    for title_id in corpus.titles:
        itercount += 1
        if itercount == iterdisplay:
            print(itercount, 'titles done.')
            iterdisplay += iterstep
        title = corpus[title_id]
        function(title, data_sets, **parameters)
    if excel:
        if 'name' in parameters:
            name = parameters['name']
        else:
            name = function.__name__
        print('[INFO] --- Saving to', name + '.xlsx')
        try:
            excel = ExcelFile(name = name, mode = 'w')
            dynmatrix = None
            to_delete = []
            for key, val in data_sets.items():
                if isinstance(val, DynMatrix): # hack
                    dynmatrix = val
                    continue
                excel.save_to_sheet(
                    name = key[:31],
                    values = val)
                to_delete.append(key)
            if 'fun' in parameters:
                parameters['fun'](excel)
            excel.close()
            if dynmatrix is not None:
                # release memory
                del excel
                for key in to_delete:
                    del data_sets[key]
                #for key, val in data_sets.items():
                #    if isinstance(val, DynMatrix):
                #
                done = False
                threshold = 10 # 5 => Out of Memory
                step = 5
                while not done:
                    try:
                        gc.collect()
                        dynmatrix.filter(threshold)
                        dynmatrix.to_excel(decorated=True)
                        done = True
                    except MemoryError:
                        threshold += step
        except MemoryError:
            print('[ERROR] Out of Memory.')
    print('[INFO] END ' + function.__name__)
    return data_sets


#
# Pattern matching
#

def match_patterns(filename, pattern):
    try:
        data = ExcelFile(filename, 'r')
    except FileNotFoundError:
        print("[WARN] File not found. Action aborted.")
        return
    pos = data.load_sheet("POS = nb occ | id | combi...", key=1, ignore=[0])
    titles = data.load_sheet("TITLES")
    nb_titles = 0
    for key, val in titles.items():
        nb_titles += len(val)
    # match pattern
    matched, unmatched = pattern.match(pos)
    # save results
    nb_title_matched = 0
    for key in matched:
        nb_title_matched += len(titles[key])
    print("Pattern :", pattern)
    print(f"   Possibilities = {pattern.possibilities}")
    print(f"   Longuest = {pattern.max_length}")
    print(f"   Shortest = {pattern.min_length}")
    print("Matched rules:", len(matched), "/", len(pos), "(", f"{len(matched)/len(pos)*100:.2f}",")")
    print("Unmatched rules:", len(unmatched), "/", len(pos), "(", f"{len(unmatched)/len(pos)*100:.2f}", ")")
    print("Matched titles:", nb_title_matched, "/", nb_titles, "(", f"{nb_title_matched/nb_titles*100:.2f}", ")")
    results = ExcelFile('patron_results', mode='w')
    results.save_to_sheet_mul(
        name = "PATTERN",
        values = {'Patron' : [str(pattern)]})
    results.save_to_sheet_mul(
        name = "EXTENDED id | length | ...",
        values = pattern.extended_by_length(),
        order_col = 1,
        reverse_order = False)
    def save(data, name):
        data_dict = {}
        for key in data:
            data_dict[key] = [key, len(pos[key]), *(pos[key])]
        results.save_to_sheet_mul(
            name = name,
            values = data_dict,
            order_col = 1, # by length
            reverse_order = False) # asc
    save(matched, 'MATCHED nb occ | length | ...')
    save(unmatched, 'UNMATCHED nb occ | length | ...')
    results.save()

      
class Application:    

    def __init__(self):
        self.corpus = None
        self.debug = False
        
    def start(self, *actions):
        start_time = datetime.datetime.now()
        print('[INFO] RUN -------------------------------------------------------\n')
        print('[INFO] --- Started at', start_time, '\n')
        #origin = r'.\corpus\corpus_6\corpus_6.xml'
        #origin = r'.\corpus\corpus_medium\corpus_medium.xml'
        #origin = r'.\corpus\corpus_1dblcolno0inf30\corpus_1dblcolno0inf30.xml'
        #origin = r'.\corpus\corpus_big\corpus_big.xml'
        for nb_action in range(len(actions)):
            action = actions[nb_action]
            print("[INFO] ACT ACTION", nb_action + 1, "/", len(actions), ":", action)
            self.execute(action)
            print("[INFO] END ACTION\n")
        print('\n[INFO] --- Ending at', datetime.datetime.now())
        delta = datetime.datetime.now() - start_time
        print(f"[INFO] --- Script has ended [{delta} elapsed].\n")
        print('[INFO] END -------------------------------------------------------')

    def execute(self, action):
        # Actions
        if action == 1:
            filter_zero_words_duplicates_title()
        elif action == 2:
            count_by_domain()
        elif action == 3:
            convert_to_new_format()
            save_dont_mess('mini_dump.xml') # mini_dump_converted.xml
            run_talismane('mini_dump_same.xml')
        elif action == 4:
            run_talismane_heavy('corpus.xml')
        elif action == 5:
            make_lexique('mini_corpus_talismane.xml')
            make_lexique('corpus_talismane.xml')
        elif action == 6:
            produce_antconc_files('corpus_talismane.xml')
        elif action == 8:
            find_examples(corpus, rule='DET|NC|P|DET|NC')
        elif action == 12:
            # Compter où est la dernière suite NC/NPP
            iterate(corpus, last_index_of_the_second_NC_NPP, True)
        # NEW ACTIONS
        elif action.startswith('load_excel?'):
            filename = action[len('load_excel?'):]
            print(filename)
            data = ExcelFile(filename, mode='r')
            titles = data.load_sheet(0)
            
        elif action.startswith('load?'):
            origin = action[len('load?'):]
            try:
                self.corpus = Corpus.load('.\\corpus\\' + origin + '\\' + origin + '.xml')
            except FileNotFoundError:
                self.corpus = Corpus.load(origin + '.xml')
        elif action == 'make?corpus_1dblcolno0inf30': # only one ':', 0 < nb word after ':' < 30
            sub = self.corpus.extract(has_only_one_form, ':')
            sub = sub.extract(has_x_after_form, ':', 0, '!=')
            sub = sub.extract(has_x_after_form, ':', 30, '<')
            sub.save('corpus_1dblcolno0inf30.xml')
            # check
            print()
            count(self.corpus, ':') # should be 100% with 1
            print()
            count_after_word(self.corpus, ':') # should be between 1 and 29
        elif action.startswith('filter_corpus?'):
            parameters = action[len('filter_corpus?'):]
            parameters = parameters.split('&')
            for par in parameters:
                var, val = par.split('=')
                print(var, val)
                sub = self.corpus.extract(has_domain, val)
                sub.save('corpus_' + var + '_' + val + '.xml')
        elif action.startswith('stats_after_word?'):
            form = action[len('stats_after_word?'):]
            iterate(self.corpus, stats_after_word, excel = True, start = form)
        elif action == 'match_pattern':
            pattern = Pattern('DET? ADJ? [NC NPP] [NC NPP]? ADJ? [(P DET?) P+D] ADJ? [NC NPP] [NC NPP]? ADJ?')
            match_patterns('stats_after_word.xlsx', pattern)
        elif action.startswith('corpus2excel_pattern?'):
            if self.corpus is None: raise Exception('[ERROR] A corpus should be loaded first!')
            pattern = Pattern('DET? ADJ? [NC NPP] [NC NPP]? ADJ? [(P DET?) P+D] ADJ? [NC NPP] [NC NPP]? ADJ?')
            name = action[len('corpus2excel_pattern?'):]
            iterate(self.corpus, corpus2excel_pattern, excel = True, name = name, fun = post_process, pattern = pattern)
        elif action.startswith('corpus2excel?'):
            if self.corpus is None: raise Exception('[ERROR] A corpus should be loaded first!')
            name = action[len('corpus2excel?'):]
            iterate(self.corpus, corpus2excel, excel = True, name = name, after = True, form = ':')
        elif action == 'repl':
            cmd = ''
            while cmd != 'exit':
                cmd = input('>>> ')
                print(cmd)
                self.exec_cmd(cmd)
    
    def exec_cmd(self, cmd):
        try:
            if cmd == 'debug':
                self.debug = not self.debug
                print('Debug is', self.debug)
            elif cmd.startswith('find '):
                pattern = Pattern(cmd[len('find '):])
                if self.debug:
                    for ex in pattern.extended:
                        print(ex)
                title, start, extended_form_matched = pattern.find_one(self.corpus)
                if title is not None:
                    print('At least one title found for pattern:')
                    print(pattern)
                    print('Matched extended form:')
                    print(extended_form_matched)
                    print('Starting at:')
                    print(start)
                    print('Title:')
                    print(title)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    app = Application()

    # Corpus 2 Corpus with filtering
    app.start('load?corpus_1dblcolno0inf30', 'filter_corpus?domain=shs')
    #app.start('make?corpus_1dblcolno0inf30')
    
    # Corpus 2 Excel without filtering
    #app.start('load?corpus_1dblcolno0inf30', 'corpus2excel?1dblcolno0inf30')

    # Corpus 2 Excel with Pattern filtering
    #app.start('load?corpus_medium', 'corpus2excel_pattern?medium')                     # For test
    #app.start('load?corpus_1dblcolno0inf30', 'corpus2excel_pattern?1dblcolno0inf30')   # Slow ~13-20 minutes

    # Corpus 2 Stats and eventually match_pattern
    #app.start('load?corpus_1dblcolno0inf30', 'stats_after_word?:')
    #app.start('load?corpus_1dblcolno0inf30', 'stats_after_word?:', 'match_pattern', 'stat_pattern')

    # Simple REPL
    #app.start('load?corpus_1dblcolno0inf30', 'repl')

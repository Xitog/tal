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
from titles import Word, Title, Corpus, has_only_one_form, no_filter, has_x_after_form, has_domain, has_not_domain
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
            after = 0
            for i in range(last + 1, len(title.words)):
                if title.words[i].pos != "PONCT":
                    after += 1
            #after = len(title.words) - last - 1
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
    excel.save_to_sheet(
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
    excel.save_to_sheet(
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

# count also before and after ":"
def make_lexique(corpus):
    excel = ExcelFile(name='lexiqueX', mode='w')
    print('[INFO] --- Running make_lexique')
    print('[INFO] --- Loading corpus')
    #corpus = Corpus.load(r'.\output_dump_repo' + os.sep + origin)
    itercount = 0
    iterdisplay = 1000
    iterstep = 1000
    print('[INFO] --- Counting')
    lemmas = {}
    lemmas_before = {}
    lemmas_after = {}
    for title_id in corpus.titles:
        itercount += 1
        if itercount == iterdisplay:
            print(itercount, 'titles done.')
            iterdisplay += iterstep
        title = corpus[title_id]
        after = False
        for w in title.words:
            if w.lemma == '_': # handling of word without lemme
                lemme = w.form
            else:
                lemme = w.lemma
            if w.form == ':':
                after = True
            key = lemme + '_' + w.pos # handling of word withe same lemme but different POS
            if key not in lemmas:
                lemmas[key] = [lemme, w.pos, 1]
            else:
                lemmas[key][2] += 1
            if after:
                if key not in lemmas_after:
                    lemmas_after[key] = [lemme, w.pos, 1]
                else:
                    lemmas_after[key][2] += 1
            else:
                if key not in lemmas_before:
                    lemmas_before[key] = [lemme, w.pos, 1]
                else:
                    lemmas_before[key][2] += 1                
    print('[INFO] --- Saving')
    to_save = [lemmas, lemmas_before, lemmas_after]
    for data in to_save:
        excel.save_to_sheet(
            name = 'LEMME | POS | NB',
            values = data,
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
    if "STATS N1" not in data_sets:
        data_sets["STATS N1"] = {}
    if "STATS P" not in data_sets:
        data_sets["STATS P"] = {}
    if "STATS N2" not in data_sets:
        data_sets["STATS N2"] = {}
    if "STATS N1 N2" not in data_sets:
        data_sets["STATS N1 N2"] = {}
    if "STATS N1 P" not in data_sets:
        data_sets["STATS N1 P"] = {}
    if "STATS N1 P N2" not in data_sets:
        data_sets["STATS N1 P N2"] = {}
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
        nb_prep = 0
        inside = False
        suite = []
        n1 = None
        n2 = None
        prep = None
        for i in range(len(pos) + 1):
            if i < len(pos):
                p = pos[i]
            else:
                p = 'STOP'
            if p in ['NC', 'NPP']:
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
                        save = "STATS N1"
                        n1 = ' + '.join(suite)
                        nb += 1
                    elif nb == 1:
                        save = "STATS N2"
                        n2 = ' + '.join(suite)
                        # stats for n1 + n2
                        nkey = n1 + '|' + n2 #(n1, n2) #'1. ' + n1 + ' 2. ' + n2
                        if nkey not in data_sets["STATS N1 N2"]:
                            data_sets["STATS N1 N2"][nkey] = [n1, n2, 1]
                        else:
                            data_sets["STATS N1 N2"][nkey][-1] += 1
                        npkey = n1 + '|' + prep + '|' + n2 # (n1, prep, n2) #n1 + ' ' + prep + ' ' + n2
                        if npkey not in data_sets["STATS N1 P N2"]:
                            data_sets["STATS N1 P N2"][npkey] = [n1, prep, n2, 1]
                        else:
                            data_sets["STATS N1 P N2"][npkey][-1] += 1
                        data_sets['MATRIX'].add(n1, n2)
                        nb += 1
                    else:
                        nb += 1
                    if nb in [1, 2]:
                        tsuite = tuple(suite)
                        if tsuite not in data_sets[save]:
                            data_sets[save][tsuite] = [0, *suite]
                        data_sets[save][tsuite][0] += 1
                    inside = False       
                if p in ['P+D', 'P']:
                    if n1 is None:
                        print('DOCID:', title.docid)
                        print('TITLE:', title.text)
                        print('FORM:', forms)
                        print('LEMMA:', lemma)
                        print('POS:', pos)
                        print('Match:', res)
                        raise Exception("WTF")
                    if nb_prep == 0:
                        prep = lemma[i]
                        if prep not in data_sets["STATS P"]:
                            data_sets["STATS P"][prep] = [0, prep]
                        data_sets["STATS P"][prep][0] += 1
                        pkey = n1 + '|' + prep # (n1, prep) # n1 + ' ' + prep
                        if pkey not in data_sets["STATS N1 P"]:
                            data_sets["STATS N1 P"][pkey] = [n1, prep, 0]
                        data_sets["STATS N1 P"][pkey][-1] += 1
                        nb_prep += 1
    else:
        return
    roots = {
        'shs' : 0, 'sdv' : 0, 'sdu' : 0, 'info' : 0, 'scco' : 0,
        'phys' : 0, 'spi' : 0, 'sde' : 0, 'math' : 0, 'chim' : 0,
        'stat' : 0, 'qfin' : 0, 'nlin' : 0, 'phys-atom' : 0,
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
    form_stop = parameters['form_stop'].split(',') if 'form_stop' in parameters else None
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
        if form_stop is not None and w.form in form_stop:
            break
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


def stats_count(title, data_sets, **parameters):
    # data_set
    kind = 'TYPE'
    year = 'YEAR'
    length = 'LENGTH'
    domain = 'DOMAIN'
    authors = 'AUTHORS'
    specials = 'SPECIALS'
    sentence = 'SENTENCE'
    specials_nb = 'SPECIALS_NB'
    specials_end = 'SPECIALS_END'
    segmentation = 'SEGMENTATION'
    nbauth_length = 'AUTHORS LENGTH'
    sentence_domain = 'SENTENCE DOMAIN'
    if kind not in data_sets: data_sets[kind] = {}
    if year not in data_sets: data_sets[year] = {}
    if length not in data_sets: data_sets[length] = {}
    if domain not in data_sets: data_sets[domain] = {}
    if authors not in data_sets: data_sets[authors] = {}
    if specials not in data_sets: data_sets[specials] = {'?' : ['?', 0], '!' : ['!', 0], '«' : ['«', 0], '»' : ['»', 0], '"' : ['"', 0], ':' : [':', 0], ';' : [';', 0], '.' : ['.', 0], '“' : ['“', 0], '”' : ['”', 0] }
    if specials_nb not in data_sets: data_sets[specials_nb] = {}
    if specials_end not in data_sets: data_sets[specials_end] = {'?' : ['?', 0], '!' : ['!', 0], '«' : ['«', 0], '»' : ['»', 0], '"' : ['"', 0], ':' : [':', 0], ';' : [';', 0], '.' : ['.', 0], '“' : ['“', 0], '”' : ['”', 0] }
    if sentence not in data_sets: data_sets[sentence] = {'oui' : ['oui', 0], 'non' : ['non', 0]}
    if segmentation not in data_sets: data_sets[segmentation] = {}
    if nbauth_length not in data_sets: data_sets[nbauth_length] = {}
    if sentence_domain not in data_sets: data_sets[sentence_domain] = {}
    # no parameters
    # algorithm
    # date
    if title.date not in data_sets[year]:
        data_sets[year][title.date] = [title.date, 1]
    else:
        data_sets[year][title.date][1] += 1
    # kind
    if title.kind not in data_sets[kind]:
        data_sets[kind][title.kind] = [title.kind, 1]
    else:
        data_sets[kind][title.kind][1] += 1
    # length
    nb = 0
    for w in title.words:
        if w.pos != 'PONCT':
            nb += 1
    if nb not in data_sets[length]:
        data_sets[length][nb] = [nb, 1]
    else:
        data_sets[length][nb][1] += 1
    # domains
    domains = []
    for d in title.domains:
        if d.startswith('0.'):
            dom = d[len('0.'):]
            domains.append(dom)
            if dom not in data_sets[domain]:
                data_sets[domain][dom] = [dom, 1]
            else:
                data_sets[domain][dom][1] += 1
    # sentence
    has_verb = False
    for w in title.words:
        if w.pos in ['VS', 'V', 'VIMP']:
            has_verb = True
            break
    if has_verb:
        data_sets[sentence]['oui'][1] += 1
    else:
        data_sets[sentence]['non'][1] += 1
    #if has_verb:
    #    print('Sentence:', title.text)
    # nb authors
    if len(title.authors) not in data_sets[authors]:
        data_sets[authors][len(title.authors)] = [len(title.authors), 1]
    else:
        data_sets[authors][len(title.authors)][1] += 1
    # segmentation
    title.text = title.text.replace('...', '…')
    nb_segment = title.text.count(':')
    nb_segment += title.text.count(';')
    nb_segment += title.text.count('.')
    nb_segment += title.text.count('?')
    nb_segment += title.text.count('!')
    nb_segment += title.text.count('…')
    if title.text[-1] not in [':', ';', '.', '?', '!', '…']:
        nb_segment += 1
    if nb_segment not in data_sets[segmentation]:
        data_sets[segmentation][nb_segment] = [nb_segment, 1]
    else:
        data_sets[segmentation][nb_segment][1] += 1
    #if nb_segment > 2:
    #    print(nb_segment, title.text)
    # nb authors & length
    key = (len(title.authors), len(title.words))
    if key not in data_sets[nbauth_length]:
        data_sets[nbauth_length][key] = [len(title.authors), len(title.words), 1]
    else:
        data_sets[nbauth_length][key][2] += 1

    if title.words[-1].form in data_sets[specials_end]:
        data_sets[specials_end][title.words[-1].form][1] += 1
    #  special chars : nb of titles with and special chars count
    spe = {'?' : 0, '!' : 0, '«' : 0, '»' : 0, '"' : 0, ':' : 0, ';' : 0, '.' : 0, '“' : 0, '”' : 0 }
    for special_char in spe:
        spe[special_char] += title.text.count(special_char)
        #if special_char == ':' and spe[special_char] > 1:
        #    raise Exception(str(spe[special_char]) + ' >>> ' + title.text + ' >>> ' + str(title.words))
        if spe[special_char] > 0:
            data_sets[specials][special_char][1] += 1
        spe_key = (special_char, spe[special_char])
        if spe_key not in data_sets[specials_nb]:
            data_sets[specials_nb][spe_key] = [special_char, spe[special_char], 1]
        else:
            data_sets[specials_nb][spe_key][2] +=1
    # sentence and domain
    if has_verb:
        for d in domains:
            if d not in data_sets[sentence_domain]:
                data_sets[sentence_domain][d] = [d, 1]
            else:
                data_sets[sentence_domain][d][1] += 1


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
    if not excel:
        print()
        for key, val in data_sets.items():
            print('===', key, '=== [', len(val), ']')
            for value, row in val.items():
                for cell in row:
                    print(f"{str(cell):6}", end='')
                print()
            print()
    else:
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
                order_col = 0
                if 'divide' in parameters and 'name2' in parameters: # make multiple excel
                    if key == parameters['divide']:
                        excel.close()
                        excel = ExcelFile(name = parameters['name2'], mode = 'w')
                if isinstance(val, DynMatrix): # hack
                    dynmatrix = val
                    continue
                #    threshold = 5 #1
                #    val.filter(threshold)
                #    #val.to_excel(decorated=True)
                #    val = val.matrix
                #    order_col = None
                #try:
                excel.save_to_sheet(
                    name = key[:31],
                    values = val,
                    order_col = order_col)
                #except TypeError:
                #    print(key)
                #    print('Type:', type(val))
                #    print('Length:', len(val))
                #    for key, val in val.items():
                #        print('Key: ', key, ' = ', end='')
                #        for cell in val:
                #            print(cell, '  ', end='')
                #            if cell is None:
                #                raise Exception("NONE DETECTED")
                #        print()
                to_delete.append(key)
            if 'fun' in parameters:
                parameters['fun'](excel)
            excel.close()
            if dynmatrix is not None:
                # release memory
                del excel
                for key in to_delete:
                    del data_sets[key]
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

def match_patterns(filename, pattern, code):
    try:
        data = ExcelFile(filename, 'r')
    except FileNotFoundError:
        print("[WARN] File not found. Action aborted.")
        return
    pos = data.load_sheet("POS id | length | nb occ | comb", key=0, ignore=[0, 1, 2])
    titles = data.load_sheet("TITLES id_pos | id_titles...")
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
    results = ExcelFile(code + '_patron_results', mode='w')
    results.save_to_sheet(
        name = "PATTERN",
        values = {'Patron' : [str(pattern)]})
    results.save_to_sheet(
        name = "EXTENDED id | length | ...",
        values = pattern.extended_by_length(),
        order_col = 1,
        reverse_order = False)
    def save(data, name):
        data_dict = {}
        for key in data:
            data_dict[key] = [key, len(pos[key]), *(pos[key])]
        results.save_to_sheet(
            name = name,
            values = data_dict,
            order_col = 1, # by length
            reverse_order = False) # asc
    save(matched, 'MATCHED nb occ | length | ...')
    save(unmatched, 'UNMATCHED nb occ | length | ...')
    results.close()
    del data

      
class Application:    

    # 3456 poss, length= 3 <= x <= 11
    patterns = {
        'sn_v1' : 'DET? ADJ? [NC NPP] [NC NPP]? ADJ? [(P DET?) P+D] ADJ? [NC NPP] [NC NPP]? ADJ?',
        'sn_v2' : '[DETWH DET]? ADJ? [NC NPP] [NC NPP]? [(ADV ADJ) ADJ (ADJ ADV)]? [(P DET?) P+D] ADJ? [NC NPP] [NC NPP]? ADJ?',
        'sp_v1' : '[P+D P] DET? ADJ? [NC NPP] [NC NPP]? ADJ? [(P DET?) P+D] ADJ? [NC NPP] [NC NPP]? ADJ?',
        'cc_v1' : '[NC NPP] CC NC',
        'cc_v2' : '[DET DETWH]? ADJ? [NC NPP] [NC NPP]? ADJ? CC DET? ADJ? [NC NPP] [NC NPP]?'
    }
    
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
        #
        # NEW ACTIONS
        #
        #   load_excel? filename
        elif action.startswith('load_excel?'):
            filename = action[len('load_excel?'):]
            print(filename)
            data = ExcelFile(filename, mode='r')
            titles = data.load_sheet(0)
        #   load? filename
        elif action.startswith('load?'):
            origin = action[len('load?'):]
            try:
                self.corpus = Corpus.load('.\\corpus\\' + origin + '\\' + origin + '.xml')
            except FileNotFoundError:
                self.corpus = Corpus.load(origin + '.xml')
        #   count   (count a corpus)
        elif action == 'count':
            print(len(self.corpus))
        #   stats   (make various stats on the corpus)
        elif action == 'stats':
            iterate(self.corpus, stats_count, excel = True, name = 'stats_' + self.corpus.name)
        #   lexique (make the lexique)
        elif action == 'lexique':
            make_lexique(self.corpus)
        #   make? what_to_make (make a corpus from a corpus)
        elif action.startswith('make?'):
            param = action[len('make?'):]
            if param == 'corpus_1dblpt_sup0_inf30': # only one ':', 0 < nb word after ':' < 30
                sub = self.corpus.extract(has_only_one_form, ':')
                sub = sub.extract(has_x_after_form, ':', 0, '!=')
                sub = sub.extract(has_x_after_form, ':', 30, '<')
                sub.save(param + '.xml')
            elif param == 'corpus_1dblpt':
                sub = self.corpus.extract(has_only_one_form, ':')
                sub.save(param + '.xml')
            del self.corpus
            self.corpus = sub
            print()
            count(self.corpus, ':') # should be 100% with 1
            print()
            count_after_word(self.corpus, ':') # should be between 1 and 29
        # filter_corpus? (make a corpus from a corpus)
        elif action.startswith('filter_corpus?'):
            parameters = action[len('filter_corpus?'):]
            parameters = parameters.split('&')
            for par in parameters:
                var, val = par.split('=')
                print(var, val)
                if val[0] == '!':
                    sub = self.corpus.extract(has_not_domain, val[1:])
                else:
                    sub = self.corpus.extract(has_domain, val)
                sub.save('corpus_' + var + '_' + val + '.xml')
        # stats_after_word? form (make an Excel of all the combi of POS after the form)
        elif action.startswith('stats_after_word?'):
            form = action[len('stats_after_word?'):]
            iterate(self.corpus, stats_after_word, excel = True, start = form, form_stop = '.,?,!,;')
        # match_pattern? pattern_name (make an Excel of the matched and unmatched POS combi from a stats_after_word Excel)
        elif action.startswith('match_pattern'):
            code = action[len('match_pattern?'):]
            pattern = Pattern(Application.patterns[code])
            match_patterns('stats_after_word.xlsx', pattern, code)
        # corpus2excel_pattern? filename_output (make an Excel from a corpus filtered through a Pattern)
        elif action.startswith('corpus2excel_pattern?'):
            if self.corpus is None: raise Exception('[ERROR] A corpus should be loaded first!')
            pattern = Pattern(Application.pattern_sn)
            name = action[len('corpus2excel_pattern?'):]
            iterate(self.corpus, corpus2excel_pattern, excel = True, name = name,
                    fun = post_process, pattern = pattern)
                    #fun = post_process, pattern = pattern, divide = 'STATS N1', name2 = name + '_stat') # divide into 2 files : titles + stats
        # corpus2excel? filename_output (make an Excel from a corpus)
        elif action.startswith('corpus2excel?'):
            if self.corpus is None: raise Exception('[ERROR] A corpus should be loaded first!')
            name = action[len('corpus2excel?'):]
            iterate(self.corpus, corpus2excel, excel = True, name = name, after = True, form = ':')
        # Start an REPL
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

def actions_make_sub_corpus():
    return ['load?corpus_1dblcolno0inf30',
            'filter_corpus?domain=shs',       # Extracted: 60724 / 84923 1. Sciences de l'Homme et Société (487646)
            'filter_corpus?domain=sdv',       # Extracted: 12233 / 84923 Sciences du Vivant [q-bio] (207100)
            'filter_corpus?domain=sdu',       # Extracted: 1804 / 84923  Planète et Univers [physics] (76471)
            'filter_corpus?domain=info',      # Extracted: 3746 / 84923  Informatique [cs] (210465)
            'filter_corpus?domain=scco',      # Extracted: 1153 / 84923  Sciences cognitives (20938)
            'filter_corpus?domain=phys',      # Extracted: 1709 / 84923  2. Physique [physics] (229921)
            'filter_corpus?domain=spi',       # Extracted: 3796 / 84923  Sciences de l'ingénieur [physics] (181699)
            'filter_corpus?domain=sde',       # Extracted: 3027 / 84923  Sciences de l'environnement (56405)
            'filter_corpus?domain=math',      # Extracted: 747 / 84923   Mathématiques [math] (76696)
            'filter_corpus?domain=chim',      # Extracted: 950 / 84923   Chimie(81098)
            'filter_corpus?domain=stat',      # Extracted: 191 / 84923   Statistiques [stat] (10738)
            'filter_corpus?domain=qfin',      # Extracted: 265 / 84923   Économie et finance quantitative [q-fin] (3527)
            'filter_corpus?domain=nlin',      # Extracted: 19 / 84923    Science non linéaire [physics] (2211)
            'filter_corpus?domain=phys-atom', # Extracted: 0 / 84923
            'filter_corpus?domain=electromag',# Extracted: 0 / 84923
            'filter_corpus?domain=photon',    # Extracted: 0 / 84923
            'filter_corpus?domain=other',     # Extracted: 0 / 84923
            'filter_corpus?domain=image',     # Extracted: 0 / 84923
            'filter_corpus?domain=stic']      # Extracted: 0 / 84923

if __name__ == '__main__':
    app = Application()

    # Choose corpus
    #corpus = 'corpus_1dbl_6'
    #corpus = 'corpus_medium'
    #corpus = 'corpus_big'
    corpus = 'corpus_1dblpt_sup0_inf30'
    
    # Make a corpus with filtering
    #app.start('load?' + corpus, 'make?corpus_1dblpt')
    #app.start('load?' + corpus, 'make?corpus_1dblpt_sup0_inf30')
    #app.start('load?' + corpus, 'filter_corpus?domain=shs', 'filter_corpus?domain=!shs')

    # Make some stats
    #app.start('load?' + corpus, 'count', 'stats')
    #app.start('load?' + corpus, 'stats_after_word?:')
    app.start('load?' + corpus, 'lexique')
    
    # Pattern matching (an stats_after_word.xlsx file is mandatory before match_pattern)
    #app.start('load?' + corpus, 'stats_after_word?:', 'match_pattern')
    #app.start('match_pattern?cc_v2')
    
    # Make an Excel without filtering
    #app.start('load?corpus_1dblcolno0inf30', 'corpus2excel?1dblcolno0inf30')

    # Make an Excel with Pattern filtering
    #app.start('load?corpus_medium', 'corpus2excel_pattern?medium')                     # For test
    #app.start('load?corpus_1dbl_6', 'corpus2excel_pattern?corpus_1dbl_6')              # For test 6 titles and 4 matching the pattern
    #app.start('load?corpus_1dblcolno0inf30', 'corpus2excel_pattern?1dblcolno0inf30')   # Slow ~13-20 minutes
    #app.start('load?corpus_domain_shs', 'corpus2excel_pattern?shs')
    #app.start('load?corpus_domain_!shs', 'corpus2excel_pattern?not_shs')
    
    # Simple REPL
    #app.start('load?corpus_1dblcolno0inf30', 'repl')

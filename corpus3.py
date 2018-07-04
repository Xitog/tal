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
from titles import Word, Title, Corpus, has_only_one_form, no_filter, has_x_after_form
from excel import ExcelFile
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


def count_after(corpus : Corpus, form : str, display=True):
    """Count the number of words after a specific form in the titles. Return a dict:
         { 1 : title with only 1 word after this form,
           2 : title with two words after this form,
           ...
         }
    """
    print('[INFO] RUN count_after')
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
    excel.save()
    zero.close()
    one.close()
    big.close()
    print('[INFO] END count_after')
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
    excel.save()
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
    excel.save()
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
    
    excel.save()

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
    excel.save()


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
    excel.save()


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


def stats_after_word(title, data_sets, **parameters):
    """
        Onglet POS LENGTHS : length | nb
            Ex : 6 | 23
        Onglet POS : nb_occ | id_combi | combi...
            Ex : 1 | 34675 | DET | NC
        Onglet TITLES : id_combi | id...
            Ex : 1 | id23 | id45 | id24 | id87
    """
    # data_set
    if "POS LENGTHS" not in data_sets:
        data_sets["POS LENGTHS"] = {}
    if "POS = nb occ | id | combi..." not in data_sets:
        data_sets["POS = nb occ | id | combi..."] = {}
    if "TITLES" not in data_sets:
        data_sets["TITLES"] = {}
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
        if tkey not in data_sets["POS = nb occ | id | combi..."]:
            stats_after_word.id_rule += 1
            data_sets["POS = nb occ | id | combi..."][tkey] = [1, stats_after_word.id_rule, *tkey]
            data_sets["TITLES"][tkey] = [stats_after_word.id_rule, title.docid]
        else:
            data_sets["POS = nb occ | id | combi..."][tkey][0] += 1
            data_sets["TITLES"][tkey].append(title.docid)
        if length not in data_sets["POS LENGTHS"]:
            data_sets["POS LENGTHS"][length] = [length, 1]
        else:
            data_sets["POS LENGTHS"][length][1] += 1
stats_after_word.id_rule = 0


# Iterate through the corpus with a function
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
    print('[INFO] --- Saving')
    if excel:
        excel = ExcelFile(name = function.__name__, mode='w')
        for key, val in data_sets.items():
            excel.save_to_sheet_mul(
                name = key[:31],
                values = val)
        excel.save()
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


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print('[INFO] RUN -------------------------------------------------------\n')
    print('[INFO] --- Started at', start_time, '\n')
    #origin = r'.\corpus\corpus_6\corpus_6.xml'
    #origin = r'.\corpus\corpus_medium\corpus_medium.xml'
    #origin = r'.\corpus\corpus_1dblcolno0inf30\corpus_1dblcolno0inf30.xml'
    #origin = r'.\corpus\corpus_big\corpus_big.xml'
    ACTIONS = ['load_corpus_1dblcolno0inf30', 'pos_combinaisons', 'match_pattern']
    #ACTIONS = ['match_pattern']
    for nb_action in range(len(ACTIONS)):
        action = ACTIONS[nb_action]
        print("[INFO] ACT ACTION", nb_action + 1, "/", len(ACTIONS), ":", action)
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
        elif action.startswith('load_'):
            origin = action[5:]
            corpus = Corpus.load('.\\corpus\\' + origin + '\\' + origin + '.xml')
        elif action == 'make_corpus_1dblcolno0inf30': # only one ':', 0 < nb word after ':' < 30
            sub = corpus.extract(has_only_one_form, ':')
            sub = sub.extract(has_x_after_form, ':', 0, '!=')
            sub = sub.extract(has_x_after_form, ':', 30, '<')
            sub.save('corpus_1dblcolno0inf30.xml')
            # check
            print()
            count(corpus, ':') # should be 100% with 1
            print()
            count_after(corpus, ':') # should be between 1 and 29
        elif action == 'pos_combinaisons': # after ':'
            iterate(corpus, stats_after_word, excel=True, start=':')
        elif action == 'match_pattern':
            pattern = Pattern('DET? ADJ? [NC NPP] [NC NPP]? ADJ? [(P DET?) P+D] ADJ? [NC NPP] [NC NPP]? ADJ?')
            match_patterns('stats_after_word.xlsx', pattern)
        elif action == 'make_stat':
            make_stat('stats_after_word.xlsx', 'patron_results.xlsx')
        print("[INFO] END ACTION\n")
    # end of actions
    print('\n[INFO] --- Ending at', datetime.datetime.now())
    delta = datetime.datetime.now() - start_time
    print(f"[INFO] --- Script has ended [{delta} elapsed].\n")
    print('[INFO] END -------------------------------------------------------')

    

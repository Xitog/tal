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


def stats_after_word(corpus, start=':', after=None):
    print('[INFO] RUN stats_after_word')
    itercount = 0
    iterdisplay = 1000
    iterstep = 1000
    stats = {}
    print('[INFO] --- Processing')
    for title_id in corpus.titles:
        itercount += 1
        if itercount == iterdisplay:
            print(itercount, 'titles done.')
            iterdisplay += iterstep
        title = corpus[title_id]
        key = '' # we are going to make a key pos1|pos2|pos3...
        found = False
        nb = 0
        for w in title.words:
            if found == False and w.form != start:
                continue
            if found == False:
                found = True
                continue # do not take the start symbol into the key
            key += w.pos + '|'
            nb += 1
            if after is not None and nb == after:
                break
        if found:
            if after is not None and nb < after:
                key += '-|' * (after - nb) # complete to have keys of the same size
            key = key[:-1]
            if key not in stats:
                stats[key] = 1
            else:
                stats[key] += 1
    print('[INFO] --- Saving')
    stats_excel = {}
    for s in stats:
        stats_excel[s] = s.split('|')
        stats_excel[s].insert(0, stats[s])
    excel = ExcelFile(name='stats_after_' + start.replace(':', 'dblcol'), mode='w')
    excel.save_to_sheet_mul(
        name = 'STATS',
        values = stats_excel,
        order_col = 0,
        reverse_order = True,
        percent_col = 0)
    excel.save()
    print('[INFO] END stats_after_word')


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


def get_pattern_after(title, form = ':'):
    pattern = []
    found = False
    for w in title.words:
        if found == False and w.form != form:
            continue
        if found == False:
            found = True
            continue # do not take the start symbol into the pattern
        pattern.append(w.pos)
    return pattern


def pattern_matching(corpus):
    print('[INFO] --- Running pattern_matching')
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
        pattern = get_pattern_after(title)
        print(pattern)
    print('[INFO] --- Saving')


def FUNCTION_NAME(corpus):
    print('[INFO] --- Running FUNCTION_NAME')
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
    print('[INFO] --- Saving')


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print('[INFO] RUN -------------------------------------------------------\n')
    print('[INFO] --- Started at', start_time, '\n')
    #origin = r'.\corpus\corpus_medium\corpus_medium.xml'
    #origin = r'.\corpus\corpus_big\corpus_big.xml'
    origin = r'.\corpus\corpus_1dblcolno0inf30\corpus_1dblcolno0inf30.xml'
    corpus = Corpus.load(origin)
    ACTION = 11
    # Actions
    if ACTION == 1:
        filter_zero_words_duplicates_title()
    elif ACTION == 2:
        count_by_domain()
    elif ACTION == 3:
        convert_to_new_format()
        save_dont_mess('mini_dump.xml') # mini_dump_converted.xml
        run_talismane('mini_dump_same.xml')
    elif ACTION == 4:
        run_talismane_heavy('corpus.xml')
    elif ACTION == 5:
        make_lexique('mini_corpus_talismane.xml')
        make_lexique('corpus_talismane.xml')
    elif ACTION == 6:
        produce_antconc_files('corpus_talismane.xml')
    elif ACTION == 7:
        # All the POS combination 5 after ':'
        stats_after_word(corpus)
    elif ACTION == 8:
        # found example of rule (lemme & form)
        # Ex : DET  NC  P  DET  NC
        find_examples(corpus, rule='DET|NC|P|DET|NC')
    elif ACTION == 9:
        # - count number of titles with ':'
        # - extract the sub corpus of titles with only one ':'
        #print()
        #display(corpus)
        #print()
        #count(corpus, ':')
        print()
        sub = corpus.extract(has_only_one_form, ':')
        sub = sub.extract(has_x_after_form, ':', 0, '!=')
        sub = sub.extract(has_x_after_form, ':', 30, '<')
        sub.save('only_one.xml')
    elif ACTION == 10:
        # Check action of the previous result
        # - count number of titles with ':' (100% = 1)
        # - count after ':'
        print()
        count(corpus, ':')
        print()
        count_after(corpus, ':')
    elif ACTION == 11:
        pattern_matching(corpus)
    # end of actions
    print('\n[INFO] --- Ending at', datetime.datetime.now())
    delta = datetime.datetime.now() - start_time
    print(f"[INFO] --- Script has ended [{delta} elapsed].\n")
    print('[INFO] END -------------------------------------------------------')

    

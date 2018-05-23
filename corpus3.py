#===============================================================================
# Code handling the elaborated corpus for TAL
# Author : Damien Gouteux
# Last updated : 22 May 2018
# Technologies : Python, Excel, XML
#===============================================================================

#-------------------------------------------------------------------------------
# Import
#-------------------------------------------------------------------------------

# standard
import datetime
import xml.etree.ElementTree as ET
import zipfile
import os

# project
from corpus2 import Title, ExcelFile

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

#
# Corpus
#
class Corpus:
    """A corpus is a collection of Title serialized in an xml File.
       Loading of the xml file is iterative: it is too big for reading it directly.
    """
    def __init__(self):
        self.titles = {}

    @staticmethod
    def load(filepath):
        corpus = Corpus()
        start = datetime.datetime.now()
        for event, elem in ET.iterparse(filepath, events=('end',)):
            if event == 'end':
                if elem.tag == 'notice':
                    t = Title.from_xml(elem)
                    corpus.titles[t.docid] = t
                    elem.clear()
        delta = datetime.datetime.now() - start
        print('Nb titles:', len(corpus.titles))
        print(f"Loaded in {delta}.")
        return corpus
    
    # Code taken from Repository.dump
    def save(self, filename, makezip=False):
        full_filename = 'output_dump_repo' + os.sep + filename + '.xml'
        outfile = open(full_filename, encoding='utf-8', mode='w')
        outfile.write('<notices>\n')
        for title_id in self.titles:
            title = self.titles[title_id]
            try:
                outfile.write(title.to_xml())
            except Exception as problem:
                print(problem)
                print(title.title, title_id)
        outfile.write('</notices>')
        outfile.close()
        if makezip:
            out = zipfile.ZipFile('output_dump_repo' + os.sep + filename + '_' + output + '.zip', mode='w')
            out.write(full_filename)
            out.close()

    def __getitem__(self, key):
        return self.titles[key]

    def __setitem__(self, key, val):
        self.titles[key] = val
    
    def __len__(self):
        return len(self.titles)
    
    def add_title(self, t):
        self[t.docid] = t
    
    def count_titles(self):
        return len(self.titles)


def count_by_domain():
    corpus = Corpus.load(r'.\output_dump_repo\dump.xml') #minidump
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

CORPUS = None

def filter_zero_words_duplicates_title():
    global CORPUS
    corpus = Corpus.load(r'.\output_dump_repo\dump.xml') #minidump
    CORPUS = corpus
    key_to_delete = []
    nb_double = 0
    nb_empty = 0
    all_title_text = []
    itercount = 0
    iterdisplay = 1000
    iterstep = 1000
    old_length = len(corpus)
    print('-- Filtering --')
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
    print('-- Saving --')
    print('Origin corpus:', old_length)
    print('Saved corpus is:', len(corpus))
    print('Discarded: empty =', nb_empty, 'double =', nb_double, 'total =', nb_empty + nb_double)
    corpus.save('corpus_filtered')


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

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print('\n----- Starting ------\n')
    print('Started at', start_time)
    # action
    #01
    filter_zero_words_duplicates_title()
    #02
    #count_by_domain()
    # end of action
    print('Ending at', datetime.datetime.now())
    print('\n----- End -----\n')
    delta = datetime.datetime.now() - start_time
    print(f"    Script has ended [{delta} elapsed].")
    

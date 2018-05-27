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
from corpus2 import ExcelFile
import pytalismane
from xml.sax.saxutils import escape, unescape

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

#
# Word
#
class Word:

    def __init__(self, form, lemma, pos):
        self.form = form
        self.lemma = lemma
        self.pos = pos

    #def to_xml(self):
    #    s = '            <word>\n'
    #    s += f'                <form>{escape(self.form)}</form>\n'
    #    s += f'                <lemma>{escape(self.lemma)}</lemma>\n'
    #    s += f'                <pos>{self.pos}</pos>\n'
    #    s += '            </word>\n'
    #    return s

    # minimized version
    def to_xml(self):
        s = f'<word><form>{escape(self.form)}</form><lemma>{escape(self.lemma)}</lemma><pos>{self.pos}</pos></word>\n'
        return s
    
    @staticmethod
    def from_xml(elem):
        form = None
        lemma = ''
        pos = ''
        if len(elem) > 0:
            for child in elem:
                if child.tag == 'form':
                    form = unescape(child.text)
                elif child.tag == 'lemma':
                    if child.text is not None:
                        lemma = unescape(child.text)
                elif child.tag == 'pos':
                    if child.text is not None:
                        pos = child.text
        # compat mode
        else:
            form = elem.text            
        return Word(form, lemma, pos)

    def __str__(self):
        return f'<Word Object form={self.form}, lemma={self.lemma}, pos={self.pos}>'
#
# Title
#
class Title:

    def __init__(self):
        self.docid = None
        self.kind = None
        self.date = None
        self.text = None
        self.words = []
        self.authors = []
        self.domains = []

    def to_xml(self):
        authors_xml = ''
        for a in self.authors:
            #authors_xml += f'            <author>{escape(a)}</author>\n'
            authors_xml += f'<author>{escape(a)}</author>\n'
        domains_xml = ''
        for d in self.domains:
            #domains_xml += f'            <domain>{d}</domain>\n'
            domains_xml += f'<domain>{d}</domain>\n'
        words_xml = ''
        for w in self.words:
            words_xml += w.to_xml()
        data = """<notice>
<id>{0}</id>
<type>{1}</type>
<date>{2}</date>
<text>{3}</text>
<words>\n{4}</words>
<authors>\n{5}</authors>
<domains>\n{6}</domains>
</notice>\n""".format(self.docid, self.kind, self.date, escape(self.text), words_xml, authors_xml, domains_xml)
        return data
        data = """    <notice>
        <id>{0}</id>
        <type>{1}</type>
        <date>{2}</date>
        <text>{3}</text>
        <words>\n{4}        </words>
        <authors>\n{5}        </authors>
        <domains>\n{6}        </domains>
    </notice>\n""".format(self.docid, self.kind, self.date, escape(self.text), words_xml, authors_xml, domains_xml)
        return data

    @staticmethod
    def from_xml(elem):
        t = Title()
        for child in elem:
            if child.tag == 'id':
                t.docid = int(child.text)
            elif child.tag == 'type':
                t.kind = child.text
            elif child.tag == 'date':
                t.date = child.text
            elif child.tag == 'text':
                t.text = unescape(child.text)
            # compat mode
            elif child.tag == 'title':
                t.text = unescape(child.text)
            elif child.tag == 'words':
                for word in child:
                    t.words.append(Word.from_xml(word))
            elif child.tag == 'authors':
                for author in child:
                    t.authors.append(unescape(author.text))
            elif child.tag == 'domains':
                for domain in child:
                    t.domains.append(domain.text)
        return t

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
        print('[INFO] --- Nb titles:', len(corpus.titles))
        print(f"[INFO] --- Loaded in {delta}.")
        return corpus
    
    # Code taken from Repository.dump
    def save(self, filename, makezip=False):
        full_filename = 'output_dump_repo' + os.sep + filename # + '.xml'
        outfile = open(full_filename, encoding='utf-8', mode='w')
        outfile.write('<notices>\n')
        for title_id in self.titles:
            title = self.titles[title_id]
            #try:
            outfile.write(title.to_xml())
            #except Exception as problem:
            #    print(problem)
            #    print(title.text, title_id)
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


def filter_zero_words_duplicates_title():
    corpus = Corpus.load(r'.\output_dump_repo\dump.xml') #minidump
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
            if w.lemma not in lemmas:
                lemmas[w.lemma] = 1
            else:
                lemmas[w.lemma] += 1
    print('[INFO] --- Saving')
    excel.save_to_sheet('LEMMAS | nb', lemmas, len(lemmas))
    excel.save()


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print('[INFO] --- Start -------------------------------------------------\n')
    print('[INFO] --- Started at', start_time)
    # action
    #01
    #filter_zero_words_duplicates_title()
    #02
    count_by_domain()
    #03
    #convert_to_new_format()
    #save_dont_mess('mini_dump.xml') # mini_dump_converted.xml
    #run_talismane('mini_dump_same.xml')
    #04
    #run_talismane_heavy('corpus.xml')
    #05
    #make_lexique('corpus_talismane.xml') #mini_corpus_talismane.xml')
    # end of action
    print('[INFO] --- Ending at', datetime.datetime.now())
    print('\n[INFO] --- End -------------------------------------------------')
    delta = datetime.datetime.now() - start_time
    print(f"[INFO] --- Script has ended [{delta} elapsed].")
    

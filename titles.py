#===============================================================================
# Code handling the title corpus
#-------------------------------------------------------------------------------
# Author : Damien Gouteux
# Last updated : 25 June 2018
# Technologies & Tools : Python, Excel, XML, Talismane
#===============================================================================

#-------------------------------------------------------------------------------
# Import
#-------------------------------------------------------------------------------

from xml.sax.saxutils import escape, unescape
import xml.etree.ElementTree as ET
import datetime
import zipfile
import os

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class Word:

    def __init__(self, form, lemma, pos):
        self.form = form
        self.lemma = lemma
        self.pos = pos
    
    # minimized version
    def to_xml(self, minimize=True):
        if minimize:
            s = f'<word><form>{escape(self.form)}</form><lemma>{escape(self.lemma)}</lemma><pos>{self.pos}</pos></word>\n'
        else:
            s = '            <word>\n'
            s += f'                <form>{escape(self.form)}</form>\n'
            s += f'                <lemma>{escape(self.lemma)}</lemma>\n'
            s += f'                <pos>{self.pos}</pos>\n'
            s += '            </word>\n'
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


class Corpus:
    """A corpus is a collection of Title serialized in an xml File.
       Loading of the xml file is iterative: it is too big for reading it directly.
    """
    def __init__(self):
        self.titles = {}

    @staticmethod
    def load(filepath):
        print('[INFO] RUN Corpus#load')
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
        print('[INFO] END Corpus#load')
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

    def extract(self, filter_function, *parameters):
        print('[INFO] RUN Corpus#extract')
        itercount = 0
        iterdisplay = 1000
        iterstep = 1000
        stats = {}
        sub = Corpus()
        for title_id in self.titles:
            itercount += 1
            if itercount == iterdisplay:
                print(itercount, 'titles done.')
                iterdisplay += iterstep
            title = self[title_id]
            if filter_function(title, *parameters):
                sub[title_id] = title
        print(f'[INFO] --- Extracted: {len(sub)} / {len(self)}')
        print('[INFO] END Corpus#extract')
        return sub

#-------------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------------

def has_only_one_form(title, form):
    count = 0
    for word in title.words:
        if word.form == form:
            count += 1
    return count == 1

def no_filter(title, *parameters):
    return True

def has_x_after_form(title, form, nb, tst):
    count = 0
    start_counting = False
    for word in title.words:
        if start_counting:
            count += 1
        if word.form == form:
            start_counting = True
    if tst == '==':
        return count == nb
    elif tst == '!=':
        return count != nb
    elif tst == '>=':
        return count >= nb
    elif tst == '<=':
        return count <= nb
    elif tst == '>':
        return count > nb
    elif tst == '<':
        return count < nb

#-------------------------------------------------------------------------------
# Test if main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    w = Word('fatigué', 'fatiguer', 'V')
    print(w)
    print(w.to_xml())
    print(w.to_xml(minimize=False))

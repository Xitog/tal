#===============================================================================
# Code handling the elaborated corpus for TAL
# Author : Damien Gouteux
# Last updated : 08 April 2018
# Technologies : Python, Excel, XML
#===============================================================================

#-------------------------------------------------------------------------------
# Import
#-------------------------------------------------------------------------------

# standard
import datetime
import xml.etree.ElementTree as ET

# project
from corpus2 import Title, ExcelFile

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class Corpus:

    def __init__(self, filepath):
        start = datetime.datetime.now()
        self.titles = {}
        #tree = ET.parse(filepath)
        #root = tree.getroot()
        for event, elem in ET.iterparse(filepath, events=('end',)):
            if event == 'end':
                if elem.tag == 'notice':
                    t = Title.from_xml(elem)
                    self.titles[t.docid] = t
                    elem.clear()
        delta = datetime.datetime.now() - start
        print('Nb titles:', len(self.titles))
        print(f"Loaded in {delta}.")

    def count_titles(self):
        return len(self.titles)


if __name__ == '__main__':

    start_time = datetime.datetime.now()

    print('\n----- Starting ------\n')

    # Result file

    excel = ExcelFile(name='results3', mode='w')
    
    print('\n----- Loading corpus ------\n')
    
    #corpus = Corpus(r'output_dump_repo\dump.xml')
    corpus = Corpus(r'D:\Autres\dump.xml')
    
    print('\n----- Structures and words ------\n')
    
    # Structures and words after :

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
    
    print('\n----- End -----\n')

    delta = datetime.datetime.now() - start_time

    print(f"    Script has ended [{delta} elapsed].")

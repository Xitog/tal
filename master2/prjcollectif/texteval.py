#-----------------------------------------------------------
# Code to dialog with a Talismane server
# and process Talismane results.
#
# Inspired from:
# https://github.com/joliciel-informatique/talismane/blob/master/talismane_examples/src/main/java/com/joliciel/talismane/examples/TalismaneClient.java
#
#-----------------------------------------------------------

#-----------------------------------------------------------
# Import
#-----------------------------------------------------------

import sys
import pickle
from socket import socket, AF_INET, SOCK_STREAM

#-----------------------------------------------------------
# Connexion to an instance of Talismane
#-----------------------------------------------------------

def open_sock():
    """Open a connection to a running Talismane instance on the localhost"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('localhost', 7272))
    return sock


def send(cmd, debug=False):
    """Send data to a running Talismane instance"""
    sock = open_sock()
    cmd += '\f\f\f'
    if debug:
        print('Sending input to server:', cmd)
    sock.send(cmd.encode(encoding='utf-8'))
    # receive data
    chunks = []
    done = False
    while not done:
        chunk = sock.recv(2048)
        if chunk == b'':
            done = True
        chunks.append(chunk)
    res = b''.join(chunks)
    if debug:
        print('Server:', res)
    sock.close()
    return process_multilines(res.decode(encoding='utf-8').split('\n'))


#-----------------------------------------------------------
# Data model
#-----------------------------------------------------------

class Part:

    def __init__(self):
        self.sentences = []

    def append(self, s):
        self.sentences.append(s)

    def extend(self, p):
        self.sentences.extend(p.sentences)
    
    def __repr__(self):
        return f"A part of {len(self.sentences)} sentences."

    def __getitem__(self, i):
        return self.sentences[i]


class Sentence:

    def __init__(self):
        self.words = []

    def append(self, w):
        self.words.append(w)

    def __repr__(self):
        return f"A sentence of {len(self.words)} words."

    @property
    def form(self):
        f = []
        for w in self.words:
            f.append(w.form)
        return ' '.join(f)

    @property
    def lemmas(self):
        lem = []
        for w in self.words:
            lem.append(w.lemma)
        return ' '.join(lem)

    @property
    def char_len(self):
        nb = 0
        for w in self.words:
            nb += len(w.form)
        return nb

    def __len__(self):
        return len(self.words)

    def __getitem__(self, i):
        return self.words[i]

    
class Word:

    def __init__(self, num, form, lemma, pos, pos_lexicon, morphinfo, f7, f8, f9, f10):
        self.num = num          # The token number (starting at 1 for the first token)
        self.form = form        # The original word form (or _ for an empty token)
        self.lemma = lemma      # The lemma found in the lexicon (or _ when unknown)
        self.pos = pos          # The part-of-speech tag
        #self.pos_lexicon = pos_lexicon # The grammatical category found in the lexicon
        # The additional morpho-syntaxic information found in the lexicon.
        self.number = None      #     n=p|s: number = plural or singluar
        self.gender = None      #     g=m|f: gender = male or female
        self.person = None      #     p=1|2|3|12|23|123: person = 1st, 2nd, 3rd (or a combination thereof if several can apply)
        self.poss_number = None #     poss=p|s: possessor number = plural or singular
        self.tense = None       #     t=pst|past|imp|fut|cond: tense = present, past, imperfect, future or conditional. Verb mood is not included, since it is already in the postag.
        informations = morphinfo.split('|')
        for info in informations:
            infos = info.split('=')
            if len(infos) > 1:
                typ, val = infos[0], infos[1]
                if typ == 'n':
                    self.number = 'plural' if val == 'p' else 'singular'
                elif typ == 'g':
                    self.gender = 'male' if val == 'm' else 'female'
                elif typ == 'p':
                    self.person = val
                elif typ == 'poss':
                    self.possessor_number = 'plural' if val == 'p' else 'singular'
                elif typ == 't':
                    self.tense = val
        self.f7 = f7            # The token number of this token's governor (or 0 when the governor is the root)
        self.f8 = f8            # The label of the dependency governing this token
        #self.f9 = f9            
        #self.f10 = f10          

    def __str__(self):
        return self.num + '. ' + self.form + ' / ' + self.lemma + ' (' + self.pos + ')'

    def __repr__(self):
        return str(self)

#-----------------------------------------------------------
# Convert Talismane output to the datamodel
#-----------------------------------------------------------

def process_line(line, expected=15, debug=False):
    elems = line.split('\t')
    if len(elems) >= 10:
        return Word(*elems[0:10])
    else:
        if debug:
            o = '(' + str(len(elems)) + ')'
            print(f"{o:5}", ':', line)
        return None


def process_multilines(content):
    part = Part()
    sentence = None
    for line in content:
        w = process_line(line)
        if w is not None:
            if sentence is None:
                sentence = Sentence()
            sentence.append(w)
        else:
            if sentence is not None:
                part.append(sentence)
                sentence = None
    return part


def process_file(filename, encoding):
    file = open(filename, mode='r', encoding=encoding)
    content = file.readlines()
    file.close()
    return process_multilines(content)


def console():
    cmd = None
    while cmd != 'exit':
        cmd = input('enter sentence: ')
        if cmd != 'exit':
            part = send(cmd, debug=True)
            for sentence in part.sentences:
                for word in sentence.words:
                    print('   ', word)


def load_bin(filename):
    return pickle.load(open(filename, mode='rb'))


def txt2tal(target, encoding):
    f = open(target, mode='r', encoding=encoding)
    content = f.readlines()
    f.close()
    part = Part()
    logicalline = ''
    for phyline in content:
        if len(phyline) > 1:
            logicalline += ' '+ phyline.strip()
        elif len(logicalline) > 0:
            #print(logicalline)
            part.extend(send(logicalline))
            logicalline = ''
    if len(logicalline) > 0:
        #print(logicalline)
        part.extend(send(logicalline))
        logicalline = ''
    f = open(target.replace('.txt', '.bin'), mode='wb')
    pickle.dump(part, f)
    f.close()
    return part


order = 'test_process_file'
if __name__ == '__main__':
    if len(sys.argv) > 1:
        order = sys.argv[1]
    if order == 'console':
        console()
    elif order == 'test_send':
        part = send('Bonjour le monde !', debug=True)
        print(part)
    elif order == 'test_process_file':
        part = process_file('ema.tal', 'utf8')
        pickle.dump(part, open('ema.bin', mode='wb'))
    elif order == 'test_loading':
        part = load_bin('ema.bin')
    elif order == 'tal2bin':
        target = sys.argv[2]
        try: encoding = sys.argv[3]
        except IndexError: encoding = 'utf8'
        part = process_file(target, encoding)
        pickle.dump(part, open(target.replace('.tal', '.bin'), mode='wb'))
    elif order == 'loadbin':
        filename = sys.argv[2]
        part = load_bin(filename)
    elif order == 'txt2bin':
        target = sys.argv[2]
        try: encoding = sys.argv[3]
        except IndexError: encoding = 'utf8'
        part = txt2tal(target, encoding)

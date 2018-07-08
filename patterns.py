from copy import deepcopy


class Pattern:
    
    def __init__(self, text):
        self.text = text
        self.ast = parse(text)
        self.extended = build_possibilities(self.ast, [[]])
        self.possibilities = len(self.extended)
        self.min_length = None
        self.max_length = 0
        for pc in self.extended:
            if len(pc) > self.max_length:
                self.max_length = len(pc)
            if self.min_length is None or len(pc) < self.min_length:
                self.min_length = len(pc)

    def extended_by_length(self):
        res = []
        nb = 0
        for e in self.extended:
            res.append([nb, len(e), *e])
            nb += 1
        return res
    
    def to_xml(self, name='pattern_xml.txt'):
        f = open(name, mode='w', encoding='utf-8')
        f.write(str(suite))
        f.close()

    def to_txt(self, name='pattern_extended.txt'):
        f = open(name, mode='w', encoding='utf-8')
        for line in pattern_compiled:
            f.write(str(line) + '\n')
        f.close()

    def find_one(self, corpus):
        """ Try to find in data one title corresponding to at least one extended form of the pattern.
            Pattern is searched EVERYWHERE in the title.
            data must be a CORPUS.
            Warning:
                - contrary to the rest of the lib, this function needs a Corpus, not a list of POS.
                - contrary to the rest of the lib, this function searches anywhere in the title."""
        for key, title in corpus.titles.items():
            words = title.words
            for ex in self.extended:
                i = 0
                start = None
                matched = None
                while i < min(len(ex), len(words)) and ex[i] != words[i].pos:
                    i += 1
                if i < min(len(ex), len(words)):
                    start = i
                    i += 1
                    ln = 1
                    while ln < len(ex) and i < min(len(ex), len(words)):
                        if ex[i] == words[i].pos:
                            ln += 1
                        else:
                            break
                    if ln == len(ex):
                        return title, start, ex
        return None, None, None
    
    def trilist(self, words, after=None):
        "Transform a list of words to 3 lists for forms, lemma and pos."
        forms = []
        lemma = []
        pos = []
        if after is None:
            for w in words:
                forms.append(w.form)
                lemma.append(w.lemma)
                pos.append(w.pos)
        else:
            started = False
            for w in words:
                if started:
                    forms.append(w.form)
                    lemma.append(w.lemma)
                    pos.append(w.pos)
                if w.form == after:
                    started = True
        return forms, lemma, pos
    
    #def find_all_with(self, corpus, n1, n2):
    #    for key, title in corpus.titles.items():
    #        forms, lemma, pos = self.trilist(title.words, after=':')
            

    def match_one(self, val):
        """Take a list of pos as val"""
        if len(val) < self.min_length:
            return None
        selected = self.extended
        for i in range(len(val)):
            filtered = []
            for j in range(len(selected)):
                if i >= len(selected[j]) or val[i] == selected[j][i]:
                    if len(val) >= len(selected[j]): # don't match start of extended form not complete!
                        filtered.append(selected[j])
            selected = filtered
            if len(selected) == 0:
                break
        if len(selected) > 0:
            max_length = 0
            final = None
            for pc in selected:
                if len(pc) > max_length:
                    max_length = len(pc)
                    final = pc
            return final
        else:
            return None
    
    def match(self, data, info=True):
        matched = []
        unmatched = []
        itercount = 0
        iterdisplay = 1000
        iterstep = 1000
        for key, val in data.items():
            itercount += 1
            if itercount == iterdisplay:
                print(itercount, 'elements done.')
                iterdisplay += iterstep
            if len(val) < self.min_length:
                unmatched.append(key)
                continue
            selected = self.extended
            for i in range(len(val)):
                filtered = []
                for j in range(len(selected)):
                    if i >= len(selected[j]) or val[i] == selected[j][i]:
                        if len(val) >= len(selected[j]): # don't match start of extended form not complete!
                            filtered.append(selected[j])
                selected = filtered
                if len(selected) == 0:
                    break
            if len(selected) > 0:
                perfect = False
                for pc in selected:
                    if len(pc) == len(val):
                        perfect = True
                        break
                matched.append(key)
            else:
                unmatched.append(key)
        return matched, unmatched

    def __str__(self):
        return self.text

    def __repr__(self):
        return "Pattern : " + self.text

class Node:
    
    def __init__(self):
        self.opt = False
    
    def __str__(self):
        return f'<Node opt={self.opt}/>'

    def display(self, level=0):
        return '    ' * level + str(self)


class Identifier(Node):
    
    def __init__(self, val):
        Node.__init__(self)
        self.val = val

    def __str__(self):
        return f'<Identifier val={self.val} opt={self.opt}/>'


class Suite(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.nodes = []
        self.name = 'Suite'
        self.mod = 'AND'
    
    def append(self, node : Node):
        if not isinstance(node, Node):
            raise Exception('Not a Node: ' + str(node))
        self.nodes.append(node)
    
    def last(self):
        return self.nodes[-1]

    def display(self, level=0):
        s = '    ' * level + f'<{self.name} opt={self.opt}\n'
        cpt = 0
        for n in self.nodes:
            x = self.mod if cpt < len(self.nodes) - 1 else ''
            s += n.display(level + 1) + f' {x}\n'
            cpt += 1
        s += '    ' * level + '/>'
        return s
    
    def __str__(self):
        return self.display()

    def __getitem__(self, i):
        return self.nodes[i]


class Choice(Suite):

    def __init__(self):
        Suite.__init__(self)
        self.name = 'Choice'
        self.mod = 'OR'


def parse(pattern, choice=False):
    #print('Parsing:', pattern, 'choice=', choice)
    suite = Suite() if not choice else Choice()
    w = ''
    in_word = False
    i = 0
    def find_closing(pattern, form, i):
        level = 1
        last = None
        closing = {'(' : ')', '[' : ']'}
        closing = closing[form]
        for i2 in range(i + 1, len(pattern)):
            c2 = pattern[i2]
            if c2 == form:
                level += 1
            elif c2 == closing:
                level -= 1
            if level == 0:
                last = i2
                break
        if last is None:
            raise Exception("Not closing ) found!")
        return last
    while i  < len(pattern):
        c = pattern[i]
        # identifier
        if c.isalpha() or c == '+':
            in_word = True
        elif in_word:
            in_word = False
            suite.append(Identifier(w))
            w = ''
        if in_word:
            w += c
        # option
        if c == '?':
            suite.last().opt = True
        elif c == '[':
            last = find_closing(pattern, '[', i)
            suite.append(parse(pattern[i+1 : last], True))
            i = last
        elif c == '(':
            last = find_closing(pattern, '(', i)
            suite.append(parse(pattern[i+1 : last]))
            i = last
        i += 1
    if in_word:
        suite.append(Identifier(w))
    return suite


def build_possibilities(elem, possibilities):
    if type(elem) == Identifier:
        new_possibilities = deepcopy(possibilities)
        for np in new_possibilities:
            np.append(elem.val)
        if not elem.opt:
            possibilities = new_possibilities
        else:
            possibilities += new_possibilities
    elif type(elem) == Suite:
        new_possibilities = deepcopy(possibilities)
        for e2 in elem:
            new_possibilities = build_possibilities(e2, new_possibilities)
        if not elem.opt:
            possibilities = new_possibilities
        else:
            possibilities += new_possibilities
    elif type(elem) == Choice:
        new_possibilities = []
        for e2 in elem:
            new_possibilities.append(deepcopy(possibilities))
            new_possibilities[-1] = build_possibilities(e2, new_possibilities[-1])
        if not elem.opt: # if not optional, there will be only our choices available, not the original ones that we must delete
            possibilities = []
        for n in new_possibilities:
            possibilities += n
    else:
        raise Exception("Type not known: " + str(type(elem)))
    return possibilities

if __name__ == '__main__':
    from titles import Word
    w = [Word('tests', 'test', 'DET'), Word(':', ':', 'PONCT'), Word('la', 'la', 'DET'), Word('maison', 'maison', 'NC'), Word('de', 'de', 'P'), Word('la', 'la', 'DET'), Word('forêt', 'forêt', 'NC')]
    pattern = Pattern('DET? ADJ? [NC NPP] [NC NPP]? ADJ? [(P DET?) P+D] ADJ? [NC NPP] [NC NPP]? ADJ?')
    forms, lemma, pos = pattern.trilist(w, after=':')
    print(forms)
    print(lemma)
    print(pos)


    

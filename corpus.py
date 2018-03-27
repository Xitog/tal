# standard
import os
import os.path
import json
import datetime
import sys

# external
import xlwt
import matplotlib.pyplot as plt

class Repository:

    def __init__(self, path):
        self.path = path
        self.filenames = os.listdir(self.path)
        self.num_found = None
        self.num_read = 0
        self.titles = []
        self.discarded = {}
    
    def count_files(self):
        return len(self.filenames)

    def count_titles(self):
        return len(self.titles)
    
    def load_all(self):
        for i in range(0, len(self.filenames)):
            self.load_one(i)
    
    def load_one(self, num):
        filename = self.filenames[num]
        path = os.path.join(self.path, filename)
        content = json.load(open(path, encoding='utf8'))
        response = content["response"]
        # numFound check
        if self.num_found is None:
            self.num_found = response['numFound']
        elif self.num_found != response['numFound']:
            # Tolerating +1 or +2 in response
            if self.num_found != response['numFound'] - 1 and self.num_found != response['numFound'] - 2:
                print('[ERROR]')
                print(f'self.num_found = {self.num_found}')
                print(f'response["numFound"] = {response["numFound"]}')
                print(f'in doc {filename}')
                raise Exception('numFound not corresponding to the previously found.')
        # counting
        docs = response['docs']
        self.num_read += len(docs)
        for doc in docs:
            try:
                self.titles.append(Title(doc, filename))
            except KeyError as ke:
                kes = str(ke)
                if kes not in self.discarded:
                    self.discarded[kes] = []
                self.discarded[kes].append(str(doc['docid']) + ' in ' + filename)
    
    def __str__(self):
        return 'Repository ' + self.path + ' (' + str(self.num_read) + ')'

    def __repr__(self):
        return str(self)

    def discarded_info(self):
        for key in self.discarded:
            print(f'{len(self.discarded[key])} because of missing key {key}')


class Domain:
    
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.titles = []
        self.children = {}
        self.parent = None

    def display(self, nb, out=sys.stdout):
        ttl = len(self.titles)
        out.write('    ' * (self.level + 1) + f"{self.level}.{nb} {self}\n")
        i = 1
        for child in sorted(self.children.keys()):
            ttl += self.children[child].display(i, out)
            i += 1
        return ttl
    
    @staticmethod
    def register_list(domain_list, title):
        last = None
        for domain_code in domain_list:
            last = Domain.register_one(domain_code)
        last.titles.append(title) # we link the title and the domain only once
        return last # we retains only the last domain to put into title#domains
    
    ROOTS = {}

    @staticmethod
    def register_one(domain_code):
        element = domain_code.split('.')
        level = int(element[0])
        domain = None
        if level == 0:
            if len(element) != 2:
                raise Exception('A 0-level domain can only have one following name.')
            if element[1] not in Domain.ROOTS:
                Domain.ROOTS[element[1]] = Domain(element[1], 0)
            domain = Domain.ROOTS[element[1]]
        else: # level > 0
            parent = Domain.ROOTS[element[1]]
            for i in range(2, len(element)):
                if element[i] not in parent.children:
                    parent.children[element[i]] = Domain(element[i], level)
                parent = parent.children[element[i]]
            domain = parent
        return domain

    def __str__(self):
        return self.name.upper() + ' (lvl=' + str(self.level) + ', chld=' + str(len(self.children)) + ', ttl=' + str(len(self.titles)) + ')'


class Author:

    ALL_AUTHORS = {}
    
    def __init__(self, name):
        self.name = name
        self.titles = []

    @staticmethod
    def register(name, title):
        if name not in Author.ALL_AUTHORS:
            Author.ALL_AUTHORS[name] = Author(name)
        Author.ALL_AUTHORS[name].titles.append(title)
        return Author.ALL_AUTHORS[name]

    def __repr__(self):
        return self.name


def segment_string(string):
    words = []
    start = 0
    end = 0
    length = 0
    for c in string:
        if start == end: # we are not in a word
            if c.isspace() or c in ["“", '"', "'", '’', '.', '«', '»', '°', '(', ')', '/', '\\', ':', '[', ']', ',']:
                start += 1
                end += 1
            else:
                end += 1
        else: # we are in a word
            if c.isspace() or c in ["“", '"', "'", '’', '.', '«', '»', '°', '(', ')', '/', '\\', ':', '[', ']', ',']:
                words.append((start, end))
                start = end + 1
                end = start
            else:
                end += 1
    if start != end:
        words.append((start, end))
    return words

# if a title has twice a not alphanumeric, it is counted only one
# for this character. We don't want to know how many time there is "."
# in a title, but how many titles have at least one "." in
SPECIAL_CHAR_COUNT = {}

class Title:

    def __init__(self, dic, filename):
        global WRONG_TITLES
        # Atomic values
        self.docid = dic['docid']
        self.kind = dic['docType_s']
        self.date = dic['modifiedDateY_i']
        self.filename = filename
        # Lang
        lang_list = dic['language_s']
        if len(lang_list) > 1:
            raise Exception('Too many langs')
        self.lang = lang_list[0]
        if self.lang != 'fr':
            raise KeyError('lang')
        # Authors
        author_list = dic['authFullName_s']
        self.authors = []
        for author in author_list:
            self.authors.append(Author.register(author, self))
        # Domains
        domain_list = dic['domain_s']
        self.domains = Domain.register_list(domain_list, self)
        # Title
        title_list = dic['title_s']
        self.title = title_list[0]
        self.char_count = len(self.title)
        self.words = segment_string(self.title)
        self.word_count = len(self.words)
        self.special_char = False
        self.special_char_count = {}
        for c in self.title:
            if not c.isalnum() and not c.isspace():
                self.special_char = True
                if c not in self.special_char_count:
                    self.special_char_count[c] = 1
                    if c not in SPECIAL_CHAR_COUNT:
                        SPECIAL_CHAR_COUNT[c] = 0
                    SPECIAL_CHAR_COUNT[c] += 1
                else:
                    self.special_char_count[c] += 1
    
    def __repr__(self):
        return f"{self.docid} in {self.filename}"




class Statistic:

    def __init__(self, repo):
        self.repo = repo

    def count_values(self, key):
        values = {}
        for t in repo.titles:
            val = getattr(t, key)
            if val not in values:
                values[val] = 1
            else:
                values[val] += 1
        return values

    def count_length(self, key, threshold=None, export=None):
        sums = {}
        for t in repo.titles:
            val = len(getattr(t, key))
            if val not in sums:
                sums[val] = 1
            else:
                sums[val] += 1
        return sums

    def count_word_n(self, index):
        values = {}
        for t in repo.titles:
            if index >= 0 and index < len(t.words):
                delim = t.words[index]
                word = t.title[delim[0]:delim[1]]
                if word not in values:
                    values[word] = 1
                else:
                    values[word] += 1
        return values
    
    def count_values_n(self, key, index):
        values = {}
        for t in repo.titles:
            att = getattr(t, key)
            if index >= 0 and index < len(att):
                val = att[index]
                if val not in values:
                    values[val] = 1
                else:
                    values[val] += 1
        return values
    
    def select(self, **keyval):
        results = []
        for t in repo.titles:
            ok = True
            for key, val in keyval.items():
                if getattr(t, key) != val:
                    ok = False
                    break
            if ok:
                results.append(t)
        return results

    def info(self, idv):
        for t in repo.titles:
            if t.docid == idv:
                print('docid =', t.docid)
                print('kind =', t.kind)
                print('date =', t.date)
                print('filename =', t.filename)
                print('title =', t.title)
                print('char_count=', t.char_count)
                print('word_count=', t.word_count)
                print('lang=', t.lang)
                print('authors=')
                for auth in t.authors:
                    print('   ', auth)
                print('domains=')
                if t.domains is not None:
                    for dom in t.domains:
                        print('   ', dom)
                else:
                    print('    None')

start = datetime.datetime.now()

repo = Repository('corpus-3046-files-2018-02-20-197-Mo')
print('Nb files :', repo.count_files())
repo.load_all()
print('Nb titles:', repo.count_titles())
stat = Statistic(repo)

# Result file

wb = xlwt.Workbook()

def save_to_excel(wb, name, values):
    ws = wb.add_sheet(name)
    row = 0
    for val in sorted(values.keys()):
        ws.write(row, 0, val)
        ws.write(row, 1, values[val])
        row += 1

def save_to_graph(name, values):
    plt.bar(range(len(values)), values.values(), align="center")
    plt.xticks(range(len(values)), list(values.keys()))
    plt.legend((name), 'upper left')
    plt.autoscale(True)
    plt.grid(True)
    #plt.show()
    plt.savefig(name + '.png')

# Atomic values

by_date = stat.count_values('date')
save_to_excel(wb, 'Date | nb', by_date)
save_to_graph('date', by_date)

by_kind = stat.count_values('kind')
save_to_excel(wb, 'Type | nb', by_kind)
save_to_graph('kind', by_kind)

by_lang = stat.count_values('lang')
save_to_excel(wb, 'Lang | nb', by_lang)
del by_lang

by_char_count = stat.count_values('char_count')
save_to_excel(wb, 'Char Count | nb', by_char_count)
save_to_graph('char_count', by_char_count)
del by_char_count

by_sc = stat.count_values('special_char')
save_to_excel(wb, 'Special char in title | nb', by_sc)
del by_sc
# Not alpha numeric char
save_to_excel(wb, 'Special char | nb', SPECIAL_CHAR_COUNT)

by_word_count = stat.count_values('word_count')
save_to_excel(wb, 'Word Count | nb', by_word_count)
save_to_graph('word_count', by_word_count)

first_word = stat.count_word_n(0)
save_to_excel(wb, 'First word | nb', first_word)

# Author
print('\n----- Authors ------\n')
print('    There is', len(Author.ALL_AUTHORS), 'authors.\n')
nb_authors_by_length = {}
print('    nb articles (Y) => authors (X) : There is X authors having Y articles')
for name, author in Author.ALL_AUTHORS.items():
    nb = len(author.titles)
    if nb not in nb_authors_by_length:
        nb_authors_by_length[nb] = 0
    nb_authors_by_length[nb] += 1
for nb in sorted(nb_authors_by_length.keys()):
    print('   ', nb, ':', nb_authors_by_length[nb])
print()
for name, author in Author.ALL_AUTHORS.items():
    if len(author.titles) >= 190:
        print('   ', name, 'has', len(author.titles), 'publications.')
print()
print('    nb authors (Y) => articles (X) (there is X articles having Y authors)')
stat.count_length('authors', threshold=6)

# Domain
print('\n----- Domains -----\n')
print('    There is', len(Domain.ROOTS), 'roots domain.')
out = open('domains.txt', mode='w', encoding='utf8')
i = 1
nb = 0
for _, dom in Domain.ROOTS.items():
    nb += dom.display(i, out) #print('    ', i, '. ', dom, sep='')
    i += 1
out.close()
print('    There is', nb, 'publications linked to the domains.')
# Request
print('\n----- Request -----\n')
res = stat.select(char_count=0)
print('    Length of selection of char_count == 0:', len(res))
for r in res:
    print('      ', r)
res = stat.select(char_count=1)
print('    Length of selection of char_count == 1:', len(res))
for r in res:
    print('      ', r)
print('\n----- End -----\n')

wb.save('results.xls')

end = datetime.datetime.now()

delta = end - start

print(f"Script has ended [{delta} elapsed].")

repo.discarded_info()


#bwc = by_word_count
#lists = sorted(bwc.items())
#x, y = zip(*lists)
#plt.plot(x, y)
#plt.savefig('one.png')
#plt.show()

#plt.bar(range(len(bwc)), bwc.values(), align="center")
#plt.xticks(range(len(bwc)), list(bwc.keys()))
#plt.show()
#plt.savefig('two.png')

# 3046 fichiers
# 100 enregistrements à chaque fois
# total ~= 304 600

# 2018 100

# ART 40
# COMM 27
# COUV 16
# DOUV 2
# MEM 2
# OTHER 2
# OUV 1
# REPORT 2
# THESE 7
# UNDEFINED 1

# fr 100

# 298 118 une fois "filtré"

# matplotlib 2.2.2
#   numpy 1.14.2
#   pyparsing 2.2.0
#   pytz 2018.3
#   python-dateutil 2.7.2 
#   kiwi-solver 1.0.1
#   cycler 0.10.0


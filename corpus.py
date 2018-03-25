import os
import os.path
import json

class Repository:

    def __init__(self, path):
        self.path = path
        self.filenames = os.listdir(self.path)
        self.num_found = None
        self.num_read = 0
        self.titles = []
    
    def count(self):
        return len(self.filenames)

    def load_one(self, num):
        filename = self.filenames[num]
        path = os.path.join(self.path, filename)
        content = json.load(open(path, encoding='utf8'))
        response = content["response"]
        # numFound check
        if self.num_found is None:
            self.num_found = response['numFound']
        elif self.num_found != response['numFound']:
            raise Exception('numFound not corresponding to the previously found.')
        # counting
        docs = response['docs']
        self.num_read += len(docs)
        for doc in docs:
            self.titles.append(Title(doc))

    def __str__(self):
        return 'Repository ' + self.path + ' (' + str(self.num_read) + ')'

    def __repr__(self):
        return str(self)


class Domain:
    
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.titles = []
        self.children = {}
        self.parent = None

    def display(self, nb):
        ttl = len(self.titles)
        print('    ' * (self.level + 1), self.level, '.', nb, ' ', str(self), sep='')
        i = 1
        for child in sorted(self.children.keys()):
            ttl += self.children[child].display(i)
            i += 1
        return ttl
    
    @staticmethod
    def register_list(domain_list, title):
        last = None
        for domain_code in domain_list:
            last = Domain.register_one(domain_code)
        last.titles.append(title) # we link the title and the domain only once
    
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


class Title:

    def __init__(self, dic):
        # Atomic values
        self.docid = dic['docid']
        self.title = dic['title_s']
        self.kind = dic['docType_s']
        self.date = dic['modifiedDateY_i']
        # Lang
        lang_list = dic['language_s']
        if len(lang_list) > 1:
            raise Exception('Too many langs')
        self.lang = lang_list[0]
        # Authors
        author_list = dic['authFullName_s']
        self.authors = []
        for author in author_list:
            self.authors.append(Author.register(author, self))
        # Domains
        domain_list = dic['domain_s']
        self.domains = Domain.register_list(domain_list, self)


class Counter:

    def __init__(self, repo):
        self.repo = repo

    def count_values(self, key=''):
        values = {}
        for t in repo.titles:
            val = getattr(t, key)
            if val not in values:
                values[val] = 1
            else:
                values[val] += 1
        for val in sorted(values.keys()):
            print('    ', val, ' => ', values[val], sep='')

    def count_sum(self, key=''):
        sums = {}
        for t in repo.titles:
            val = len(getattr(t, key))
            if val not in sums:
                sums[val] = 1
            else:
                sums[val] += 1
        for val in sorted(sums.keys()):
            print('    ', val, ' => ', sums[val], sep='')


repo = Repository('corpus-3046-files-2018-02-20-197-Mo')
print(repo.count())
repo.load_one(0)
counter = Counter(repo)
# Atomic values
print('\n----------\n')
counter.count_values('date')
print('\n----------\n')
counter.count_values('kind')
print('\n----------\n')
counter.count_values('lang')
# Author
print('\n----------\n')
print('    There is', len(Author.ALL_AUTHORS), 'authors.\n')
for name, author in Author.ALL_AUTHORS.items():
    if len(author.titles) > 1:
        print('   ', name, 'has', len(author.titles), 'publications.')
print()
print('    nb authors => articles')
counter.count_sum('authors')
# Domain
print('\n----------\n')
print('    There is', len(Domain.ROOTS), 'roots domain:')
i = 1
nb = 0
for _, dom in Domain.ROOTS.items():
    nb += dom.display(i) #print('    ', i, '. ', dom, sep='')
    i += 1
print('There is', nb, 'publications linked to the domains.')

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


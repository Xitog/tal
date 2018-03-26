# standard
import os
import os.path
import json
import datetime

# external
import xlwt

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
                self.titles.append(Title(doc))
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
        self.kind = dic['docType_s']
        self.date = dic['modifiedDateY_i']
        # Title
        title_list = dic['title_s']
        self.title = title_list[0]
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

    def count_length(self, key='', threshold=None, export=None):
        sums = {}
        for t in repo.titles:
            val = len(getattr(t, key))
            if val not in sums:
                sums[val] = 1
            else:
                sums[val] += 1
            #if val == 2 and key == 'title':
            #    print(getattr(t, key))
        for val in sorted(sums.keys()):
            if threshold is None or sums[val] >= threshold:
                print('    ', val, ' => ', sums[val], sep='')
        if export is not None:
            if export == 'Excel':
                wb = xlwt.Workbook()
                ws = wb.add_sheet(key)
                ws.write(0, 0, 'lenght of ' + key)
                ws.write(0, 1, 'number of titles')
                row = 1
                for val in sorted(sums.keys()):
                    ws.write(row, 0, val)
                    ws.write(row, 1, sums[val])
                    row += 1
                wb.save(key + '.xls')

start = datetime.datetime.now()

repo = Repository('corpus-3046-files-2018-02-20-197-Mo')
print('Nb files :', repo.count_files())
repo.load_all()
print('Nb titles:', repo.count_titles())
#LOAD = 1000
#for i in range(0, LOAD):
#    repo.load_one(i)
counter = Counter(repo)
# Atomic values
print('\n------ Date ------\n')
counter.count_values('date')
print('\n------ Kind ------\n')
counter.count_values('kind')
print('\n------ Lang ------\n')
counter.count_values('lang')
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
counter.count_length('authors', threshold=6)
# Title
print('\n----- Title -----\n')
counter.count_length('title', export='Excel') # calcul de longueur
# Domain
print('\n----- Domains -----\n')
print('    There is', len(Domain.ROOTS), 'roots domain:')
i = 1
nb = 0
for _, dom in Domain.ROOTS.items():
    nb += dom.display(i) #print('    ', i, '. ', dom, sep='')
    i += 1
print('There is', nb, 'publications linked to the domains.')

end = datetime.datetime.now()

delta = end - start

print(f"Script has ended [{delta} elapsed].")

repo.discarded_info()

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


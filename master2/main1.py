#-------------------------------------------------
# Data model
#-------------------------------------------------

class Word:

    def __init__(self, form, lemma, gov, dep):
        self.form = form
        self.lemma = lemma
        self.pos = pos
        self.gov = gov
        self.dep = dep


class Title:

    def __init__(self, idt, year, typ, domains, authors, text):
        self.idt = idt
        self.year = year
        self.typ = typ
        self.domains = domains
        self.authors = authors
        self.text = text
        self.words = []

    def __repr__(self):
        return f"<Title |{self.text[:20]}| #{self.typ} @{self.year}>"

    def __str__(self):
        return repr(self)

#-------------------------------------------------
# Split talismane data
#-------------------------------------------------

try:
    file = open('titres-articles-HAL.tal', encoding='utf8', mode='r')
except FileNotFoundError:
    print('File not found.')
except UnicodeDecodeError:
    print('Invalid utf-8 format.')
else:
    content = file.readlines()
    nb = 0
    nb_part = 0
    nb_total_part = 6
    nb_by_part = len(content) // nb_total_part
    output = None
    for line in content:
        if nb == nb_by_part:
            output.close()
            nb = 0
        if nb == 0:
            nb_part += 1
            output = open(f"output_{nb_part:02d}.txt", encoding='utf8', mode='w')
        nb += 1
        output.write(line)
    if output is not None:
        output.close()

#-------------------------------------------------
# Read titles metadata
#-------------------------------------------------

titles = {}
titles_idt = []

try:
    file = open('total-articles-HAL.tsv', encoding='utf8', mode='r')
    content = file.readlines()
except FileNotFoundError:
    print('File not found.')
except UnicodeDecodeError:
    print('Invalid utf-8 format.')
else:
    print('[INFO] ---', len(content), 'lines.') # 339687
    for line in content:
        elements = line.split('\t')
        idt = elements[0]
        year = elements[1]
        typ = elements[2][1:-1]
        domains = elements[3][1:-1]
        authors = elements[4][1:-1]
        text = elements[5][1:-1]
        t = Title(idt, year, typ, domains, authors, text)
        titles[t.idt] = t
        titles_idt.append(t.idt)
    file.close()

#-------------------------------------------------
# Write only title, one title per line
#-------------------------------------------------

output = open('titles.txt', encoding='utf8', mode='w')
for t in titles:
    output.write(t.text)
output.close()

print('[INFO] ---', len(titles), 'titles.')
if len(titles) > 0:
    t = titles[titles_idt[0]]
    print(t)

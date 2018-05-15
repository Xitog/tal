#-------------------------------------------------------------------------------
# Import
#-------------------------------------------------------------------------------

import os
import pytalismane
import jsonpickle
import json

#-------------------------------------------------------------------------------
# Data model
#-------------------------------------------------------------------------------

class Collection:

    def __init__(self):
        self.collection = {}

    def register(self, key):
        if key in self.collection:
            self.collection[key] += 1
        else:
            self.collection[key] = 1

    def display(self, num=None, ordered=True):
        if ordered:
            for key in sorted(self.collection.keys(), key=self.collection.get, reverse=True):
                if num is None:
                    print(key, '{:02d}'.format(self.collection[key]))
                else:
                    print(key, '{:02d}'.format(self.collection[key]), '{:05.2f}'.format(self.collection[key] / num * 100))
        else:
            for k, v in self.collection.items():
                if num is None:
                    print(k, '{:02d}'.format(v))
                else:
                    print(k, '{:02d}'.format(v), '{:06.2f}'.format(v / num * 100))

class Hash:

    def __init__(self, tag):
        self.tag = tag
        self.ids = tag.lower()
        
    def __str__(self):
        return self.ids

class Tweet:

    def __init__(self, idt=None, author=None, account=None, rt=None, fav=None, date=None, text=None,
                 annotated=None, status=None, discourse=None, verbal_act=None, physical_act=None,
                 theme=None, relationship=None, language_acte=None, temps=None, milieu=None,
                 agit=None, agitsx=None, subit=None, subitsx=None, enonciator=None, url=None):
        self.idt = idt
        self.author = author
        self.account = account
        self.rt = rt
        self.fav = fav
        self.date = date 
        self.raw_text = text
        self.annotated = annotated
        self.status = status
        self.discourse = discourse
        self.verbal_act = verbal_act
        self.physical_act = physical_act
        self.theme = theme
        self.relationship = relationship
        self.language_acte = language_acte
        self.temps = temps
        self.text = delete_url(self.raw_text)
        self.words = pytalismane.process_string(self.text)
        self.hashtag_and_ref = hashtag_and_ref(self.text)
        self.milieu = milieu
        self.agit = agit
        self.agitsx = agitsx
        self.subit = subit
        self.subitsx = subitsx
        self.enonciator = enonciator
        self.url = url

#-------------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------------

def load_csv(filename):
    all_content = []
    file = open(filename, mode='r', encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        content = line.split(';')
        all_content.append(Tweet(*content))
    return all_content

def load_text_files(dirname, encoding='utf-8'):
    """Load a bunch of text files and read them all. Return a list of their content."""
    all_contents = []
    filenames = os.listdir(dirname)
    for filename in filenames:
        file = open(os.path.join(dirname,filename), mode='r', encoding=encoding)
        content = file.read()
        file.close()
        all_contents.append(content)
    return all_contents

def delete_url(content):
    """Delete all URL from content. URL can have two forms:
        1) http://... ou https://...
        2) pic.twitter.com...
    """
    found = content.find('http')
    if found == -1:
        found = content.find('pic.twitter.com')
    while found != -1:
        for c in range(found, len(content)):
            if content[c] == ' ':
                if c+1 < len(content):
                    if content[c+1] == '…':
                        continue
                break
        if c == len(content)-1:
            content = content[:found]
        else:
            content = content[:found] + content[c:]
        found = content.find('http')
        if found == -1:
            found = content.find('pic.twitter.com')
    return content

def hashtag_and_ref(content):
    """Get hashtags."""
    start = False
    value = ''
    hashes = []
    for c in content:
        if start and c not in [' ', '"', '\n']:
            value += c
        elif c == '#':
            start = True
            value = '#'
        elif c == '@':
            start = True
            value = '@'
        elif start and c in [' ', '"', '\n']:
            start = False
            hashes.append(Hash(value))
            value = ''
    if start and value != '':
        hashes.append(Hash(value))
    return hashes

#-------------------------------------------------------------------------------
# Main program
#-------------------------------------------------------------------------------

PASS = 3

if __name__ == '__main__':
    if PASS == 1:
        #tweets = load_text_files('')
        tweets = load_csv('projet_tweet_corpus.csv')
        i = 1
        all_hashes = Collection()
        sock = pytalismane.open_sock()
        for tw in tweets:
            print('----', i, '----')
            print(tw.text)
            for h in tw.hashtag_and_ref:
                print('   ', h)
                all_hashes.register(h.ids)
            i+=1
            print()
        all_hashes.display()
        save_json = jsonpickle.encode(tweets)
        json.dump(save_json, open('save.json', mode='w', encoding='utf-8'), indent='    ', ensure_ascii=False)
    elif PASS == 2:
        o_json = json.load(open('projet_tweet_save.json', mode='r', encoding='utf-8'))
        tweets = jsonpickle.decode(o_json)
        all_hashes = Collection()
        all_sexes_of_actor = Collection()
        all_sexes_of_subissor = Collection()
        milieux = Collection()
        status = Collection()
        discourses = Collection()
        verbal_acts = Collection()
        physical_acts = Collection()
        themes = Collection()
        relationships = Collection()
        language_acts = Collection()
        subit_ennonce = Collection()
        for tw in tweets:
            hash_and_ref_already_ref = []
            for h in tw.hashtag_and_ref:
                if h.ids not in hash_and_ref_already_ref:
                    all_hashes.register(h.ids)
                    hash_and_ref_already_ref.append(h.ids)
            all_sexes_of_actor.register(tw.agitsx)
            all_sexes_of_subissor.register(tw.subitsx)
            subit_ennonce.register(tw.enonciator)
            milieux.register(tw.milieu)
            status.register(tw.status)
            discourses.register(tw.discourse)
            verbal_acts.register(tw.verbal_act)
            physical_acts.register(tw.physical_act)
            themes.register(tw.theme)
            relationships.register(tw.relationship)
            language_acts.register(tw.language_acte)
        print('\nHash and ref\n')
        all_hashes.display()
        print('\nSexe of Actor\n')
        all_sexes_of_actor.display(50)
        print('\nSexe of Subissor\n')
        all_sexes_of_subissor.display(50)
        print('\nSexe of Ennonce\n')
        subit_ennonce.display(50)
        print('\nMilieu\n')
        milieux.display(50)
        print('\nStatus\n')
        status.display(50)
        print('\nDiscourses\n')
        discourses.display(50)
        print('\nVerbal acts\n')
        verbal_acts.display(50)
        print('\nPhysical acts\n')
        physical_acts.display(50)
        print('\nThemes\n')
        themes.display(50)
        print('\nRelationships\n')
        relationships.display(50)
        print('\nLanguage Acts\n')
        language_acts.display(50)
    elif PASS == 3:
        o_json = json.load(open(r'projet_tweet\projet_tweet_save.json', mode='r', encoding='utf-8'))
        tweets = jsonpickle.decode(o_json)
        
        rules = { 'cat_milieu_media' : {
                    'typ' : 'set_of_words',
                    'ens' : ['media', 'journalisme', 'chaîne', 'journaliste'],
                    'cat' : 'milieu',
                    'val' : 'Média',
                    'plus': 'score',
                }, 'ref_milieu_media' : {
                    'typ' : 'ref',
                    'ens' : ['@frhaz'],
                    'cat' : 'milieu',
                    'val' : 'Média',
                    'plus': 'score',
                }, 'cat_milieu_études' : {
                    'typ' : 'set_of_words',
                    'ens' : ['étudiant', 'étudiants', 'fac', 'université'],
                    'cat' : 'milieu',
                    'val' : 'Études',
                    'plus': 'score'
                },
            }
        for tw in tweets:
            print('Tweet:', tw.text[:50])
            categories = {
                    'milieu' : {
                            'Média' : 0,
                            'Études': 0,
                        }
                }
            for rule in rules.values():
                score = 0
                if rule['typ'] == 'set_of_words':
                    for w in tw.words:
                        if w.lemma in rule['ens']:
                            #print('    ', w.lemma, sep='')
                            score += 1
                elif rule['typ'] == 'ref':
                    for h in tw.hashtag_and_ref:
                        if h.ids in rule['ens']:
                            score += 1
                if score > 0:
                    categories[rule['cat']][rule['val']] += score
            #end of rules
            for key, val in categories['milieu'].items():
                if val > 0:
                    print(f"Milieu = {key} for with tweet with a score of {val}")
            print('This has for milieu: ', getattr(tw, rule['cat']), '.', sep='')
            #print(f"    Its category {rule['cat']} should be {rule['val']} with a score of {score} and is {getattr(tw, rule['cat'])}.") 
            print()
            print()
        
        # 16h39 : YES ! Cela valide mon archi.
        

#-----------------------------------------------------------
# Damien Gouteux 2019
# CC 3.0 BY-SA-NC
#-----------------------------------------------------------

#-----------------------------------------------------------
# Import
#-----------------------------------------------------------

# Standard library
import datetime
import pickle
import json

# External library
#import nltk
#from nltk.tokenize.regexp import RegexpTokenizer
#import re
import pandas as pd

#-----------------------------------------------------------
# Switches
#-----------------------------------------------------------

if __name__ == '__main__':
    LOAD_ALL =  False
    LOAD_TRAIN = True
    LOAD_TEST = True
    LOAD_STOPWORDS = True

    CONVERT = False
    MAKE_CORPUS_ALL = False
    MAKE_TRAIN_TEST_FROM_PICKLE_ALL = False
    LOAD_ONE_FROM_PICKLE = False
    LOAD_WHAT =  'backup.bin'
    COMPARE_TRAIN_TEST = False
    STAT_DOMAIN_SUPPORT = False
    CROSS_SUPPORT_AUTHORS = False

    LENGTH_FREQ_STATS = True
    DOUBLONS_TEST = False
    COVER_CALC = False          # (for silhouette's words on Domains)
    SHOW_BEST = False           # (for silhouette's words in Domains)
    FEATURE_EXTRACTION_POS = False
    EVALUATE_MY_MODEL_POS = False
    EVALUATE_MY_MODEL_SILHOUETTE = True    # (use my model) or True
    COMBINED_SILHOUETTE_AND_POS = True     # combine Silhouette & POS => BAD
    EVALUATE_TARGET = 'TRAIN'
    EVALUATE_NB_FACTOR = 10_000 # number of features 100 1000 10_000 None=all
else:
    LOAD_ALL = False
    LOAD_TRAIN = False
    LOAD_TEST = False
    LOAD_STOPWORDS = True

    CONVERT = False
    MAKE_CORPUS_ALL = False
    MAKE_TRAIN_TEST_FROM_PICKLE_ALL = False
    LOAD_ONE_FROM_PICKLE = False
    LOAD_WHAT =  None
    COMPARE_TRAIN_TEST = False
    STAT_DOMAIN_SUPPORT = False
    CROSS_SUPPORT_AUTHORS = False
    
    LENGTH_FREQ_STATS = False
    DOUBLONS_TEST = False
    COVER_CALC = False
    SHOW_BEST = False
    FEATURE_EXTRACTION_POS = False
    EVALUATE_MY_MODEL_POS = False
    EVALUATE_MY_MODEL_SILHOUETTE = False
    EVALUATE_TARGET = None
    EVALUATE_NB_FACTOR = 0

#-----------------------------------------------------------
# Data Model
#-----------------------------------------------------------

class MiniTitle:
    def __init__(self, d, s, y, a, t):
        self.domain = d
        self.support = s
        self.year = int(y)
        self.authors = int(a)
        self.title = t.strip()

    def to_list(self):
        return [self.domain, self.support, self.year, self.authors, self.title]

#-----------------------------------------------------------
# Globals
#-----------------------------------------------------------

titles = []
stopwords = []

#-----------------------------------------------------------
# Part 0 : Load stop words
#-----------------------------------------------------------

if LOAD_STOPWORDS:
    # https://www.ranks.nl/stopwords/french
    stopwords_ = open("data/stopwords.txt", encoding="utf8", mode="r").readlines()
    for s in stopwords_:
        stopwords.append(s.strip())

def pi(v):
    return f"{v:6d}"

def pp(v):
    return f"{round(v*100):6d} %"

# Compare train & test on domain
# ministat for building balanced corpus
def count(corpus):
    dom = {}
    nb = 0
    for t in corpus:
        if t.domain not in dom:
            dom[t.domain] = 1
        else:
            dom[t.domain] += 1
        nb += 1
    print("nb of dom:", len(dom))
    for k, v in dom.items():
        print(f"{k:12}", f"{v:6d}", pp(v / nb))

#-----------------------------------------------------------
# Part 0 : Convert the unreadable CSV to a readable CSV by pandas
#-----------------------------------------------------------

# "abc", "cde", "d,ef"
# The comma inside d,ef is a problem. We must change the separator

# Read the teacher CSV. Convert it to a list of string with ### sep and no "x"
def read_base_csv(filepath):
    f = open(filepath, mode='r', encoding='utf8')
    lines = f.readlines()
    f.close()
    first = True
    out = []
    for lin in lines:
        data = lin.split(',')
        output = ''
        for i in range(0, 4):
            d = data[i]
            output += d.strip().replace('"', '') + '###'
        output += ','.join(data[4:]).strip().replace('"', '') + "\n"
        #if not first:
        #    titles.append(MiniTitle(*output.split('###')))
        #else:
        #    first = False
        out.append(output)
    return out

# Write a list of lines
def write_to_csv(filename, lines, start=0, end=None, newsep=None, header=None):
    if end is None: end = len(lines)
    f = open(filename, mode='w', encoding='utf8')
    if header is not None:
        if type(header) in [bool]:
            pass
        else:
            if newsep is not None:
                f.write(header.replace("###", newsep))
            else:
                f.write(header)
    nb = 0
    for i in range(start, end):
        if newsep is not None:
            f.write(lines[i].replace("###", newsep))
        else:
            f.write(lines[i])
        nb += 1
    f.close()
    if header is not None:
        print('from', start, 'to', end, 'nb', nb, '+1 header')
    else:
        print('from', start, 'to', end, 'nb', nb, 'without header')

if CONVERT:
    lines = read_base_csv('data/litl-exam.csv')
    write_to_csv('data/sharpAll.csv', lines, header=True)

#-----------------------------------------------------------
# Part 0 : Make PICKLE corpus for ALL, TRAIN, TEST from CSV
#-----------------------------------------------------------

def read_csv(filename, count=None):
    # Load all title from CSV
    tt = []
    data = open(filename, mode='r', encoding='utf8').readlines()
    for line in data[1:]:
        tt.append(MiniTitle(*line.split('###')))
    if count is not None:
        assert(len(tt) == count)
    return tt

if MAKE_CORPUS_ALL:
    titles = read_csv('data_all.csv', 53426)
    
    # Send them to Talisman for processing
    from client_talismane import process_string
    for t in titles:
        t.words = process_string(t.title)

    # Or use NLTK
    # tokenizer = RegexpTokenizer(r"\w+", flags=re.UNICODE|re.IGNORECASE)
    # for t in tiles:
    #    exploded = tokenizer.tokenize(text)
    #    filtered = []
    #    for e in exploded:
    #        if e.lower() not in stopwords:
    #            filtered.append(e.lower())
    
    out = open('backup.bin', mode='wb')
    pickle.dump(titles, out)
    out.close()

if MAKE_TRAIN_TEST_FROM_PICKLE_ALL:
    titles = pickle.load(open('data/backup.bin', mode='rb'))
    tiers = int(len(titles)/3)
    print(len(titles))          # 53 426
    print(len(titles) - tiers)  # 35 618
    print(tiers)                # 17 808
    count(titles)               # 33% Ling 35% Info 32% Lettre
    tiers_info = int(18694/3)
    cpt_info = 0
    tiers_ling = int(17582/3)
    cpt_ling = 0
    tiers_lett = int(17150/3)
    cpt_lett = 0
    train_titles = []
    test_titles= []
    for t in titles:
        filtered = []
        for w in t.words:
            form = w.lemma if w.lemma != '_' else w.form.lower()
            if form not in filtered and w.pos != 'PONCT' and form not in stopwords:
                filtered.append(form)
        t.filtered = filtered
        if t.domain == 'Linguistique' and cpt_ling < tiers_ling:
            test_titles.append(t)
            cpt_ling += 1
        elif t.domain == 'Linguistique':
            train_titles.append(t)
            cpt_ling += 1
        elif t.domain == 'Lettres' and cpt_lett < tiers_lett:
            test_titles.append(t)
            cpt_lett += 1
        elif t.domain == 'Lettres':
            train_titles.append(t)
            cpt_lett += 1
        elif t.domain == 'Informatique' and cpt_info < tiers_info:
            test_titles.append(t)
            cpt_info += 1
        elif t.domain == 'Informatique':
            train_titles.append(t)
            cpt_info += 1
    # count
    count(train_titles)
    count(test_titles)
    # save
    out = open('data/train.bin', mode='wb')
    pickle.dump(train_titles, out)
    out.close()
    out = open('data/test.bin', mode='wb')
    pickle.dump(test_titles, out)
    out.close()

#-----------------------------------------------------------
# Part 0 : Load corpus from Pickle
#-----------------------------------------------------------

if LOAD_ALL:
    # warning: no filtered
    titles = pickle.load(open('backup.bin', mode='rb'))
    
if LOAD_TRAIN:
    print('Loading Train Corpus from pickle')
    train = pickle.load(open('data/train.bin', mode='rb'))

if LOAD_TEST:
    print('Loading Test Corpus from pickle')
    test = pickle.load(open('data/test.bin', mode='rb'))

if LOAD_ONE_FROM_PICKLE:
    titles = pickle.load(open(LOAD_WHAT, mode='rb'))
    print(len(titles), 'titles loaded from', LOAD_WHAT)

if COMPARE_TRAIN_TEST:
    count(train)
    count(test)

#-----------------------------------------------------------
# PART1 : Make a stat on a feat2 for feat1=val
#-----------------------------------------------------------

def stat(titles, feat1, val1, feat2):
    """Make dic of stat for a feat2 but only if feat1=val1 for a given title"""
    freq = {}
    for t in titles:
        if getattr(t, feat1) == val1:
            key = getattr(t, feat2)
            if key in freq:
                freq[key] += 1
            else:
                freq[key] = 1
    return freq

def pprint(title, dic, f='value'):
    print(title)
    print('-' * len(title))
    total = 0
    for k, v in dic.items():
        total += v
    if f == 'value' :
        sorted_keys = sorted(dic, key=dic.get, reverse=True)
    elif f == 'key' :
        sorted_keys = sorted(dic)
    else:
        Exception("How to sort?")
    for k in sorted_keys:
        v = dic[k]
        print(f"{k:15}", f"{v:6d}", f"{int(round((v/total)*100,0)):3d} %")
    print("Total           ", f"{total:6d}")
    print()
    return total

if STAT_DOMAIN_SUPPORT:
    # Domain for Support
    
    domain_for_support_ART = stat(titles, 'support', 'ART', 'domain')
    assert(pprint("Domain for support ART", domain_for_support_ART) == 17_273)

    domain_for_support_COMM = stat(titles, 'support', 'COMM', 'domain')
    assert(pprint("Domain for support COMM", domain_for_support_COMM) == 24_693)

    domain_for_support_COUV = stat(titles, 'support', 'COUV', 'domain')
    assert(pprint("Domain for support COUV", domain_for_support_COUV) == 11_460)

    # Support for Domain

    support_for_domain_LING = stat(titles, 'domain', 'Linguistique', 'support')
    assert(pprint("Support for domain Linguistique", support_for_domain_LING) == 17_582)

    support_for_domain_LETT = stat(titles, 'domain', 'Lettres', 'support')
    assert(pprint("Support for domain Lettres", support_for_domain_LETT) == 17_150)

    support_for_domain_INFO = stat(titles, 'domain', 'Informatique', 'support')
    assert(pprint("Support for domain Informatique", support_for_domain_INFO) == 18_694)

#-----------------------------------------------------------
# PART1 : Make crossed stat auteurs / support
#-----------------------------------------------------------

def crossed(feat1, feat2):
    """Look var1 compared to var2"""
    feat1vals = {}
    for t in titles:
        val1 = getattr(t, feat1)
        val2 = getattr(t, feat2)
        if val1 not in feat1vals:
            feat1vals[val1] = {}
        if val2 not in feat1vals[val1]:
            feat1vals[val1][val2] = 1
        else:
            feat1vals[val1][val2] += 1
    totaux = {}
    for key1 in feat1vals:
        totaux[key1] = 0
        for key2 in feat1vals[key1]:
            totaux[key1] += feat1vals[key1][key2]
    return feat1vals, totaux

if CROSS_SUPPORT_AUTHORS:
    c,t = crossed('support', 'authors')
    print('nb\tART', f'{t["ART"]:6d}','\t %\t\t\tCOMM', f'{t["COMM"]:6d}','\t %\t\t\tCOUV', f'{t["COUV"]:6d}','\t %\t')
    cumu_art = 0
    cumu_comm = 0
    cumu_couv = 0
    for k in range(1, 39):
        print(k, '.\t', end='')
        if k in c['ART']:
            print('A', "{:6d}".format(c['ART'][k]), '\t', "P {0:.3f}".format(c['ART'][k] / t['ART']), '\t', end='')
            cumu_art += c['ART'][k] / t['ART']
            print("C {0:.3f}\t".format(cumu_art), end='')
        else:
            print('\t\t\t\t\t', end='')
        if k in c['COMM']:
            print('A', "{:6d}".format(c['COMM'][k]), '\t', "P {0:.3f}".format(c['COMM'][k] / t['COMM']), '\t', end='')
            cumu_comm += c['COMM'][k] / t['COMM']
            print("C {0:.3f}\t".format(cumu_comm), end='')
        else:
            print('\t\t\t\t\t', end='')
        if k in c['COUV']:
            print('A', "{:6d}".format(c['COUV'][k]), '\t', "P {0:.3f}".format(c['COUV'][k] / t['COUV']), '\t', end='')
            cumu_couv += c['COUV'][k] / t['COUV']
            print("C {0:.3f}\t".format(cumu_couv), end='')
        print()

#-----------------------------------------------------------
# PART2 : Stats on length & words
#-----------------------------------------------------------

class DomainInfo:

    def __init__(self, code):
        self.code = code
        self.words = {}
        self.sum_char_length = 0
        self.sum_word_length = 0
        self.nb = 0

    def add_word(self, w):
        if w not in self.words:
            self.words[w] = 1
        else:
            self.words[w] += 1

    def add_title(self, t):
        self.sum_char_length += len(t.title)
        nb = 0
        for w in t.words:
            if w.pos != 'PONCT':
                nb += 1
        self.sum_word_length += nb #len(t.words)
        self.nb += 1

    # get word frequencies
    def get_frequencies(self):
        wf = {}
        for w in self.words:
            wf[w] = self.words[w] / self.nb
        self.mean_char_count = self.sum_char_length/self.nb
        self.mean_word_count = self.sum_word_length/self.nb
        self.freqs = wf

    # calculate precision, rappel, fmesure for each words! (not only the best!)
    def get_best(self, domains):
        best = []
        for w in self.words:
            nb_in = self.words[w]
            nb_out = 0
            for key, dom in domains.items():
                if key != self.code and w in dom.words:
                    nb_out += dom.words[w]
            precision = nb_in / (nb_out + nb_in)
            rappel = nb_in / self.nb
            fmesure = (2 * precision * rappel) / (precision + rappel)
            best.append((w, precision, rappel, fmesure))
        self.best = sorted(best, key=lambda x: x[3], reverse=True)
        #self.bestkey = {}
        #for b in self.best:
        #    self.bestkey[b[0]] = (b[1], b[2], b[3])

    def get_first_best(self, nb=None):
        i = 0
        ret = {}
        if nb is None: nb = len(self.best)
        for i in range(0, nb):
            ret[self.best[i][0]] = self.best[i][3] # {word:f-mesure}
        return ret


def count(titles):
    domains = {}
    for t in titles:
        if t.domain not in domains:
            dom = DomainInfo(t.domain)
            domains[t.domain] = dom
        else:
            dom = domains[t.domain]
        dom.add_title(t)
        for w in t.filtered:
            dom.add_word(w)
    print(len(titles))
    return domains
    # For ALL
    # Linguistique 	nb=	 017582 	mean char length=	 80.33 	mean word length=	 13.53
    # Lettres 	        nb=	 017150 	mean char length=	 75.83 	mean word length=	 14.33
    # Informatique 	nb=	 018694 	mean char length=	 79.14 	mean word length=	 12.33


def head(domains, nb):
    ling_sorted_keys = sorted(domains['Linguistique'].freqs, key=domains['Linguistique'].freqs.get, reverse=True)
    lett_sorted_keys = sorted(domains['Lettres'].freqs, key=domains['Lettres'].freqs.get, reverse=True)
    info_sorted_keys = sorted(domains['Informatique'].freqs, key=domains['Informatique'].freqs.get, reverse=True)
    print("       Linguistique          Lettres               Informatique")
    k = 0
    while k < nb:
        print(f"{k:6d}",
              f"{ling_sorted_keys[k]:>12}",
              pi(domains['Linguistique'].words[ling_sorted_keys[k]]),
              pp(domains['Linguistique'].freqs[ling_sorted_keys[k]]),
              f"{lett_sorted_keys[k]:>12}",
              pi(domains['Lettres'].words[ling_sorted_keys[k]]),
              pp(domains['Lettres'].freqs[lett_sorted_keys[k]]),
              f"{info_sorted_keys[k]:>12}",
              pi(domains['Informatique'].words[ling_sorted_keys[k]]),
              pp(domains['Informatique'].freqs[info_sorted_keys[k]])
              )
        k += 1
    print()

if LENGTH_FREQ_STATS:
    domains = count(train)
    for key, dom in domains.items():
        dom.get_frequencies()
        print(key, '\tnb=\t', f"{dom.nb:06d}",
                  '\tmean char length=\t', f"{dom.mean_char_count:.2f}",
                  '\tmean word length=\t', f"{dom.mean_word_count:.2f}")
    print()
    head(domains, 10)

# Accès au nombre d'occurrence d'un mots :
# domains['Informatique'].words['français']

#-----------------------------------------------------------
# PART2 : Doublons ?
#-----------------------------------------------------------

# Si le mot "système" a une fréquence de 10% combien de titres cela couvre ?
# Pour cela, il faut calculer s'il y a une possibilité qu'un titre est
# deux fois système dedans. Si non... Il y a 10% de titres qui ont système ;-)

if DOUBLONS_TEST:
    doublons = {}
    for t in train:
        for i1 in range(0, len(t.filtered)):
            for i2 in range(0, len(t.filtered)):
                if i1 != i2:
                    if t.filtered[i1] == t.filtered[i2]:
                        if t.filtered[i1] not in doublons:
                            doublons[t.filtered[i1]] = 1
                        else:
                            doublons[t.filtered[i1]] += 1
                        if t.filtered[i1] == 'munichois':
                            print(t.words)
                            print(t.filtered)
    print("Doublons = ", len(doublons))

#-----------------------------------------------------------
# PART2 : Best indicators based on F-Mesure
#-----------------------------------------------------------

if SHOW_BEST or COVER_CALC or EVALUATE_MY_MODEL_POS or EVALUATE_MY_MODEL_SILHOUETTE:
    print('Getting best from TRAIN corpus')
    for key, dom in domains.items():
        dom.get_best(domains)

if SHOW_BEST:
    nbmax = 10
    for key, dom in domains.items():
        print(f"{key:12}", '=========================')
        nb = 0
        for w in dom.best:
            print(f'{nb:02d}.', f"{w[0]:12}", pp(w[1]), pp(w[2]), pp(w[3]))
            nb += 1
            if nb >= nbmax: break
        print()

#-----------------------------------------------------------
# PART2 : Couverture of the Best indicators
#-----------------------------------------------------------

def calc_cover(nbmax):
    for key, dom in domains.items():
        only_w = []
        for w in dom.best[:nbmax]:
            only_w.append(w[0])
        nb = 0
        for t in train:
            if t.domain != key: continue
            found = False
            for w in only_w:
                if w in t.filtered:
                    found = True
                    break
            if found:
                nb += 1
        print(f"{key:12}", f"covered for {nbmax:4} =", pp(nb / dom.nb))

if COVER_CALC:
    # How to reach 90?
    calc_cover(50)
    calc_cover(150)
    calc_cover(200)

#-----------------------------------------------------------
# PART2 : Feature extraction : POS
#-----------------------------------------------------------

if FEATURE_EXTRACTION_POS:
    print('Feature extraction : POS')
    dom = {
        'Informatique' : {},
        'Lettres' : {},
        'Linguistique' : {}
    }
    total = {
        'Informatique' : 0,
        'Lettres' : 0,
        'Linguistique' : 0
    }
    for t in train:
        for w in t.words:
            if w.pos in dom[t.domain]:
                dom[t.domain][w.pos] += 1
            else:
                dom[t.domain][w.pos] = 1
            total[t.domain] += 1
    allkeys = list(dom['Informatique'].keys())
    allkeys.extend(list(dom['Lettres'].keys()))
    allkeys.extend(list(dom['Linguistique'].keys()))
    allkeys = set(allkeys)
    print('       ', 'Informatique', 'Lettres', 'Linguistique')
    for k in allkeys:
        print(f"{k:6}",
              f"{dom['Informatique'][k]:10d}", f"{pp(dom['Informatique'][k]/total['Informatique'])}",
              f"{dom['Lettres'][k]:10d}", f"{pp(dom['Lettres'][k]/total['Lettres'])}",
              f"{dom['Linguistique'][k]:10d}", f"{pp(dom['Linguistique'][k]/total['Linguistique'])}")
    
    # Calc moyenne NPP et PONCT par titre
    dom = {
        'Informatique' : { 'PONCT' : 0, 'NPP' : 0},
        'Lettres' : { 'PONCT' : 0, 'NPP' : 0},
        'Linguistique' : { 'PONCT' : 0, 'NPP' : 0}
    }
    for t in train:
        nb_npp = 0
        nb_ponct = 0
        for w in t.words:
            if w.pos == 'PONCT': nb_ponct += 1
            if w.pos == 'NPP': nb_npp += 1
        dom[t.domain]['PONCT'] += nb_ponct / len(t.words)
        dom[t.domain]['NPP'] += nb_npp / len(t.words)
    # average of average
    for key in dom:
        total_npp = dom[key]['NPP'] / domains[key].nb
        total_pont = dom[key]['PONCT'] / domains[key].nb
        print('Moyenne de NPP par titre pour domaine', key, '=', total_npp)
        print('Moyenne de PONCT par titre pour domaine', key, '=', total_pont)
        print()
            
#-----------------------------------------------------------
# PART3 : Common evaluating framework
#-----------------------------------------------------------

# Categorize all titles
def categorize_all(titles, categorize_function):
    start_time = datetime.datetime.now()
    threshold = 1000
    step = 1000
    cpt = 0
    total = len(titles)
    for t in titles:
        t.guess = categorize_function(t)
        # Count progress
        cpt += 1
        if cpt == step:
            print(f"{threshold:>08} / {total} titles done.'")
            cpt = 0
            threshold += step
    print('Duration : ' + str(datetime.datetime.now() - start_time))

if EVALUATE_MY_MODEL_POS or EVALUATE_MY_MODEL_SILHOUETTE:
    if EVALUATE_TARGET == 'TEST':
        del train
        titles = test
    elif EVALUATE_TARGET == 'TRAIN':
        del test
        titles = train

#-----------------------------------------------------------
# PART3 : My evaluation model on POS
#-----------------------------------------------------------

def evaluate_pos(t, pos):
    nb_pos = 0
    for w in t.words:
        if w.pos == pos: nb_pos += 1
    average = nb_pos / len(t.words)
    return average

def categorize_npp(t):
    ave = evaluate_pos(t, 'NPP')
    if ave >= 0.15170332213057197:
        return 'Lettres'
    elif ave >= 0.06985772976260159:
        return 'Informatique'
    elif ave >= 0.05335999774579773:
        return 'Linguistique'
    else:
        return 'Unknown'

def categorize_ponct(t):
    ave = evaluate_pos(t, 'PONCT')
    if ave >= 0.11768722659526903:
        return 'Lettres'
    elif ave >= 0.0967350821984055:
        return 'Linguistique'
    elif ave >= 0.05180327475794362:
        return 'Informatique'
    else:
        return 'Unknown'


if EVALUATE_MY_MODEL_POS:
    pos_list = ['NPP', 'PONCT']
    fun_dict = {
            'NPP' : categorize_npp,
            'PONCT' : categorize_ponct
        }
    for pos in pos_list:
        print('Evaluating on POS =', pos,':')
        categorize_all(titles, fun_dict[pos])
        estimated = {
            'Informatique' : {
                'Informatique' : 0,
                'Lettres' : 0,
                'Linguistique' : 0
            },
            'Lettres' : {
                'Informatique' : 0,
                'Lettres' : 0,
                'Linguistique' : 0
            },
            'Linguistique' : {
                'Informatique' : 0,
                'Lettres' : 0,
                'Linguistique' : 0
            },
            'Unknown' : {
                'Informatique' : 0,
                'Lettres' : 0,
                'Linguistique' : 0
            }
        }
        for t in titles:
            estimated[t.guess][t.domain] += 1
        
        good = estimated['Linguistique']['Linguistique'] + \
               estimated['Lettres']['Lettres'] + \
               estimated['Informatique']['Informatique']
        countall = len(titles)
        print("Accuracy based on pos ", pos, "=", pp(good/countall))
        for key in estimated:
            if key == 'Unknown': continue
            good = estimated[key][key]
            al = estimated[key]['Informatique'] + estimated[key]['Lettres'] + estimated[key]['Linguistique']
            precision = good/al
            print("Precision for", key, "=", pp(precision))
            rappel = good/domains[key].nb
            print("Rappel for", key, "=", pp(rappel))
            #print("F-measure for", key, "=", pp((2 * precision * rappel)/(precision+rappel)))
            print("F-measure for", key, "=", (2 * precision * rappel)/(precision+rappel))
        print(estimated)

#-----------------------------------------------------------
# PART 3 : My evaluation model on Silhouette
#-----------------------------------------------------------

# Evaluate for a given domain the proximity of the title limited to nb best words
def evaluate(t, domain):
    factor = 0
    for b in first_best[domain]:
        if b in t.filtered:
             factor += first_best[domain][b]
    return factor

# Categorize one title
def categorize_silhouette(t):
    if len(t.filtered) == 0:
        return 'No silhouette'
    info = evaluate(t, 'Informatique')
    lett = evaluate(t, 'Lettres')
    ling = evaluate(t, 'Linguistique')
    # COMBINE SILHOUETTE AND POS
    if COMBINED_SILHOUETTE_AND_POS:
        extra_npp = categorize_npp(t)
        extra_ponct = categorize_ponct(t)
        if extra_npp == 'Informatique':
            info += 0.22342113614725484
        elif extra_npp == 'Lettres':
            lett += 0.5107107107107107
        elif extra_npp == 'Linguistique':
            ling += 0.07739679160647761
        if extra_ponct == 'Informatique':
            info += 0.2585027168444355
        elif extra_ponct == 'Lettres':
            lett += 0.438816291705959
        elif extra_ponct == 'Linguistique':
            ling += 0.15549089924893433
    # END COMBINE
    if info > lett and info > ling: return 'Informatique'
    elif lett > info and lett > ling: return 'Lettres'
    elif ling > info and ling> lett: return 'Linguistique'
    elif ling == info or ling == lett or info == lett:
        if ling == 0:
            return 'Zero Equality'
        else:
            print(ling, info, lett, t.filtered)
            return 'Non Zero Equality'
    else:
        print(ling, info, lett, t.filtered)
        raise Exception("Impossible")

if EVALUATE_MY_MODEL_SILHOUETTE:
    # Title with nothing
    cpt = 0
    for t in titles:
        if len(t.filtered) == 0:
            cpt += 1
    print("Title without silhouette in", EVALUATE_TARGET, "=", cpt)

    # Getting the best
    first_best = {
        'Informatique' : domains['Informatique'].get_first_best(EVALUATE_NB_FACTOR),
        'Lettres' : domains['Lettres'].get_first_best(EVALUATE_NB_FACTOR),
        'Linguistique' : domains['Linguistique'].get_first_best(EVALUATE_NB_FACTOR)
    }

    # Go & Count https://fr.wikipedia.org/wiki/Matrice_de_confusion
    nbfactor = EVALUATE_NB_FACTOR if EVALUATE_NB_FACTOR is not None else 'ALL'
    print('Evaluating on', nbfactor, 'factors.')
    categorize_all(titles, categorize_silhouette)
    estimated = {
        'Informatique' : {
            'Informatique' : 0,
            'Lettres' : 0,
            'Linguistique' : 0
        },
        'Lettres' : {
            'Informatique' : 0,
            'Lettres' : 0,
            'Linguistique' : 0
        },
        'Linguistique' : {
            'Informatique' : 0,
            'Lettres' : 0,
            'Linguistique' : 0
        },
        'No silhouette' : {
            'Informatique' : 0,
            'Lettres' : 0,
            'Linguistique' : 0
        },
        'Zero Equality' : {
            'Informatique' : 0,
            'Lettres' : 0,
            'Linguistique' : 0 
        },
        'Non Zero Equality' : {
            'Informatique' : 0,
            'Lettres' : 0,
            'Linguistique' : 0
        }
    }

    for t in titles:
        estimated[t.guess][t.domain] += 1

    good = estimated['Linguistique']['Linguistique'] + \
           estimated['Lettres']['Lettres'] + \
           estimated['Informatique']['Informatique']
    countall = len(titles)
    print(f"{'Accuracy =':15}", pp(good/countall))
    no_sil = estimated['No silhouette']['Linguistique'] + estimated['No silhouette']['Lettres'] + estimated['No silhouette']['Informatique']
    print(f"{'Title without Silhouette =':15}", cpt, no_sil)
    ze = estimated['Zero Equality']['Linguistique'] +  estimated['Zero Equality']['Lettres'] +  estimated['Zero Equality']['Informatique']
    print(f"{'Title with Zero Equality =':15}", ze)
    nze = estimated['Non Zero Equality']['Linguistique'] +  estimated['Non Zero Equality']['Lettres'] +  estimated['Non Zero Equality']['Informatique']
    print(f"{'Title with Non Zero Equality =':15}", nze)
    print(estimated)
    print('Nb factors :')
    print('Informatique =', len(first_best['Informatique']))
    print('Lettres =', len(first_best['Lettres']))
    print('Linguistique =', len(first_best['Linguistique']))



return

#-----------------------------------------------------------
# PART 3 : The Decision Tree
#-----------------------------------------------------------

# Make panda

train_silhouette =  {
    'silhouette' : [],
    'domain' : [],
}

for t in train:
    words = []
    for w in t.filtered:
        if w in first_best[t.domain]:
            words.append(w)
    train_silhouette['silhouette'].append(' '.join(words))
    train_silhouette['domain'].append(t.domain)

train_silhouette_frame = pd.DataFrame(train_silhouette)
try:
    train_silhouette_frame_onehot = pd.get_dummies(train_silhouette_frame, prefix='sil', dtype=int, columns=['silhouette'])
except MemoryError:
    print('Not enough memory.')

exit()

#-----------------------------------------------------------
#-----------------------------------------------------------
#-----------------------------------------------------------

titles = []
titles_string = []

# Stats
domains = {}
supports = {}
years = {}
nauthors = {}
for t in titles:
    if t.domain in domains:
        domains[t.domain] += 1
    else:
        domains[t.domain] = 1
    if t.support in supports:
        supports[t.support] += 1
    else:
        supports[t.support] = 1
    if t.year in years:
        years[t.year] += 1
    else:
        years[t.year] = 1
    if t.authors in nauthors:
        nauthors[t.authors] += 1
    else:
        nauthors[t.authors] = 1

#-----------------------------------------------------------

PRINT=True

if PRINT:
    pprint("Domains by value", domains, domains.get)
    pprint("Supports by value", supports, supports.get)
    pprint("Years by value", years, years.get)
    pprint("Years by key", years)
    pprint("Nb authors by value", nauthors, nauthors.get)
    pprint("Nb authors by key", nauthors)

JSON=False

if JSON:
    import json
    f = open('data.json', 'w')
    big = []
    for t in titles:
        big.append({
            "sparse" : False,
            "weight" : 1.0,
            "values" : t.to_list()
        })

    big = {
        "header" :
        {
            "relation" : "TEST",
            "attributes" :
            [
                {
                    "name" : "domain",
                    "type" : "nominal",
                    "class" : False,
                    "weight" : 1.0,
                    "labels" : [
                        "Linguistique",
			"Informatique",
                        "Lettres"
		    ]
		},
                {
                    "name" : "support",
                    "type" : "nominal",
                    "class" : False,
                    "weight" : 1.0,
                    "labels" : [
                        "COMM",
			"ART",
                        "COUV"
		    ]
		},
                {
                    "name" : "year",
                    "type" : "numeric",
                    "class" : False,
                    "weight" : 1.0
		},
                {
                    "name" : "authors",
                    "type" : "numeric",
                    "class" : False,
                    "weight" : 1.0
		},
                {
                    "name" : "title",
                    "type" : "string",
                    "class" : False,
                    "weight" : 1.0
		},
            ],
        },
        "data" : big
    }
    json.dump(big, f, indent=" ")
    f.close()

#-----------------------------------------------------------

SPLIT=False

if SPLIT:
    # SPLIT
    header = titles_string[0]
    titles_string = titles_string[1:]
    tier = int(len(titles_string)/3)
    print(0, tier)
    # 1 tier
    write("testing.csv", titles_string, start=0, end=tier, header=header)
    # 2 tiers
    write("learning.csv", titles_string, start=tier, header=header)

#-----------------------------------------------------------

MERGE=False

if MERGE:
    print("[ACTION] Merging")
    f = open('data_learning.csv', mode='r', encoding='utf8')
    lines = f.readlines()
    f.close()
    f = open('data_testing.csv', mode='r', encoding='utf8')
    lines.extend(f.readlines()[1:])
    f.close()
    f = open('data_all.csv', mode='w', encoding='utf8')
    for lin in lines:
        f.write(lin)
    f.close()

#-----------------------------------------------------------

from copy import copy
from sklearn.preprocessing import LabelEncoder

def example():
    mini = {
        'name' : ['Stacy', 'Morgan', 'Fabien', 'Damien', 'Sandrine', 'Gloria', 'Camille'],
        'age'  : [    20 ,      22 ,      32 ,      34 ,        25 ,      18 ,       28 ],
        'sexe' : [   'F' ,     'F' ,     'M' ,     'M' ,       'F' ,     'F' ,      '?' ],
    }
    d = pd.DataFrame(mini)
    
    # ENCODE TOUT EN ONE HOT
    #from sklearn.preprocessing import OneHotEncoder
    #ohe = OneHotEncoder(dtype=int, sparse=False)
    #x = ohe.fit_transform(d) # return <class 'numpy.ndarray'>
    
    d2 = copy(d)
    d2 = d2.drop('name', axis=1)
    le = LabelEncoder()
    d2['sexe'] = le.fit_transform(d['sexe'])
    dt = tree.DecisionTreeClassifier()
    # Une seule feature, obligé de reshape !
    dt.fit(d2['age'].values.reshape(-1, 1), d2['sexe'])
    f = open("dt.dot", "w")
    features = list(d2.columns[:1])
    tree.export_graphviz(dt, out_file=f, feature_names=features, class_names=le.classes_)
    f.close()

mini = {
    'Titre'   : [
        "J'aime les nouilles.",
        "Tu adores les saucisses ?",
        "Bonjour le monde",
        "Voici la fin"
    ],
    'domain'  : [
        'A',
        'B',
        'C',
        'C'
    ]
}
d = pd.DataFrame(mini)

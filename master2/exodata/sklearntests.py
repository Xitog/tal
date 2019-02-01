#-----------------------------------------------------------
# Import
#-----------------------------------------------------------

# External Library
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import tree
import numpy as np

# Project Library
from preprocess import read_base_csv, write_to_csv

#-----------------------------------------------------------
# Decision Tree
#-----------------------------------------------------------

def make_panda(filepath):
    print("Information on the dataframe\n---")
    data = pd.read_csv(filepath, sep="###", engine='python', encoding='utf8')
    print(data.dtypes)
    print(data.describe())
    data.head(5)
    print(data.columns)
    return data

CONVERT_CSV = False
if CONVERT_CSV:
    lines = read_base_csv("data/litl-exam-3000.csv")
    write_to_csv("data/sharp3000.csv", lines)
    print()

data = make_panda("data/sharp3000.csv")

def make_train_test(data):
    tiers = int(len(data)/3)
    train, test = train_test_split(data,
                               train_size = len(data) - tiers, #35_618
                               test_size = tiers,
                               random_state=1,
                               stratify=data["Domaine"])
    print("\nCompare the frequence of domains in both set\n---")
    freqTrain = pd.crosstab(index=train["Domaine"], columns="count")
    print(freqTrain/freqTrain.sum())
    freqTest = pd.crosstab(index=test["Domaine"], columns="count")
    print(freqTest/freqTest.sum())
    return train, test

train, test = make_train_test(data)

def make_model(data, filename, debug=False):
    #alldata = pd.concat([train , test])
    #train['label'] = 'train'
    #test['label'] = 'test'
    #features_df = pd.get_dummies(alldata, columns=[], dummy_na=True) # il faut exploser avant Titre en mots !
    
    vec = TfidfVectorizer()
    X = vec.fit_transform(data["Titre"])
    if debug:
        ohe = pd.DataFrame(X.toarray(), columns=vec.get_feature_names())
        print(ohe)
    dt = tree.DecisionTreeClassifier(min_samples_split=20, random_state=99)
    dt.fit(X, data["Domaine"]) # feature, target
    f = open(filename, "w")
    tree.export_graphviz(dt, out_file=f, feature_names=vec.get_feature_names(),
                         class_names=data["Domaine"].unique(),
                         filled=True, rounded=True,  
                         special_characters=True)
    f.close()
    if debug:
        return vec, dt, ohe, X
    else:
        return ohe


def predict(vec, model, data):
    Xtest = vec.transform(data["Titre"])
    # 8709 (train) vs 6646 (test)
    res = model.predict(Xtest)
    acc = model.score(Xtest, data["Domaine"])
    return res, acc


def get_code(tree, feature_names, target_names,
             spacer_base="    ", max_depth = None):
    left      = tree.tree_.children_left
    right     = tree.tree_.children_right
    threshold = tree.tree_.threshold
    features  = [feature_names[i] for i in tree.tree_.feature]
    value = tree.tree_.value

    def recurse(left, right, threshold, features, node, depth, max_depth=None):
        spacer = spacer_base * depth
        if (threshold[node] != -2):
            print(spacer + "if ( " + features[node] + " <= " + \
                  str(threshold[node]) + " ) {")
            if left[node] != -1:
                if max_depth is None or depth+1 < max_depth:
                    recurse(left, right, threshold, features,
                            left[node], depth+1, max_depth)
            print(spacer + "}\n" + spacer +"else {")
            if right[node] != -1:
                if max_depth is None or depth+1 < max_depth:
                    recurse(left, right, threshold, features,
                        right[node], depth+1, max_depth)
            print(spacer + "}")
        else:
            target = value[node]
            for i, v in zip(np.nonzero(target)[1],
                            target[np.nonzero(target)]):
                target_name = target_names[i]
                target_count = int(v)
                print(spacer + "return " + str(target_name) + \
                      " ( " + str(target_count) + " examples )")

    recurse(left, right, threshold, features, 0, 0, max_depth)

# [3000 rows x 8709 columns]
# only_titles = pd.DataFrame(train["Titre"])
vec, dt, ohe, trainTransformed = make_model(data, "eval_based_on_titles_sklearn3000.dot", True)
print(dt.tree_.node_count) # 1659
print(dt.tree_.max_depth)  #   96
get_code(dt, ohe.columns, data["Domaine"].unique(), "  ", 20)
res, acc = predict(vec, dt, test)
print(acc)



